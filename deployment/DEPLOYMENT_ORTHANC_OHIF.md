# Orthanc + OHIF Deployment Notes

## Purpose
This stack provides the local DICOM repository and viewer layer for the project:

- **Orthanc**: PACS-like DICOM server and REST API
- **OHIF**: web viewer served through Orthanc

The AI backend and Streamlit client are deployed separately.

## Prerequisites
- Docker Desktop installed and running
- Docker CLI available in PowerShell / CMD
- A working `docker compose` command
- The project backend already configured separately

## Deployment folder
Recommended contents:

```text
deployment/
├─ docker-compose.yml
└─ orthanc-storage/   # local persistent data, do not commit to Git
```

`orthanc-storage/` should remain local and should **not** be pushed to GitHub.

## docker-compose.yml
Use the compose file that successfully enabled both Orthanc and OHIF.

Key points:
- `OHIF_PLUGIN_ENABLED: "true"`
- `DICOM_WEB_PLUGIN_ENABLED: "true"`
- `ORTHANC__OHIF__DATA_SOURCE: "dicom-web"`
- `ORTHANC__OHIF__ROUTER_BASENAME: "/ohif/"`

Example structure:

```yaml
services:
  orthanc:
    image: orthancteam/orthanc:latest
    container_name: orthanc
    ports:
      - "8042:8042"
      - "4242:4242"
    environment:
      VERBOSE_ENABLED: "true"
      OHIF_PLUGIN_ENABLED: "true"
      DICOM_WEB_PLUGIN_ENABLED: "true"
      ORTHANC__NAME: "OrthancDemo"
      ORTHANC__REGISTERED_USERS: |
        {"orthanc":"orthanc"}
      ORTHANC__AUTHENTICATION_ENABLED: "true"
      ORTHANC__REMOTE_ACCESS_ALLOWED: "true"
      ORTHANC__OHIF__DATA_SOURCE: "dicom-web"
      ORTHANC__OHIF__ROUTER_BASENAME: "/ohif/"
    volumes:
      - ./orthanc-storage:/var/lib/orthanc/db
    restart: unless-stopped
```

## Start / restart the stack
From the deployment folder:

```powershell
docker compose down
docker compose up -d
```

### Why not just Stop/Start from Docker Desktop?
Stopping and starting a container from Docker Desktop usually restarts the **existing** container.
It does **not** guarantee that a modified `docker-compose.yml` is reapplied.

If the compose file changed, use:

```powershell
docker compose down
docker compose up -d
```

## Verify the container
```powershell
docker compose ps
docker compose logs -f
```

## URLs
### Orthanc
`http://127.0.0.1:8042`

### OHIF
Use the URL **with the trailing slash**:

`http://127.0.0.1:8042/ohif/`

The trailing slash matters. Without it, OHIF may resolve static assets incorrectly and show a blank page.

## Credentials
Example credentials used during local setup:
- Username: `orthanc`
- Password: `orthanc`

## Notes
- Orthanc stores original and derived DICOM studies.
- OHIF is only the viewer layer.
- The AI backend does not run inside this compose stack.
- The backend communicates with Orthanc through its REST API.

## Common issues
### 1. `docker compose` changes not applied
Use:
```powershell
docker compose down
docker compose up -d
```

### 2. OHIF opens blank
Check:
- that the URL is `http://127.0.0.1:8042/ohif/`
- that both OHIF and DICOMweb plugins are enabled
- browser console for missing assets or authentication errors

### 3. Orthanc data should not be versioned
Do not commit:
- `orthanc-storage/`
- local DB files
- persisted studies

Only commit:
- `docker-compose.yml`
- deployment docs

## Relationship with the rest of the project
- Backend: runs inference, generates outputs and derived DICOM
- Streamlit: thin demo client
- Orthanc: stores DICOM studies and derived objects
- OHIF: visualizes studies from Orthanc
