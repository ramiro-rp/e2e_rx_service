# Basic Diagnostic Requirements (BDR)

## Purpose

This document summarizes the **diagnostic-side requirements** of the AI service in a simplified but faithful way. In the logic presented in the lecture materials, diagnostic requirements describe the clinical task solved by the AI service and the pathological findings it is expected to detect.

This reduced version is aligned with the actual MVP that was delivered. It does not invent clinical functions that are not implemented.

## 1. Service name

**RSNA DICOM Service MVP**

## 2. Clinical task solved by the AI service

Binary chest X-ray analysis for findings compatible with **pneumonia / lung opacity**.

## 3. Target study type

- Chest X-ray
- DICOM is the main validated workflow
- PNG/JPG/JPEG are accepted as a convenience mode, but they do not redefine the core diagnostic task

## 4. Clinical basis and input-side assumptions

Practical training and evaluation basis:
- **RSNA Pneumonia Detection Challenge** (Kaggle)

Input-side assumptions for the current MVP:
- chest X-ray study
- preferably DICOM
- standard images accepted only as a convenience path
- no extended institutional taxonomy is required in the current MVP

## 5. Main diagnostic logic

### 5.1 Positive case (1)
The study is treated as a positive case when:
- the model exceeds the operational threshold for the target class,
- the service returns a **positive** decision,
- and the result is interpreted as compatible with pneumonia / lung opacity.

#### 1a. Mandatory diagnostic answer
The response must include:
- positive decision
- calibrated probability
- confidence-related fields

Format:
- structured JSON

Delivery:
- backend HTTP response
- user-facing visualization in Streamlit

#### 1b. Visual explanatory evidence
For positive cases, the service may additionally return:
- original image
- model input image
- heatmap
- overlay
- transparent overlay / contour when available

Format:
- PNG outputs and generated artifact URLs

Delivery:
- retrieved by the demo client from backend output URLs

#### 1c. DICOM-derived result
In DICOM workflows, the service may additionally generate:
- a derived DICOM Secondary Capture object
- explicitly marked as a service-generated derived result

Format:
- DICOM Secondary Capture

Delivery:
- optional reinsertion into Orthanc
- viewer-side inspection through OHIF

### 5.2 Negative case (2)
The study is treated as a negative case when:
- the model does not exceed the operational threshold for the target class,
- and the service returns a **negative** decision.

The response must include:
- negative decision
- calibrated probability
- basic study metadata

Format:
- structured JSON

Delivery:
- backend HTTP response
- user-facing visualization in Streamlit

Important policy:
- user-facing Grad-CAM artifacts are **not exposed** for negative cases.

## 6. Diagnostic answer content

Mandatory in the current MVP:
- prediction label (`positive` / `negative`)
- calibrated probability
- confidence-related fields
- basic study metadata

Not implemented / out of scope in the current MVP:
- multi-class clinical classification
- formal morphometric measurements
- full radiology report drafting
- productive physician worklist prioritization

## 7. Output formats

The current MVP may produce:
- structured JSON
- explanatory PNG artifacts
- derived DICOM Secondary Capture in DICOM workflows

Not implemented in the current MVP:
- DICOM SR as the diagnostic output contract

## 8. References

1. Lecture materials on AI service requirements, especially the diagnostic-requirement logic.
2. RSNA Pneumonia Detection Challenge (Kaggle) as the practical basis for model training.
3. Final technical project documentation.

## 9. Fidelity note

This version keeps the diagnostic logic of the original requirement template while remaining honest about the delivered MVP. When a function is not implemented, it is explicitly marked as **not implemented**, **out of scope**, or **not applicable**, instead of being left blank.
