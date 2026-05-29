from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from dicom_service.src.orthanc_client import OrthancClient, OrthancClientError
from dicom_service.src.schemas import (
    InferResponse,
    OrthancBatchInferResponse,
    OrthancBatchItem,
    OrthancInferRequest,
    OrthancStoreDerivedResponse,
)
from shared.config import settings
from shared.logging_utils import get_logger

app = FastAPI(title=settings.service_name, version=settings.service_version)
logger = get_logger()
settings.outputs_dir.mkdir(parents=True, exist_ok=True)
app.mount('/outputs', StaticFiles(directory=str(settings.outputs_dir)), name='outputs')


@lru_cache(maxsize=1)
def get_pipeline():
    from dicom_service.src.pipeline import InferencePipeline
    return InferencePipeline()


@lru_cache(maxsize=1)
def get_orthanc_client() -> OrthancClient:
    return OrthancClient()


@app.get('/health')
def health() -> dict:
    model_ready = (
        settings.model_path.exists()
        and settings.calibration_temperature_path.exists()
        and settings.threshold_path.exists()
    )
    return {
        'service': settings.service_name,
        'version': settings.service_version,
        'model_ready': model_ready,
        'model_name': settings.model_name,
        'model_version': settings.model_version,
        'calibrated': True,
        'allowed_modalities': list(settings.allowed_modalities),
        'task': settings.task_name,
        'input_size': [settings.image_size, settings.image_size],
        'max_saved_runs': settings.max_saved_runs,
        'outputs_base_url': '/outputs',
        'orthanc_enabled': settings.orthanc_enabled,
        'supported_upload_types': ['dcm', 'png', 'jpg', 'jpeg'],
    }


@app.post('/infer', response_model=InferResponse)
async def infer(file: UploadFile = File(...)) -> InferResponse:
    try:
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail='Uploaded file is empty.')
        response = get_pipeline().run(payload=payload, filename=file.filename)
        logger.info('request_id=%s status=%s filename=%s', response.request_id, response.status, file.filename)
        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception('Inference failed')
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get('/orthanc/studies')
def list_orthanc_studies(limit: int | None = None) -> list[dict]:
    if not settings.orthanc_enabled:
        raise HTTPException(status_code=400, detail='Orthanc integration is disabled.')
    try:
        return [item.model_dump() for item in get_orthanc_client().list_studies(limit=limit)]
    except Exception as exc:
        logger.exception('Orthanc study listing failed')
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post('/orthanc/infer', response_model=InferResponse)
def orthanc_infer(request: OrthancInferRequest) -> InferResponse:
    if not settings.orthanc_enabled:
        raise HTTPException(status_code=400, detail='Orthanc integration is disabled.')

    client = get_orthanc_client()

    try:
        if client.study_has_ai_result(request.study_id):
            raise HTTPException(
                status_code=409,
                detail='This Orthanc study already contains an AI-derived series.',
            )

        payload = client.download_first_instance_dicom(request.study_id)
        response = get_pipeline().run(payload=payload, filename=f'{request.study_id}.dcm')
        logger.info(
            'request_id=%s status=%s orthanc_study_id=%s',
            response.request_id,
            response.status,
            request.study_id,
        )
        return response

    except HTTPException:
        raise
    except OrthancClientError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception('Orthanc inference failed')
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post('/orthanc/runs/{run_id}/store-derived', response_model=OrthancStoreDerivedResponse)
def orthanc_store_derived(run_id: str) -> OrthancStoreDerivedResponse:
    if not settings.orthanc_enabled:
        raise HTTPException(status_code=400, detail='Orthanc integration is disabled.')
    derived_path = settings.outputs_dir / run_id / 'derived_result.dcm'
    if not derived_path.exists():
        raise HTTPException(status_code=404, detail='Derived DICOM not found for this run.')
    try:
        reply = get_orthanc_client().upload_dicom(derived_path.read_bytes())
        return OrthancStoreDerivedResponse(
            run_id=run_id,
            orthanc_response=reply,
            message='Derived DICOM stored in Orthanc successfully.',
        )
    except Exception as exc:
        logger.exception('Orthanc derived DICOM upload failed')
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post('/orthanc/batch/infer-unprocessed', response_model=OrthancBatchInferResponse)
def orthanc_batch_infer_unprocessed(limit: int | None = None) -> OrthancBatchInferResponse:
    if not settings.orthanc_enabled:
        raise HTTPException(status_code=400, detail='Orthanc integration is disabled.')

    client = get_orthanc_client()
    pipeline = get_pipeline()

    try:
        studies = client.list_studies(limit=limit)
    except Exception as exc:
        logger.exception('Orthanc batch study listing failed')
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    items: list[OrthancBatchItem] = []
    already_analyzed = 0
    processed_now = 0
    failed = 0
    positive_cases = 0
    negative_cases = 0
    rejected_cases = 0

    for study in studies:
        study_id = study.study_id
        try:
            if client.study_has_ai_result(study_id):
                already_analyzed += 1
                items.append(
                    OrthancBatchItem(
                        study_id=study_id,
                        status='SKIPPED',
                        message='Study already contains AI-derived series.',
                    )
                )
                continue

            payload = client.download_first_instance_dicom(study_id)
            response = pipeline.run(payload=payload, filename=f'{study_id}.dcm')

            label = response.prediction.label
            if response.status == 'REJECT':
                rejected_cases += 1
            elif label == settings.label_positive:
                positive_cases += 1
            elif label == settings.label_negative:
                negative_cases += 1

            orthanc_response = None
            derived_path = settings.outputs_dir / response.artifacts.run_id / 'derived_result.dcm'
            if derived_path.exists():
                orthanc_response = client.upload_dicom(derived_path.read_bytes())

            processed_now += 1
            items.append(
                OrthancBatchItem(
                    study_id=study_id,
                    status='PROCESSED',
                    run_id=response.artifacts.run_id,
                    message=response.message,
                    orthanc_response=orthanc_response,
                    prediction_label=label,
                    prediction_status=response.status,
                )
            )
            logger.info(
                'batch processed study_id=%s run_id=%s status=%s',
                study_id,
                response.artifacts.run_id,
                response.status,
            )

        except Exception as exc:
            failed += 1
            logger.exception('Orthanc batch inference failed study_id=%s', study_id)
            items.append(
                OrthancBatchItem(
                    study_id=study_id,
                    status='FAILED',
                    message=str(exc),
                )
            )

    return OrthancBatchInferResponse(
        total_studies=len(studies),
        already_analyzed=already_analyzed,
        processed_now=processed_now,
        failed=failed,
        positive_cases=positive_cases,
        negative_cases=negative_cases,
        rejected_cases=rejected_cases,
        items=items,
        message='Batch analysis completed.',
    )