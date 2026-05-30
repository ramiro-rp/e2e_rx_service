# User Manual

## Purpose

This manual explains how to use **RSNA DICOM Service MVP** from the user side.

Functional subtitle:
- **End-to-end service for chest X-ray pneumonia / lung opacity analysis**

Main user-facing interface:
- **RSNA DICOM Service MVP — Demo Client**

## 1. Interfaces

### Streamlit demo client
Used to:
- upload a local DICOM or image,
- request an Orthanc study list,
- launch inference,
- visualize outputs,
- store derived DICOM in Orthanc when applicable.

### Orthanc
Used as the DICOM repository.

### OHIF
Used as the viewer for studies stored in Orthanc.

## 2. Supported input types

- DICOM (`.dcm`)
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)

Important:
- the main validated workflow is the DICOM path,
- standard images are supported as a convenience workflow.

## 3. Local analysis through Streamlit

1. Open the Streamlit app.
2. Confirm the backend URL, typically:
   `http://127.0.0.1:8000`
3. Select **Upload local file**.
4. Upload a supported file.
5. Click **Analyze**.

Returned information may include:
- status,
- predicted class,
- probability,
- confidence,
- study metadata,
- visual outputs.

## 4. Meaning of the prediction

- **positive** -> findings compatible with pneumonia / lung opacity
- **negative** -> no positive decision for the target class

This meaning should remain consistent across backend, frontend, notebook documentation, and repository docs.

## 5. Visual outputs

### Main image
The frontend shows the original image.

If a transparent visual artifact exists, the user may enable the overlay view.

### Additional generated images
When available, the interface may also show:
- model input image (`224x224`)
- heatmap (`224x224`)
- overlay (`224x224`)

For negative predictions, Grad-CAM user-facing visuals are intentionally not generated.

## 6. Analyzing a study from Orthanc

1. Switch source mode to **Select study from Orthanc**.
2. Refresh the study list if needed.
3. Select a study.
4. Click **Analyze**.

If the study already contains an AI-derived series, the system returns a warning and blocks duplicate analysis.

## 7. Storing a derived DICOM

This option is available only for DICOM workflows.

After a valid DICOM analysis, the user may:
- download the analyzed DICOM
- or store the derived DICOM back into Orthanc

## 8. Batch processing

1. Switch to Orthanc mode.
2. Click **Analyze all pending Orthanc studies**.

The backend:
- detects already analyzed studies,
- skips them,
- processes pending studies only,
- stores derived DICOM back into Orthanc when possible.

The frontend shows:
- total studies
- already analyzed
- processed now
- failed
- positive cases
- negative cases
- rejected cases

## 9. Viewing studies in OHIF

Open:
```text
http://127.0.0.1:8042/ohif/
```

Then:
- authenticate if required,
- browse studies,
- open original and derived series.

## 10. Scope note

This system is an academic technical MVP for demonstration and workflow validation. It is not a regulated diagnostic product.
