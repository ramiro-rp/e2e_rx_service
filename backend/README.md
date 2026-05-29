# RSNA DICOM Service MVP

This repository contains the backend service for the first checkpoint of the chest X-ray analysis MVP.

## Supported upload types
- DICOM (`.dcm`)
- Standard image (`.png`, `.jpg`, `.jpeg`)

## Important behavior
- DICOM remains the primary workflow.
- Standard image uploads use a separate image QC path in the backend.
- Orthanc integration is only enabled for DICOM workflows.
- Derived DICOM generation is only produced for DICOM inference runs.
- User-facing Grad-CAM is not generated for negative predictions.

## Required model artifacts
Before starting the backend, confirm that these files exist:
- `artifacts/checkpoints/best_model.pt`
- `artifacts/temperature.json`
- `artifacts/threshold.json`

## Environment configuration
The backend loads variables from `.env`. Install dependencies first, including `python-dotenv`.

## Start backend
```bash
uvicorn dicom_service.src.api:app --port 8000
```

## Orthanc
Orthanc is optional but required for `/orthanc/*` endpoints.


## Notes on standard-image inference
Standard image uploads are intended as a convenience/demo path. The main validated workflow remains DICOM-based. For positive standard-image runs, the backend generates `original_image.png`, `image_analyzed.png`, `heatmap.png`, `overlay.png`, and `transparent_heatmap.png`. For negative standard-image runs, no Grad-CAM assets are generated.
