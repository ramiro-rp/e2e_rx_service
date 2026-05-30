# Global Deployment Guide

## Purpose

This guide describes how to deploy the complete project stack in local development mode:

- FastAPI backend
- Streamlit demo frontend
- Orthanc
- OHIF
- model artifacts and configuration

The goal is reproducible technical deployment for demonstration and validation, not clinical production deployment.

---

## 1. Repository structure

Expected repository layout:

```text
e2e_rx_service/
├─ backend/
├─ frontend-streamlit/
├─ deployment/
└─ README.md
```

### Main roles
- `backend/` -> inference service, QC, Grad-CAM outputs, DICOM derivation, Orthanc integration
- `frontend-streamlit/` -> thin demo client
- `deployment/` -> Orthanc + OHIF Docker stack

---

## 2. Prerequisites

### Required software
- Python 3.10+ or compatible local Python environment
- pip
- Docker Desktop
- Docker CLI with `docker compose`
- Git (optional for repository updates)

### Recommended checks
```powershell
python --version
pip --version
docker version
docker compose version
```

---

## 3. Required local artifacts

The backend expects the trained model artifacts to be present locally.

### Required files
Typical expected files:

```text
backend/artifacts/
├─ temperature.json
├─ threshold.json
└─ checkpoints/
   ├─ best_model.pt
   └─ last_checkpoint.pt   # optional for local recovery, not required for GitHub
```

### Important
Large `.pt` files should remain local and should **not** be committed to GitHub.

---

## 4. Backend deployment

Open a terminal in:

```text
backend/
```

### Install dependencies
```powershell
pip install -r requirements.txt
```

### Configuration
Create a local `.env` file in `backend/` based on your project needs.

Typical configuration areas:
- artifact paths
- Orthanc base URL
- Orthanc credentials
- service labels and metadata
- runtime options

### Start the backend
```powershell
py -m uvicorn dicom_service.src.api:app --port 8000
```

### Expected backend URL
```text
http://127.0.0.1:8000
```

### Basic validation
Open:

```text
http://127.0.0.1:8000/health
```

The backend should report:
- service name
- version
- model readiness
- Orthanc enabled status
- supported upload types

---

## 5. Frontend deployment

Open a second terminal in:

```text
frontend-streamlit/
```

### Install dependencies
```powershell
pip install -r requirements_streamlit.txt
```

### Start Streamlit
```powershell
streamlit run streamlit_app.py
```

### Expected frontend URL
Usually:

```text
http://localhost:8501
```

### Frontend purpose
The Streamlit app is a thin demo client. It should be used to:
- upload a DICOM file
- upload a standard image (`png`, `jpg`, `jpeg`)
- request an Orthanc study list
- run a single-study Orthanc analysis
- run batch analysis for non-analyzed Orthanc studies
- visualize output artifacts returned by the backend

---

## 6. Orthanc + OHIF deployment

Open a third terminal in:

```text
deployment/
```

### Start / restart the stack
```powershell
docker compose down
docker compose up -d
```

### Why not only Stop/Start in Docker Desktop?
Stopping and restarting an existing container in Docker Desktop does not guarantee that updated compose configuration is reapplied. If the compose file changed, use:

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

### Important
Use the OHIF URL with the trailing slash. Without it, the viewer may resolve static assets incorrectly and open with a blank page.

### Default local credentials
- Username: `orthanc`
- Password: `orthanc`

---

## 7. End-to-end startup order

Recommended startup order:

1. ensure local model artifacts are present
2. start Orthanc + OHIF
3. start backend
4. validate `/health`
5. start Streamlit
6. test local upload
7. test Orthanc study listing
8. test Orthanc single inference
9. test derived DICOM storage
10. test OHIF study visualization

---

## 8. Functional validation checklist

### Backend
- `/health` returns valid JSON
- `/infer` accepts local DICOM
- `/infer` accepts standard images
- outputs are published under `/outputs/...`

### Frontend
- local file upload works
- predicted class is shown
- overlay is available when the backend returns a transparent visual artifact
- derived DICOM download appears only for DICOM workflows

### Orthanc
- study list is visible through backend
- derived DICOM can be stored back into Orthanc
- already-analyzed studies are skipped in batch mode

### OHIF
- viewer loads successfully
- original studies can be opened
- derived series can be inspected in the same study workflow

---

## 9. Notes about local persistence

### Backend outputs
The backend writes per-run results under:

```text
backend/outputs/<run_id>/
```

These folders may contain:
- report JSON
- original image
- model input image
- heatmap
- overlay
- transparent heatmap
- transparent contour
- derived DICOM

These runtime outputs should not be committed to GitHub. Keep only:

```text
backend/outputs/.gitkeep
```

### Orthanc storage
The `orthanc-storage/` directory should remain local and should not be versioned.

---

## 10. Common issues

### Problem: model is not ready
Check that the expected artifacts exist in the configured paths.

### Problem: Orthanc endpoints return disabled
Check `.env` and ensure Orthanc integration is enabled in backend configuration.

### Problem: OHIF opens blank
Use:
```text
http://127.0.0.1:8042/ohif/
```
with the trailing slash, and verify Docker logs.

### Problem: study already analyzed
The backend now prevents duplicate single-study Orthanc processing and batch mode skips already analyzed studies.

### Problem: no overlay shown
For negative predictions, Grad-CAM visual outputs are intentionally not generated for user-facing display.

---

## 11. What is out of scope for this deployment guide

This guide does not cover:
- regulated production deployment
- security hardening beyond local demo needs
- cloud deployment
- asynchronous queues
- long-term database persistence
- automated CI/CD

---

## 12. Related project documents

Recommended companion documents:
- root `README.md`
- user manual
- administrator manual
- deployment notes for Orthanc + OHIF
- backend technical docs under `backend/docs/`
