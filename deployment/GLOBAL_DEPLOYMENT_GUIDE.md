# Global Deployment Guide

## Purpose

This guide explains how to deploy the complete local stack of **RSNA DICOM Service MVP**:

- backend service,
- Streamlit demo client,
- Orthanc,
- OHIF,
- and the locally required model artifacts.

The deployment target is a reproducible technical MVP environment for demonstration and validation.

## Repository structure expected by this guide

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

## 1. Prerequisites

### Required software
- Python 3.10+ or compatible environment
- pip
- Docker Desktop
- Docker CLI with `docker compose`

### Recommended quick checks
```powershell
python --version
pip --version
docker version
docker compose version
```

## 2. Local artifacts required by the backend

The backend needs the trained artifacts produced by the notebook.

Typical required files:

```text
backend/artifacts/
├─ temperature.json
├─ threshold.json
└─ checkpoints/
   └─ best_model.pt
```

Optional local checkpoint:
- `last_checkpoint.pt`

Large `.pt` files should remain local and should not be committed to GitHub.

## 3. Backend deployment

Open a terminal in:

```text
backend/
```

### Install dependencies
```powershell
pip install -r requirements.txt
```

### Local configuration
Create a local `.env` in `backend/` according to your environment.

Typical configuration groups:
- model artifact paths
- Orthanc integration
- service metadata
- runtime options

### Start backend
```powershell
py -m uvicorn dicom_service.src.api:app --port 8000
```

### Backend URL
```text
http://127.0.0.1:8000
```

### Validation
Open:
```text
http://127.0.0.1:8000/health
```

## 4. Streamlit deployment

Open a second terminal in:

```text
frontend-streamlit/
```

### Install dependencies
```powershell
pip install -r requirements_streamlit.txt
```

### Start the demo client
```powershell
streamlit run streamlit_app.py
```

### Typical URL
```text
http://localhost:8501
```

The frontend is a thin client only. Business logic remains in the backend.

## 5. Orthanc + OHIF deployment

Open a third terminal in:

```text
deployment/
```

### Start or recreate the stack
```powershell
docker compose down
docker compose up -d
```

### Validate the stack
```powershell
docker compose ps
docker compose logs -f
```

### URLs
Orthanc:
```text
http://127.0.0.1:8042
```

OHIF:
```text
http://127.0.0.1:8042/ohif/
```

Use the OHIF URL with the trailing slash.

## 6. Recommended startup order

1. ensure local artifacts are present
2. start Orthanc + OHIF
3. start backend
4. validate `/health`
5. start Streamlit
6. test local upload
7. test Orthanc study listing
8. test single Orthanc inference
9. test derived DICOM storage
10. test OHIF visualization

## 7. Functional validation checklist

### Backend
- `/health` responds correctly
- `/infer` accepts local DICOM
- `/infer` accepts standard images
- outputs are available under `/outputs/...`

### Frontend
- local upload works
- Orthanc selection works
- predicted class is displayed
- overlay appears only when visual artifacts exist
- derived DICOM actions appear only for DICOM workflows

### Orthanc
- studies are listed through backend
- derived DICOM can be stored
- already-analyzed studies are skipped in batch mode

### OHIF
- viewer loads correctly
- original studies can be opened
- derived series can be inspected

## 8. Notebook role in deployment context

The notebook is not part of the runtime deployment path, but it is part of the project deliverable and artifact provenance.

Its role is:
- training,
- evaluation,
- calibration,
- threshold selection,
- artifact export,
- local model validation.

Canonical notebook:
```text
notebooks/rsna_training_pipeline.ipynb
```

## 9. Runtime outputs and persistence

### Backend outputs
Stored locally under:
```text
backend/outputs/<run_id>/
```

Do not commit runtime outputs. Keep only:
```text
backend/outputs/.gitkeep
```

### Orthanc persistence
`orthanc-storage/` should remain local and should not be versioned.

## 10. Common issues

### Backend reports `model_ready=false`
Check that required artifacts exist and match configured paths.

### Orthanc endpoints report disabled
Check `.env` and confirm Orthanc integration is enabled.

### OHIF opens blank
Use:
```text
http://127.0.0.1:8042/ohif/
```
and verify Docker logs.

### Duplicate study analysis blocked
This is expected for already analyzed Orthanc studies in the current design.

### No overlay shown
Expected for negative predictions.

## 11. Related documents

- root `README.md`
- `deployment/DEPLOYMENT_ORTHANC_OHIF.md`
- `backend/docs/USER_MANUAL.md`
- `backend/docs/ADMIN_MANUAL.md`
- `backend/docs/TRAINING_AND_MODEL.md`
- `notebooks/README.md`
