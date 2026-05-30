# RSNA DICOM Service MVP

**End-to-end service for chest X-ray pneumonia / lung opacity analysis**

This repository contains an academic end-to-end MVP that turns a notebook-trained chest X-ray classifier into a reproducible service stack with:

- a FastAPI backend,
- a Streamlit demo client,
- Orthanc integration,
- OHIF visualization,
- and derived DICOM generation for DICOM workflows.

The project is a technical MVP for demonstration, validation, and integration work. It is not a regulated clinical product.

## Project goal

The goal of the project is to move beyond a training notebook and provide a coherent service pipeline that can:

- accept imaging inputs,
- apply backend quality-control checks,
- run calibrated inference,
- generate explainability artifacts,
- create derived DICOM output,
- and integrate with local PACS/viewer-style components.

## Training basis

The model training workflow is based on the **RSNA Pneumonia Detection Challenge** dataset from Kaggle.

- Official competition page: `https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge`
- The dataset is **not redistributed** in this repository.
- The final notebook used for training and artifact export is stored under `notebooks/`.

For notebook-side details, see:
- `notebooks/README.md`
- `backend/docs/TRAINING_AND_MODEL.md`

## Current system components

### 1. Backend (`backend/`)
Main runtime service responsibilities:
- local inference for DICOM and standard images,
- QC gating,
- structured JSON responses,
- Grad-CAM artifact generation for positive predictions,
- derived DICOM generation for DICOM workflows,
- Orthanc integration,
- batch processing of non-analyzed Orthanc studies.

### 2. Streamlit demo client (`frontend-streamlit/`)
Thin user-facing client for:
- local upload,
- Orthanc study selection,
- analysis triggering,
- visual result inspection,
- derived DICOM download / store actions.

### 3. Deployment stack (`deployment/`)
Deployment layer for:
- Orthanc,
- OHIF,
- and local study visualization through Docker Compose.

### 4. Notebook layer (`notebooks/`)
Training-side layer for:
- data preparation,
- training,
- evaluation,
- calibration,
- threshold selection,
- artifact export,
- and local model sanity-checking.

## Clinical task

Binary chest X-ray decision for:

- **positive** -> findings compatible with pneumonia / lung opacity
- **negative** -> no positive decision for the target class

## Key implemented features

- notebook-trained and exported model artifacts
- FastAPI backend with structured inference contract
- DICOM input support
- standard image support (`png`, `jpg`, `jpeg`)
- DICOM-specific QC and image-specific QC
- original Rows/Columns preserved in study metadata
- Grad-CAM outputs for positive predictions
- no user-facing Grad-CAM for negative predictions
- derived DICOM generation for DICOM workflows
- Orthanc study listing and single-study analysis
- Orthanc batch processing for non-analyzed studies
- OHIF viewer integration through Orthanc

## Repository structure

```text
e2e_rx_service/
├─ backend/
├─ frontend-streamlit/
├─ deployment/
├─ notebooks/
└─ README.md
```

## Runtime flow

### Local inference
1. The user uploads a DICOM or standard image.
2. The backend applies the appropriate QC path.
3. The backend runs calibrated inference.
4. The backend returns:
   - QC information,
   - prediction fields,
   - output URLs,
   - artifact references.
5. The frontend fetches and renders the generated outputs.

### Orthanc workflow
1. The frontend requests the study list from the backend.
2. The backend queries Orthanc through its REST API.
3. The user selects a study.
4. The backend downloads the study instance and runs inference.
5. For DICOM workflows, a derived DICOM can be stored back into Orthanc.
6. OHIF can be used to inspect original and derived studies.

## Main backend endpoints

- `GET /health`
- `POST /infer`
- `GET /orthanc/studies`
- `POST /orthanc/infer`
- `POST /orthanc/runs/{run_id}/store-derived`
- `POST /orthanc/batch/infer-unprocessed`

## Quick start

### Backend
From `backend/`:

```bash
pip install -r requirements.txt
py -m uvicorn dicom_service.src.api:app --port 8000
```

### Streamlit
From `frontend-streamlit/`:

```bash
pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

### Orthanc + OHIF
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

The backend expects local model artifacts such as:

- `best_model.pt`
- `temperature.json`
- `threshold.json`

Large checkpoint files are intentionally kept out of the repository and must be provided locally.

## Documentation map

- Root overview: `README.md`
- Global deployment: `deployment/GLOBAL_DEPLOYMENT_GUIDE.md`
- Orthanc + OHIF deployment: `deployment/DEPLOYMENT_ORTHANC_OHIF.md`
- User manual: `backend/docs/USER_MANUAL.md`
- Administrator manual: `backend/docs/ADMIN_MANUAL.md`
- Training/model documentation: `backend/docs/TRAINING_AND_MODEL.md`
- Notebook notes: `notebooks/README.md`

## Current limitations

- The strongest validated route is still the DICOM workflow.
- Standard image support exists, but is less robust than native DICOM input.
- Grad-CAM is an explanatory visualization, not segmentation.
- This is an MVP service, not a production-ready regulated clinical system.

## Academic context

This repository is part of an academic project focused on turning a machine-learning workflow into a working radiology-service pipeline with practical integration layers.
