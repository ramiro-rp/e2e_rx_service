# User Manual

## Purpose

This manual describes how to use the project from the user side through the Streamlit demo client and the viewer stack.

The user workflow is intentionally simple:
- provide a study,
- request analysis,
- inspect outputs,
- optionally store the derived DICOM in Orthanc.

---

## 1. Main user interfaces

### Streamlit demo client
Used for:
- local file upload
- Orthanc study selection
- analysis execution
- result visualization
- optional derived DICOM storage

### Orthanc
Used as:
- local DICOM repository
- source of studies for analysis

### OHIF
Used as:
- viewer for studies stored in Orthanc

---

## 2. Supported input types

The system currently supports:

- DICOM (`.dcm`)
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)

### Important
The main validated workflow is still the DICOM workflow. Standard images are supported as a convenience mode and are less robust than native DICOM input.

---

## 3. Running a local analysis from Streamlit

### Step 1
Open the Streamlit client in your browser.

### Step 2
In the sidebar, confirm the backend URL, usually:

```text
http://127.0.0.1:8000
```

### Step 3
Choose **Upload local file**.

### Step 4
Upload one of the supported file types.

### Step 5
Click **Analyze**.

### Expected result
The system returns:
- status
- predicted class
- probability
- confidence
- study metadata
- visual outputs

---

## 4. Understanding the result

### Status
Typical status values:
- `ACCEPT`
- `ACCEPT_WITH_WARNINGS`
- `REJECT`

### Predicted class
The UI highlights the class visually.

Meaning:
- **positive** -> findings compatible with pneumonia / lung opacity
- **negative** -> no positive decision for the target class

### Study metadata
The result may include:
- source type
- modality
- original rows
- original columns
- photometric interpretation

---

## 5. Visual outputs

### Main visual output
The main image area shows the original image.

If a transparent visual layer is available, the user can enable the overlay display.

### Additional generated images
The interface may also display:
- model input image (`224x224`)
- heatmap (`224x224`)
- overlay (`224x224`)

### Important
For negative predictions, Grad-CAM-based user-facing artifacts are intentionally not shown.

---

## 6. Analyzing a study from Orthanc

### Step 1
Switch source mode to **Select study from Orthanc**.

### Step 2
Click **Refresh Orthanc study list** if needed.

### Step 3
Choose a study from the list.

### Step 4
Click **Analyze**.

### Expected result
The backend:
- checks whether the study was already analyzed,
- downloads the study,
- runs inference if allowed,
- returns the result to Streamlit.

### If the study was already analyzed
The interface shows a warning and does not launch a duplicate analysis.

---

## 7. Storing a derived DICOM in Orthanc

This option is available only for DICOM workflows.

### Step 1
Run an eligible DICOM analysis.

### Step 2
Use:
- **Download analyzed DICOM** to download the derived file locally
- or **Store analyzed study in Orthanc** to insert it back into Orthanc

### Expected result
A new derived DICOM series is stored in Orthanc.

---

## 8. Running batch analysis for Orthanc studies

### Step 1
Switch to **Select study from Orthanc**.

### Step 2
Click **Analyze all pending Orthanc studies**.

### What the system does
The backend:
- lists studies,
- checks which ones already contain an AI-derived series,
- skips analyzed studies,
- processes only the pending ones,
- stores derived DICOM objects back into Orthanc when possible.

### What the UI shows
A summary including:
- total studies
- already analyzed
- processed now
- failed
- positive cases
- negative cases
- rejected cases

---

## 9. Viewing studies in OHIF

### Step 1
Open:

```text
http://127.0.0.1:8042/ohif/
```

### Step 2
Authenticate if required.

### Step 3
Browse studies available in Orthanc.

### Step 4
Open the original and derived series for comparison.

---

## 10. Common messages

### Inference rejected
The file did not pass the appropriate QC path.

### Could not load Orthanc studies
The backend could not communicate with Orthanc or Orthanc integration is disabled.

### Study already contains AI-derived series
The selected Orthanc study was already analyzed and duplicate analysis is blocked.

### Could not render the main visual output
The frontend could not fetch or display one of the returned image outputs.

---

## 11. Intended use note

This system is an academic technical MVP. It is designed for:
- demonstration,
- integration testing,
- workflow validation,
- and prototype-level radiology service design.

It is not a regulated diagnostic product.
