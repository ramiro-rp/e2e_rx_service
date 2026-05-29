# Journal

## Current iteration highlights
- Added `.env` loading through `python-dotenv`.
- Added standard image support (`png`, `jpg`, `jpeg`) through the same `/infer` endpoint.
- Split QC into DICOM QC and standard-image QC branches.
- Kept Orthanc integration restricted to DICOM workflows.
- Preserved frontend as a demo-only client.
- Kept negative predictions free from user-facing Grad-CAM outputs.


## 2026-04-13 - Consolidation of v10 into v11
- Kept the validated `.env` loading behavior through `python-dotenv`.
- Preserved Orthanc integration as the active deployment path for DICOM studies.
- Preserved dual local input support: DICOM and standard image (`png`, `jpg`, `jpeg`).
- Preserved the user-facing policy of not generating Grad-CAM for negative predictions.
- Preserved the generation of `transparent_heatmap.png` for positive standard-image runs and positive DICOM runs.
- Cleaned packaging artifacts (`__pycache__`, historical `outputs/run_*`) so the repository starts from a reproducible state.
- Added a contract test to verify that positive standard-image inference exposes `transparent_heatmap_url` and does not expose a derived DICOM URL.
