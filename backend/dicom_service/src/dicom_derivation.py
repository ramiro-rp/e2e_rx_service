from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image

from shared.config import settings


def _pil_to_rgb_array(image: Image.Image) -> np.ndarray:
    return np.array(image.convert('RGB'), dtype=np.uint8)


def build_secondary_capture_from_source(source_dcm, image: Image.Image, predicted_label: str, probability: float | None, run_id: str):
    from pydicom.dataset import FileDataset, FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

    arr = _pil_to_rgb_array(image)
    rows, cols = arr.shape[0], arr.shape[1]

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b'\0' * 128)
    now = datetime.utcnow()
    ds.SpecificCharacterSet = 'ISO_IR 100'
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = 'OT'
    ds.ConversionType = 'WSD'
    ds.SeriesInstanceUID = generate_uid()
    ds.StudyInstanceUID = getattr(source_dcm, 'StudyInstanceUID', generate_uid())
    ds.PatientName = getattr(source_dcm, 'PatientName', 'Anonymous^Unknown')
    ds.PatientID = getattr(source_dcm, 'PatientID', 'UNKNOWN')
    ds.PatientBirthDate = getattr(source_dcm, 'PatientBirthDate', '')
    ds.PatientSex = getattr(source_dcm, 'PatientSex', '')
    ds.StudyDate = getattr(source_dcm, 'StudyDate', now.strftime('%Y%m%d'))
    ds.StudyTime = getattr(source_dcm, 'StudyTime', now.strftime('%H%M%S'))
    ds.SeriesDate = now.strftime('%Y%m%d')
    ds.SeriesTime = now.strftime('%H%M%S')
    ds.ContentDate = now.strftime('%Y%m%d')
    ds.ContentTime = now.strftime('%H%M%S')
    ds.AccessionNumber = getattr(source_dcm, 'AccessionNumber', '')
    ds.StudyID = getattr(source_dcm, 'StudyID', '')
    ds.SeriesNumber = 999
    ds.InstanceNumber = 1
    ds.Manufacturer = settings.ai_manufacturer
    ds.SoftwareVersions = settings.service_version
    ds.SecondaryCaptureDeviceManufacturer = settings.ai_manufacturer
    ds.SecondaryCaptureDeviceManufacturerModelName = settings.ai_model_label
    ds.ImageType = ['DERIVED', 'SECONDARY', 'AI_ANALYSIS']
    ds.SeriesDescription = f"AI Analysis - {settings.target_class.capitalize()} {predicted_label.capitalize()}"    
    prob_text = f'{probability:.5f}' if probability is not None else 'n/a'
    ds.ImageComments = (
        f'target_class={settings.target_class};'
        f'label={predicted_label}; '
        f'probability={prob_text}; '
        f'model={settings.model_name}:{settings.model_version}; '
        f'task={settings.task_name}; '
        f'run_id={run_id};'
        f'analyzed_by={settings.ai_model_label}'
    )
    ds.SamplesPerPixel = 3
    ds.PhotometricInterpretation = 'RGB'
    ds.Rows = rows
    ds.Columns = cols
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PlanarConfiguration = 0
    ds.PixelData = arr.tobytes()
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    return ds


def save_secondary_capture(path: Path, dataset) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.save_as(str(path), write_like_original=False)
    return path
