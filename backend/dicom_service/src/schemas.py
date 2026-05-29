from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class QCResult(BaseModel):
    status: Literal['ACCEPT', 'ACCEPT_WITH_WARNINGS', 'REJECT']
    reject_reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    summary: str


class ModelInfo(BaseModel):
    model_name: str
    model_version: str
    input_size: List[int]
    calibrated: bool


class DicomMeta(BaseModel):
    modality: Optional[str] = None
    rows: Optional[int] = None
    columns: Optional[int] = None
    photometric_interpretation: Optional[str] = None
    study_instance_uid: Optional[str] = None
    series_instance_uid: Optional[str] = None
    sop_instance_uid: Optional[str] = None
    source_type: Optional[Literal['dicom', 'image']] = None


class QCBlock(BaseModel):
    reject_reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    summary: str
    dicom_meta: DicomMeta


class PredictionBlock(BaseModel):
    label: Optional[str] = None
    probability: Optional[float] = None
    threshold: Optional[float] = None
    decision_source: Optional[str] = None
    target_class: str
    confidence: Optional[float] = None
    calibration_temperature: Optional[float] = None


class OutputPayload(BaseModel):
    image_analyzed_url: Optional[str] = None
    heatmap_url: Optional[str] = None
    overlay_url: Optional[str] = None
    original_image_url: Optional[str] = None
    transparent_heatmap_url: Optional[str] = None
    transparent_contour_url: Optional[str] = None


class ArtifactRefs(BaseModel):
    run_id: str
    report_url: Optional[str] = None
    derived_dicom_url: Optional[str] = None


class InferResponse(BaseModel):
    request_id: str
    status: Literal['ACCEPT', 'ACCEPT_WITH_WARNINGS', 'REJECT']
    task: str
    model_info: ModelInfo
    qc: QCBlock
    prediction: PredictionBlock
    outputs: OutputPayload = Field(default_factory=OutputPayload)
    artifacts: ArtifactRefs
    message: str


class OrthancStudySummary(BaseModel):
    study_id: str
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    study_date: Optional[str] = None
    study_description: Optional[str] = None
    accession_number: Optional[str] = None
    modalities_in_study: List[str] = Field(default_factory=list)
    instance_count: Optional[int] = None


class OrthancInferRequest(BaseModel):
    study_id: str


class OrthancStoreDerivedResponse(BaseModel):
    run_id: str
    orthanc_response: dict
    message: str


class OrthancBatchItem(BaseModel):
    study_id: str
    status: Literal['SKIPPED', 'PROCESSED', 'FAILED']
    run_id: Optional[str] = None
    message: Optional[str] = None
    orthanc_response: Optional[dict] = None
    prediction_label: Optional[str] = None
    prediction_status: Optional[str] = None


class OrthancBatchInferResponse(BaseModel):
    total_studies: int
    already_analyzed: int
    processed_now: int
    failed: int
    positive_cases: int
    negative_cases: int
    rejected_cases: int
    items: List[OrthancBatchItem] = Field(default_factory=list)
    message: str