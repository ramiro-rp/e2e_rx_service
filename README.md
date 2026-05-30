# E2E AI Radiology Service

End-to-end MVP for chest X-ray **pneumonia / lung opacity** analysis with a trained model, a FastAPI runtime service, a Streamlit demo client, Orthanc integration, and OHIF visualization.

This repository packages the project as a reproducible system rather than only a notebook experiment. It supports local inference, DICOM-oriented workflows, derived DICOM generation, and viewer-based inspection of studies.

## Project goal

The goal of the project is to turn a notebook-trained chest X-ray classifier into a **defendable end-to-end service pipeline** that can:

- accept imaging inputs,
- perform backend quality-control checks,
- run calibrated inference,
- produce explainability artifacts,
- generate derived DICOM output for DICOM workflows,
- integrate with Orthanc,
- and expose studies through OHIF.

The current implementation is a technical MVP, not a clinical production deployment.

## Current system components

### 1. Backend (`backend/`)
Authoritative runtime service implemented with FastAPI.

Main responsibilities:
- local inference for DICOM and standard images,
- QC gating,
- structured JSON responses,
- Grad-CAM artifact generation for positive predictions,
- derived DICOM generation for DICOM workflows,
- Orthanc integration,
- batch processing of non-analyzed Orthanc studies.

### 2. Streamlit demo client (`frontend-streamlit/`)
Thin user-facing interface for:
- uploading local studies,
- selecting Orthanc studies,
- launching inference,
- visualizing returned outputs,
- storing derived DICOM objects in Orthanc.

Frontend validation is intentionally minimal. The backend remains the authoritative layer.

### 3. Deployment stack (`deployment/`)
Docker-based local deployment for:
- Orthanc,
- OHIF,
- and supporting viewer-side study inspection.

## Clinical task

Binary chest X-ray decision for:

- **positive** -> findings compatible with *pneumonia / lung opacity*
- **negative** -> threshold not exceeded for the target class

The project uses a calibrated classification workflow and preserves core study metadata for traceability.

## Key implemented features

- Notebook-trained and exported model artifacts
- FastAPI backend with structured inference contract
- DICOM input support
- Standard image input support (`png`, `jpg`, `jpeg`)
- DICOM-specific QC and image-specific QC
- Original Rows/Columns preserved in study metadata
- Grad-CAM outputs for positive predictions
- No user-facing Grad-CAM for negative predictions
- Derived DICOM generation for DICOM workflows
- Orthanc study listing and single-study analysis
- Orthanc batch processing for non-analyzed studies
- OHIF viewer integration through Orthanc

## Repository structure

```text
e2e_rx_service/
├─ backend/
│  ├─ dicom_service/
│  ├─ shared/
│  ├─ docs/
│  ├─ artifacts/
│  ├─ outputs/
│  └─ requirements.txt
├─ frontend-streamlit/
│  ├─ streamlit_app.py
│  └─ requirements_streamlit.txt
├─ deployment/
│  ├─ docker-compose.yml
│  └─ DEPLOYMENT_ORTHANC_OHIF.md
└─ .gitignore
```

## Runtime flow

### Local inference
1. User uploads a DICOM or standard image.
2. Backend performs the appropriate QC branch.
3. Backend runs calibrated inference.
4. Backend returns:
   - QC block,
   - prediction block,
   - output URLs,
   - artifact references.
5. Streamlit fetches and renders the generated outputs.

### Orthanc workflow
1. Streamlit requests the study list from the backend.
2. Backend queries Orthanc through its REST API.
3. User selects a study.
4. Backend downloads the study instance, runs inference, and generates outputs.
5. For DICOM workflows, a derived DICOM can be stored back into Orthanc.
6. OHIF can be used to inspect original and derived studies.

## Main backend endpoints

- `GET /health`  
  Service status and supported capabilities.

- `POST /infer`  
  Local inference for DICOM or standard image input.

- `GET /orthanc/studies`  
  Returns available Orthanc studies.

- `POST /orthanc/infer`  
  Runs inference for a selected Orthanc study if it was not already analyzed.

- `POST /orthanc/runs/{run_id}/store-derived`  
  Stores the derived DICOM for a previous run in Orthanc.

- `POST /orthanc/batch/infer-unprocessed`  
  Processes all Orthanc studies that do not already contain an AI-derived series.

## Quick start

### Backend
From the `backend/` folder:

```bash
pip install -r requirements.txt
py -m uvicorn dicom_service.src.api:app --port 8000
```

### Streamlit frontend
From the `frontend-streamlit/` folder:

```bash
pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

### Orthanc + OHIF
From the `deployment/` folder:

```bash
docker compose down
docker compose up -d
```

Orthanc:
- `http://127.0.0.1:8042`

OHIF:
- `http://127.0.0.1:8042/ohif/`

See:
- `deployment/DEPLOYMENT_ORTHANC_OHIF.md`

## Required local artifacts

The backend expects model artifacts in the configured artifact paths.

Typical required files:
- `temperature.json`
- `threshold.json`
- model checkpoint(s) placed locally in the expected path

Large checkpoint files are intentionally kept out of the repository and must be provided locally.

## Configuration

The backend uses `.env` loading through `python-dotenv`.

Typical configuration areas:
- artifact paths
- Orthanc integration
- service identity / labels
- runtime behavior

Do not commit:
- `.env`
- local outputs
- Orthanc persistent storage
- large model checkpoints

## Documentation already included

Technical notes currently available under `backend/docs/` include:
- architecture
- functional requirements
- testing notes
- deployment notes
- iteration journal

Deployment notes for Orthanc + OHIF are available in:
- `deployment/DEPLOYMENT_ORTHANC_OHIF.md`

## Current limitations

- The main validated route is still the DICOM workflow.
- Standard image support exists, but is less reliable than the DICOM path.
- Grad-CAM is a visual explanatory aid, not segmentation.
- This is an MVP service, not a production-ready regulated clinical system.
- The project does not yet include full operational hardening, long-term persistence, or asynchronous job orchestration.

## Next documentation steps

The next formal documentation block should include:
- deployment guide,
- user manual,
- administrator manual,
- and final GitHub-facing cleanup of repository instructions.

## License / academic context

This repository is part of an academic project focused on turning a machine-learning model into a working radiology-service pipeline with practical integration layers.
