from __future__ import annotations

from pathlib import Path

from PIL import Image

from dicom_service.src.dicom_derivation import build_secondary_capture_from_source, save_secondary_capture
from dicom_service.src.dicom_io import DicomReadError, dicom_to_pil_and_array, read_dicom_from_bytes, save_bytes
from dicom_service.src.gradcam import (
    GradCAM,
    overlay_cam_on_rgb,
    resize_cam_to_shape,
    transparent_heatmap_rgba,
    transparent_heatmap_contour_rgba,
)
from dicom_service.src.image_io import StandardImageReadError, image_to_pil_and_array, read_standard_image_from_bytes
from dicom_service.src.image_qc import evaluate_image_qc
from dicom_service.src.model import InferenceModel
from dicom_service.src.preprocess import pil_to_tensor, resize_rgb_for_overlay
from dicom_service.src.qc import evaluate_qc
from dicom_service.src.schemas import ArtifactRefs, DicomMeta, InferResponse, ModelInfo, OutputPayload, PredictionBlock, QCBlock
from shared.config import settings
from shared.reporting import new_run_dir, save_report


class InferencePipeline:
    def __init__(self) -> None:
        self.runtime: InferenceModel | None = None

    def _get_runtime(self) -> InferenceModel:
        if self.runtime is None:
            self.runtime = InferenceModel()
        return self.runtime

    def _model_info(self) -> ModelInfo:
        return ModelInfo(
            model_name=settings.model_name,
            model_version=settings.model_version,
            input_size=[settings.image_size, settings.image_size],
            calibrated=True,
        )

    @staticmethod
    def _report_url(request_id: str) -> str:
        return f'/outputs/{request_id}/report.json'

    @staticmethod
    def _derived_dicom_url(request_id: str) -> str:
        return f'/outputs/{request_id}/derived_result.dcm'

    def _build_output_urls(self, request_id: str, saved: bool, include_gradcam: bool) -> OutputPayload:
        if not saved:
            return OutputPayload()
        payload = OutputPayload(
            image_analyzed_url=f'/outputs/{request_id}/image_analyzed.png',
            original_image_url=f'/outputs/{request_id}/original_image.png',
        )
        if include_gradcam:
            payload.heatmap_url = f'/outputs/{request_id}/heatmap.png'
            payload.overlay_url = f'/outputs/{request_id}/overlay.png'
            payload.transparent_heatmap_url = f'/outputs/{request_id}/transparent_heatmap.png'
            payload.transparent_contour_url = f'/outputs/{request_id}/transparent_contour.png'
        return payload
    
    def _build_artifacts(self, request_id: str, include_derived_dicom: bool) -> ArtifactRefs:
        return ArtifactRefs(
            run_id=request_id,
            report_url=self._report_url(request_id) if settings.save_report_json else None,
            derived_dicom_url=self._derived_dicom_url(request_id) if include_derived_dicom else None,
        )

    def _build_reject_response(self, request_id: str, qc_block: QCBlock, message: str, run_dir, include_derived_dicom: bool) -> InferResponse:
        prediction = PredictionBlock(
            label=None,
            probability=None,
            threshold=settings.threshold_default,
            decision_source=None,
            target_class=settings.target_class,
            confidence=None,
            calibration_temperature=settings.calibration_temperature_default,
        )
        response = InferResponse(
            request_id=request_id,
            status='REJECT',
            task=settings.task_name,
            model_info=self._model_info(),
            qc=qc_block,
            prediction=prediction,
            outputs=OutputPayload(),
            artifacts=self._build_artifacts(request_id, include_derived_dicom=include_derived_dicom),
            message=message,
        )
        if settings.save_report_json:
            save_report(run_dir, response.model_dump())
        return response

    def _run_prediction_and_outputs(self, *, source_kind: str, request_id: str, run_dir: Path, pil_img: Image.Image, arr, qc_block: QCBlock, filename: str | None, source_dcm=None) -> InferResponse:
        runtime = self._get_runtime()
        x = pil_to_tensor(pil_img)
        prob, confidence = runtime.predict_proba(x)
        label = settings.label_positive if prob >= runtime.threshold else settings.label_negative

        rgb = resize_rgb_for_overlay(pil_img)
        image_analyzed = Image.fromarray(rgb)
        original_rgb = pil_img.convert('RGB')
        original_width, original_height = original_rgb.size

        include_gradcam = label == settings.label_positive
        heatmap_only = None
        overlay_img = None
        transparent_heatmap = None
        transparent_contour = None
        if include_gradcam:
            gradcam = GradCAM(runtime.model, runtime.model.layer4[-1].conv2)
            cam = gradcam(x.to(runtime.device))
            gradcam.close()
            heatmap_only = Image.fromarray((cam * 255).astype('uint8'))
            overlay_img = Image.fromarray(overlay_cam_on_rgb(rgb, cam, alpha=0.35))
            cam_original = resize_cam_to_shape(cam, original_width, original_height)
            transparent_heatmap = Image.fromarray(transparent_heatmap_rgba(cam_original, alpha_scale=0.45), mode='RGBA')
            transparent_contour = Image.fromarray(transparent_heatmap_contour_rgba(cam_original, threshold=0.75),mode='RGBA',)
        saved_outputs = False
        if settings.save_image_outputs:
            image_analyzed.save(run_dir / 'image_analyzed.png')
            original_rgb.save(run_dir / 'original_image.png')
            if include_gradcam and heatmap_only and overlay_img and transparent_heatmap and transparent_contour:
                heatmap_only.save(run_dir / 'heatmap.png')
                overlay_img.save(run_dir / 'overlay.png')
                transparent_heatmap.save(run_dir / 'transparent_heatmap.png')
                transparent_contour.save(run_dir / 'transparent_contour.png')
            saved_outputs = True

        contour_overlay_img = None
        if include_gradcam and transparent_contour is not None:
            contour_overlay_img = Image.alpha_composite(
                original_rgb.convert('RGBA'),
                transparent_contour
            ).convert('RGB')

        include_derived_dicom = source_kind == 'dicom'
        if include_derived_dicom and source_dcm is not None:
            derived_source_image = contour_overlay_img if include_gradcam and overlay_img is not None else original_rgb
            derived_dataset = build_secondary_capture_from_source(
                source_dcm=source_dcm,
                image=derived_source_image,
                predicted_label=label,
                probability=prob,
                run_id=request_id,
            )
            save_secondary_capture(run_dir / 'derived_result.dcm', derived_dataset)

        response = InferResponse(
            request_id=request_id,
            status='ACCEPT_WITH_WARNINGS' if qc_block.summary.endswith('with_warnings') or qc_block.summary == 'accepted_with_warnings' else ('ACCEPT_WITH_WARNINGS' if qc_block.warnings else 'ACCEPT'),
            task=settings.task_name,
            model_info=self._model_info(),
            qc=qc_block,
            prediction=PredictionBlock(
                label=label,
                probability=prob,
                threshold=runtime.threshold,
                decision_source='calibrated_probability',
                target_class=settings.target_class,
                confidence=confidence,
                calibration_temperature=runtime.calibration_temperature,
            ),
            outputs=self._build_output_urls(request_id, saved_outputs, include_gradcam),
            artifacts=self._build_artifacts(request_id, include_derived_dicom=include_derived_dicom),
            message='Inference completed with warnings.' if qc_block.warnings else 'Inference completed successfully.',
        )
        if settings.save_report_json:
            save_report(run_dir, response.model_dump())
        return response

    def _dicom_meta_from_dataset(self, dcm) -> DicomMeta:
        return DicomMeta(
            modality=getattr(dcm, 'Modality', None),
            rows=getattr(dcm, 'Rows', None),
            columns=getattr(dcm, 'Columns', None),
            photometric_interpretation=getattr(dcm, 'PhotometricInterpretation', None),
            study_instance_uid=getattr(dcm, 'StudyInstanceUID', None),
            series_instance_uid=getattr(dcm, 'SeriesInstanceUID', None),
            sop_instance_uid=getattr(dcm, 'SOPInstanceUID', None),
            source_type='dicom',
        )

    def _dicom_meta_from_image(self, pil_img: Image.Image) -> DicomMeta:
        width, height = pil_img.size
        return DicomMeta(
            modality=None,
            rows=height,
            columns=width,
            photometric_interpretation='RGB',
            study_instance_uid=None,
            series_instance_uid=None,
            sop_instance_uid=None,
            source_type='image',
        )

    def run(self, payload: bytes, filename: str | None = None) -> InferResponse:
        request_id, run_dir = new_run_dir()

        is_standard_image = False
        if filename:
            suffix = Path(filename).suffix.lower()
            is_standard_image = suffix in {'.png', '.jpg', '.jpeg'}

        if is_standard_image:
            try:
                pil_img = read_standard_image_from_bytes(payload)
            except StandardImageReadError as exc:
                reason = str(exc) if str(exc) else 'invalid_standard_image'
                qc_block = QCBlock(reject_reasons=[reason], warnings=[], summary=reason, dicom_meta=DicomMeta(source_type='image'))
                return self._build_reject_response(request_id, qc_block, 'Inference rejected: invalid image payload.', run_dir, include_derived_dicom=False)

            _, arr = image_to_pil_and_array(pil_img)
            qc_result = evaluate_image_qc(pil_img, arr)
            qc_block = QCBlock(
                reject_reasons=qc_result.reject_reasons,
                warnings=qc_result.warnings,
                summary=qc_result.summary,
                dicom_meta=self._dicom_meta_from_image(pil_img),
            )
            if qc_result.status == 'REJECT':
                return self._build_reject_response(request_id, qc_block, 'Inference rejected by image QC.', run_dir, include_derived_dicom=False)
            return self._run_prediction_and_outputs(
                source_kind='image',
                request_id=request_id,
                run_dir=run_dir,
                pil_img=pil_img,
                arr=arr,
                qc_block=qc_block,
                filename=filename,
                source_dcm=None,
            )

        if settings.save_uploaded_dicom:
            uploaded_dicom_path = run_dir / (filename or 'input.dcm')
            save_bytes(uploaded_dicom_path, payload)

        try:
            dcm = read_dicom_from_bytes(payload)
        except DicomReadError as exc:
            reason = str(exc) if str(exc) else 'invalid_dicom'
            qc_block = QCBlock(reject_reasons=[reason], warnings=[], summary=reason, dicom_meta=DicomMeta(source_type='dicom'))
            return self._build_reject_response(request_id, qc_block, 'Inference rejected: invalid DICOM payload.', run_dir, include_derived_dicom=False)

        pil_img, arr = dicom_to_pil_and_array(dcm)
        qc_result = evaluate_qc(dcm, arr)
        qc_block = QCBlock(
            reject_reasons=qc_result.reject_reasons,
            warnings=qc_result.warnings,
            summary=qc_result.summary,
            dicom_meta=self._dicom_meta_from_dataset(dcm),
        )
        if qc_result.status == 'REJECT':
            return self._build_reject_response(request_id, qc_block, 'Inference rejected by QC.', run_dir, include_derived_dicom=False)

        return self._run_prediction_and_outputs(
            source_kind='dicom',
            request_id=request_id,
            run_dir=run_dir,
            pil_img=pil_img,
            arr=arr,
            qc_block=qc_block,
            filename=filename,
            source_dcm=dcm,
        )
