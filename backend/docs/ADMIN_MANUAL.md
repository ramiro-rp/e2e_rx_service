# Administrator Manual

## Purpose

This manual explains how to operate and maintain the full stack of **RSNA DICOM Service MVP**.

Functional subtitle:
- **End-to-end service for chest X-ray pneumonia / lung opacity analysis**

## 1. Managed components

- backend
- frontend-streamlit
- deployment stack (Orthanc + OHIF)
- local artifacts
- runtime outputs
- repository hygiene

## 2. Naming conventions to preserve

Canonical service name:
- **RSNA DICOM Service MVP**

Functional subtitle:
- **End-to-end service for chest X-ray pneumonia / lung opacity analysis**

Canonical notebook:
- `notebooks/rsna_training_pipeline.ipynb`

Frontend presentation:
- **RSNA DICOM Service MVP — Demo Client**

These names should remain aligned across:
- documentation,
- backend configuration,
- frontend text,
- and training-side references.

## 3. Backend operations

From `backend/`:

```powershell
pip install -r requirements.txt
py -m uvicorn dicom_service.src.api:app --port 8000
```

Validate:
```text
http://127.0.0.1:8000/health
```

## 4. Frontend operations

From `frontend-streamlit/`:

```powershell
pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

## 5. Orthanc + OHIF operations

From `deployment/`:

```powershell
docker compose down
docker compose up -d
docker compose ps
docker compose logs -f
```

URLs:
- Orthanc: `http://127.0.0.1:8042`
- OHIF: `http://127.0.0.1:8042/ohif/`

Use the OHIF URL with the trailing slash.

## 6. Artifact management

Required local artifacts typically include:
- `temperature.json`
- `threshold.json`
- `best_model.pt`

The notebook is responsible for producing the artifacts; the backend is responsible for consuming them.

If artifacts are missing, validate:
- local file existence,
- configured paths,
- `.env` consistency.

## 7. Notebook role

The notebook should remain limited to:
- training,
- evaluation,
- calibration,
- threshold selection,
- artifact export,
- local model sanity-checking.

It should not be treated as the runtime service stack.

## 8. Runtime output management

Backend outputs are stored under:
```text
backend/outputs/<run_id>/
```

Keep only:
```text
backend/outputs/.gitkeep
```

Do not version real runtime outputs.

## 9. Repository hygiene

Do not version:
- `.env`
- `.pt`
- `orthanc-storage/`
- runtime outputs
- `__pycache__`
- local convenience launchers if excluded by project policy

## 10. Troubleshooting

### Backend starts but inference fails
Check:
- artifacts,
- paths,
- backend logs.

### Orthanc listing fails
Check:
- backend `.env`,
- Orthanc URL and credentials,
- backend logs.

### OHIF opens blank
Check:
- URL with trailing slash,
- Docker logs,
- browser console.

### Single Orthanc study cannot be reprocessed
Expected behavior if the study already contains an AI-derived series.

### Overlay missing
Expected for negative predictions.

## 11. Change procedure

Recommended order for any update:
1. adjust code or config
2. validate backend
3. validate frontend
4. validate Orthanc integration
5. validate OHIF
6. review affected documentation in cascade
7. commit and push
