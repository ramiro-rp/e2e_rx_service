# RSNA DICOM Service MVP

End-to-end service for chest X-ray pneumonia / lung opacity analysis

This repository contains an academic end-to-end MVP that turns a trained chest X-ray classification model into a usable service stack with:

- a training notebook,
- a FastAPI backend,
- a Streamlit demo client,
- Orthanc integration,
- and OHIF visualization.

The project is designed as a reproducible technical pipeline for demonstration, validation, and integration practice. It is not a regulated clinical deployment.

## Repository structure

```text
e2e_rx_service/
├─ backend/
├─ deployment/
├─ frontend-streamlit/
├─ notebooks/
│  ├─ rsna_training_pipeline.ipynb
│  └─ README.md
└─ README.md
```

### Folder roles

- `backend/`  
  Runtime inference service, QC logic, artifact loading, Grad-CAM outputs, Orthanc integration, batch processing, and DICOM-derived output handling.

- `frontend-streamlit/`  
  Thin demo client for local uploads, Orthanc study selection, result rendering, and user-facing interaction with the backend.

- `deployment/`  
  Local Docker-based stack for Orthanc and OHIF, plus deployment documentation.

- `notebooks/`  
  Training-side material only: dataset preparation, training, evaluation, calibration, artifact export, and local model sanity-checking.

## Clinical task

Binary chest X-ray prediction for:

- **positive** -> findings compatible with pneumonia / lung opacity
- **negative** -> no positive decision for the target class

This meaning is used consistently across the training notebook, backend responses, frontend display, and derived DICOM tagging.

## Main implemented features

- ResNet-18 based trained model (`resnet18_rsna`)
- Training notebook with artifact export
- FastAPI backend with structured response contract
- DICOM input support
- Standard image support (`png`, `jpg`, `jpeg`) as a convenience workflow
- QC for both DICOM and standard-image branches
- Original image dimensions preserved in metadata
- Grad-CAM visual outputs for positive predictions
- No user-facing Grad-CAM for negative predictions
- Derived DICOM generation for DICOM workflows
- Orthanc single-study analysis
- Orthanc batch processing for non-analyzed studies
- OHIF viewer integration through Orthanc

## System layers

### Training layer
Implemented in the notebook:
- dataset preparation,
- training,
- evaluation,
- calibration,
- threshold selection,
- artifact export,
- local visual sanity-checking.

### Runtime layer
Implemented in the backend and connected tools:
- API endpoints,
- QC response handling,
- inference service behavior,
- visual output publishing,
- Orthanc integration,
- batch processing,
- and viewer-facing workflow.

## Main backend endpoints

- `GET /health`
- `POST /infer`
- `GET /orthanc/studies`
- `POST /orthanc/infer`
- `POST /orthanc/runs/{run_id}/store-derived`
- `POST /orthanc/batch/infer-unprocessed`

## Quick start

### 1. Backend
From `backend/`:

```bash
pip install -r requirements.txt
py -m uvicorn dicom_service.src.api:app --port 8000
```

### 2. Streamlit frontend
From `frontend-streamlit/`:

```bash
pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

### 3. Orthanc + OHIF
From `deployment/`:

```bash
docker compose down
docker compose up -d
```

Orthanc:
- `http://127.0.0.1:8042`

OHIF:
- `http://127.0.0.1:8042/ohif/`

## Required local artifacts

The backend expects the trained artifacts to be available locally, typically:

- `best_model.pt`
- `temperature.json`
- `threshold.json`

Large model checkpoint files are intentionally kept out of GitHub and must be provided locally.

## Required documentation inside the repository

Primary documentation should include:

- root `README.md`
- `deployment/GLOBAL_DEPLOYMENT_GUIDE.md`
- `deployment/DEPLOYMENT_ORTHANC_OHIF.md`
- `backend/docs/USER_MANUAL.md`
- `backend/docs/ADMIN_MANUAL.md`
- `backend/docs/TRAINING_AND_MODEL.md`
- `notebooks/README.md`

## Current limitations

- The main validated path remains the DICOM workflow.
- Standard image inference is available, but less robust than native DICOM input.
- Grad-CAM is explanatory visualization, not segmentation.
- This repository represents a technical MVP, not a clinical production system.
- Large local artifacts and persistent study storage are intentionally excluded from version control.

## Naming convention

Canonical system name:
- **RSNA DICOM Service MVP**

Functional subtitle:
- **End-to-end service for chest X-ray pneumonia / lung opacity analysis**

Notebook filename:
- **rsna_training_pipeline.ipynb**

Streamlit should be presented as:
- **RSNA DICOM Service MVP — Demo Client**

## Next documentation step

After repository cleanup and naming alignment, the documentation package should be kept synchronized with any future structural or functional changes.
