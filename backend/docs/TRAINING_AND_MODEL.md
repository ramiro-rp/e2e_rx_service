# Training and Model Documentation

## Purpose

This document explains the training-side part of **RSNA DICOM Service MVP**.

Functional subtitle:
- **End-to-end service for chest X-ray pneumonia / lung opacity analysis**

It defines the role of the notebook, the model architecture, the exported artifacts, and the boundary between training and runtime service behavior.

## 1. Notebook role

The notebook is responsible for:
- data preparation,
- training,
- evaluation,
- calibration,
- threshold selection,
- artifact export,
- local visual sanity-checking.

Canonical notebook:
```text
notebooks/rsna_training_pipeline.ipynb
```

## 2. Clinical task

Binary chest X-ray prediction for:
- **positive** -> findings compatible with pneumonia / lung opacity
- **negative** -> no positive decision for the target class

## 3. Model architecture

The trained model is based on:
- **ResNet-18**
- internal model identifier:
  - `resnet18_rsna`

## 4. Input representation

The model performs inference on a resized representation of the study.

Primary input size:
- `224 x 224`

Original image dimensions remain important for traceability and visualization, but the model predicts from the resized input.

## 5. Evaluation and calibration

The notebook should include:
- metric computation,
- validation/testing review,
- calibration,
- threshold selection.

Important:
- the threshold is an operational decision cutoff,
- not a metric.

## 6. Artifacts exported to the backend

Main artifacts:
- `best_model.pt`
- `temperature.json`
- `threshold.json`

Optional support files may include:
- calibration metrics
- summary metrics
- plots used for local validation

## 7. Boundary between notebook and service

### Notebook responsibilities
- training logic
- evaluation logic
- calibration logic
- artifact export
- local demo of the model

### Backend responsibilities
- API behavior
- QC contracts
- Orthanc integration
- batch processing
- runtime visual output publishing
- derived DICOM handling

## 8. Explainability note

The notebook may generate Grad-CAM examples for local validation.

These should be interpreted as explanatory visualizations, not segmentation.

## 9. Naming alignment

Canonical service name:
- **RSNA DICOM Service MVP**

Functional subtitle:
- **End-to-end service for chest X-ray pneumonia / lung opacity analysis**

Canonical notebook name:
- `rsna_training_pipeline.ipynb`

This alignment should also be reflected in repository documentation and frontend presentation.

## 10. Limitations

- The notebook is not the deployment guide.
- Large model files may remain local and outside version control.
- The strongest validated operational route remains the DICOM workflow in the service stack.

## 11. Summary

The notebook is the training and artifact-generation layer of the project. Its main deliverable to the service is the exported artifact set and the validated model settings used by the backend.
