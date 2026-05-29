# Testing

## Reproducibility checklist
1. Install backend dependencies, including `python-dotenv`.
2. Confirm `.env` exists and contains valid Orthanc settings if Orthanc mode is used.
3. Confirm model artifacts exist in the expected paths.
4. Start backend.
5. If Orthanc mode is used, confirm Orthanc responds on port 8042.

## Core tests
- `GET /health`
- invalid DICOM upload returns structured `REJECT`
- invalid standard image upload returns structured `REJECT`
- valid DICOM upload returns `ACCEPT` or `ACCEPT_WITH_WARNINGS`
- Orthanc study listing works when Orthanc is enabled
