# Basic Functional Requirements

## Supported inputs
1. Local DICOM upload through `/infer`.
2. Local standard image upload (`png`, `jpg`, `jpeg`) through `/infer`.
3. Orthanc study analysis through `/orthanc/infer` for DICOM-only workflows.

## QC policy
- DICOM uploads use the DICOM QC branch.
- Standard image uploads use a separate image QC branch.
- Frontend validation is only for presentation and source-mode control. The authoritative validation remains in the backend.

## Output policy
- Positive predictions may generate Grad-CAM visual outputs.
- Negative predictions do not generate user-facing Grad-CAM outputs.
- Standard image runs do not generate derived DICOM outputs.
- DICOM runs may generate `derived_result.dcm` and can be stored in Orthanc.
