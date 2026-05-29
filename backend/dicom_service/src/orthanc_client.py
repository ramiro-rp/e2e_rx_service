from __future__ import annotations

from typing import Any

import requests

from dicom_service.src.schemas import OrthancStudySummary
from shared.config import settings


class OrthancClientError(RuntimeError):
    pass


class OrthancClient:
    def __init__(self) -> None:
        self.base_url = settings.orthanc_base_url.rstrip('/')
        self.auth = (settings.orthanc_username, settings.orthanc_password)
        self.timeout = settings.orthanc_timeout
        self.verify = settings.orthanc_verify_ssl

    def _get(self, path: str) -> Any:
        response = requests.get(
            f'{self.base_url}{path}',
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify,
        )
        response.raise_for_status()
        return response.json()

    def _get_bytes(self, path: str) -> bytes:
        response = requests.get(
            f'{self.base_url}{path}',
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify,
        )
        response.raise_for_status()
        return response.content

    def _post_bytes(self, path: str, payload: bytes) -> dict:
        response = requests.post(
            f'{self.base_url}{path}',
            data=payload,
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify,
        )
        response.raise_for_status()
        return response.json()

    def list_studies(self, limit: int | None = None) -> list[OrthancStudySummary]:
        ids = self._get('/studies')
        max_items = limit or settings.orthanc_study_list_limit
        summaries: list[OrthancStudySummary] = []
        for study_id in ids[:max_items]:
            data = self._get(f'/studies/{study_id}')
            tags = data.get('MainDicomTags', {})
            summaries.append(
                OrthancStudySummary(
                    study_id=study_id,
                    patient_name=tags.get('PatientName'),
                    patient_id=tags.get('PatientID'),
                    study_date=tags.get('StudyDate'),
                    study_description=tags.get('StudyDescription'),
                    accession_number=tags.get('AccessionNumber'),
                    modalities_in_study=data.get('ModalitiesInStudy', []) or [],
                    instance_count=data.get('InstancesCount') or data.get('ExpectedNumberOfInstances'),
                )
            )
        return summaries

    def get_study(self, study_id: str) -> dict:
        return self._get(f'/studies/{study_id}')

    @staticmethod
    def _is_ai_series_description(series_description: str | None) -> bool:
        desc = (series_description or '').strip()
        if not desc:
            return False
        if desc == settings.ai_series_description:
            return True
        if desc.startswith('AI Analysis'):
            return True
        return False

    def study_has_ai_result(self, study_id: str) -> bool:
        study = self.get_study(study_id)
        series_ids = study.get('Series', [])
        for series_id in series_ids:
            series = self._get(f'/series/{series_id}')
            tags = series.get('MainDicomTags', {}) or {}
            series_description = tags.get('SeriesDescription')
            if self._is_ai_series_description(series_description):
                return True
        return False

    def download_first_instance_dicom(self, study_id: str) -> bytes:
        study = self.get_study(study_id)
        series_ids = study.get('Series', [])
        if not series_ids:
            raise OrthancClientError(f'Study {study_id} does not contain any series.')
        series = self._get(f'/series/{series_ids[0]}')
        instance_ids = series.get('Instances', [])
        if not instance_ids:
            raise OrthancClientError(f'Series {series_ids[0]} does not contain any instances.')
        return self._get_bytes(f'/instances/{instance_ids[0]}/file')

    def upload_dicom(self, payload: bytes) -> dict:
        return self._post_bytes('/instances', payload)