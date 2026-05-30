# Administrator Manual

## Purpose

This manual describes how to manage, configure, validate, and troubleshoot the full project stack.

It is intended for the person responsible for:
- local deployment,
- environment configuration,
- runtime checks,
- and repository-level maintenance.

---

## 1. Managed components

The administrator is responsible for these parts:

- FastAPI backend
- Streamlit frontend
- Orthanc
- OHIF
- local model artifacts
- deployment configuration
- local runtime outputs

---

## 2. Repository-level responsibilities

The administrator should maintain a clean repository state.

### Do not version
- `.env`
- model checkpoint `.pt` files
- Orthanc persistent storage
- runtime output folders
- local `.cmd` launchers if they are only convenience helpers
- `__pycache__`

### Keep in Git
- source code
- requirements files
- `.env.example`
- deployment compose file
- technical documentation
- `.gitkeep` for empty runtime output directories

---

## 3. Backend administration

### Install dependencies
From `backend/`:

```powershell
pip install -r requirements.txt
```

### Start the backend
```powershell
py -m uvicorn dicom_service.src.api:app --port 8000
```

### Validate backend readiness
Open:

```text
http://127.0.0.1:8000/health
```

Check:
- model readiness
- service version
- Orthanc enabled status
- supported upload types

### Backend logs
Use the terminal where `uvicorn` is running. Runtime errors and Orthanc-related failures are written there unless redirected manually.

---

## 4. Frontend administration

### Install dependencies
From `frontend-streamlit/`:

```powershell
pip install -r requirements_streamlit.txt
```

### Start Streamlit
```powershell
streamlit run streamlit_app.py
```

### Typical frontend URL
```text
http://localhost:8501
```

### Frontend role
The frontend is a thin client. Do not move business logic from backend to frontend.

---

## 5. Orthanc + OHIF administration

### Start stack
From `deployment/`:

```powershell
docker compose down
docker compose up -d
```

### Check status
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

### Important operational note
Use the OHIF URL with the trailing slash.

---

## 6. Model artifacts management

The administrator must ensure that required artifacts are present locally.

Typical files:
- `temperature.json`
- `threshold.json`
- model checkpoint files in the configured artifact path

### If the backend reports `model_ready=false`
Check:
- file existence
- configured paths
- path consistency in `.env`

---

## 7. Environment configuration

The backend loads configuration through `.env`.

Administrative responsibilities include:
- maintaining correct artifact paths
- maintaining Orthanc connection settings
- ensuring credentials are valid
- updating service labels consistently

### Do not commit the real `.env`
Keep a safe `.env.example` in the repository instead.

---

## 8. Runtime output management

Backend runs generate outputs under:

```text
backend/outputs/<run_id>/
```

These may contain:
- report JSON
- images
- derived DICOM files

### Good practice
- keep `.gitkeep`
- remove historical runtime outputs from the repository
- use runtime folders only for local execution and validation

---

## 9. Orthanc workflow administration

### Single-study analysis
The backend blocks duplicate manual analysis when a study already contains an AI-derived series.

### Batch processing
The batch endpoint:
- detects already analyzed studies,
- skips them,
- processes pending studies only.

### Derived DICOM
The backend can store a generated derived DICOM back into Orthanc.

Administrative checks:
- derived series are visible
- metadata labels are correct
- batch logic is not duplicating existing studies

---

## 10. Typical troubleshooting

### Problem: backend starts but inference fails
Check:
- artifact files
- model path
- backend terminal logs

### Problem: Orthanc list does not load
Check:
- `.env` settings
- Orthanc credentials
- Orthanc base URL
- backend logs

### Problem: OHIF opens blank
Check:
- viewer URL with trailing slash
- Docker logs
- browser console
- plugin flags in `docker-compose.yml`

### Problem: already analyzed study cannot be reprocessed
This is expected behavior in the current design. The system blocks duplicate manual Orthanc analysis.

### Problem: no overlay shown
For negative predictions, this is expected behavior.

---

## 11. Git / repository hygiene

### Before pushing changes
Check that the repository does not track:
- `.env`
- `.pt`
- `orthanc-storage/`
- runtime outputs
- local convenience scripts if excluded by policy

### Typical update flow
```powershell
git add .
git status
git commit -m "Describe the change"
git push
```

---

## 12. Administrative change policy

Recommended order when changing the system:
1. update code or config
2. validate backend locally
3. validate frontend locally
4. validate Orthanc integration
5. validate OHIF
6. update documentation
7. push changes to GitHub

---

## 13. Scope note

This administrator manual is intended for local technical administration of the academic MVP. It is not a production operations handbook for a regulated medical deployment.
