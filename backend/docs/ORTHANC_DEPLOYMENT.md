# Orthanc Deployment (Docker)

## Recommended image
Use the official `orthancteam/orthanc` Docker image. The Orthanc documentation explains that the `osimis/orthanc` image name was renamed to `orthancteam/orthanc`, and that the Docker images are designed to be used with Docker Compose. The same documentation also states that configuration can be passed through `ORTHANC_JSON`. Orthanc listens on the DICOM port 4242 and the REST API port 8042 by default, and stores data in the storage directory mounted inside the container. See the official Orthanc documentation for details. 

## Minimal deployment
The repository includes `deploy_orthanc_docker_compose.yml`.

### Start Orthanc
```bash
cd e2e_service_repo
docker compose -f deploy_orthanc_docker_compose.yml up -d
```

### Open Orthanc Explorer
Open:
- `http://127.0.0.1:8042`

Default demo credentials in this compose file:
- username: `orthanc`
- password: `orthanc`

## Backend settings
Set these variables in your backend environment:
- `ORTHANC_ENABLED=true`
- `ORTHANC_BASE_URL=http://127.0.0.1:8042`
- `ORTHANC_USERNAME=orthanc`
- `ORTHANC_PASSWORD=orthanc`

## Workflow in this iteration
1. Upload a DICOM to Orthanc or keep studies already stored there.
2. Use Streamlit to request `/orthanc/studies`.
3. Select one study.
4. Send `/orthanc/infer` with the selected `study_id`.
5. If needed, send `/orthanc/runs/{run_id}/store-derived` to push the derived DICOM back into Orthanc.
