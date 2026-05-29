# Architecture

## Current structure
- FastAPI backend: authoritative inference, QC, Orthanc integration, derived DICOM generation.
- Streamlit frontend: demo client only.
- Orthanc: optional DICOM repository for study selection and derived study storage.

## Input branches
- DICOM branch: DICOM parsing -> DICOM QC -> inference -> optional Grad-CAM -> optional derived DICOM.
- Standard image branch: image parsing -> image QC -> inference -> optional Grad-CAM for positive predictions.

## Orthanc scope
Orthanc integration is only used for DICOM studies. Standard image uploads are local-only and are not stored in Orthanc.
