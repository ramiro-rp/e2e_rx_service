# Notebooks

## Purpose

This folder contains the final notebook used for:

- data preparation,
- model training,
- evaluation,
- calibration,
- threshold selection,
- artifact export,
- and a local visual sanity-check of the trained model.

The notebook is **not** the runtime service. Backend inference, Orthanc integration, OHIF integration, and frontend behavior belong to the deployed service stack outside the notebook.

## Final notebook name

Use the notebook under this folder as:

```text
rsna_training_pipeline.ipynb
```

## Dataset reference

The training workflow is based on the **RSNA Pneumonia Detection Challenge** dataset from Kaggle.

- Official competition page: `https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge`

The dataset is not redistributed in this repository and must be obtained separately by the user.

## What the notebook should produce

The notebook should generate the model artifacts required by the backend, typically:

- `best_model.pt`
- `temperature.json`
- `threshold.json`

Optional supporting outputs may include:
- calibration metrics
- summary metrics
- evaluation figures

Large checkpoint files should remain local and should not be committed to GitHub if repository size is a concern.

## What should stay outside the notebook

The notebook should not be treated as the full E2E system. It should not be the place where the final runtime pipeline is documented or implemented.

The following belong to the service stack outside the notebook:
- FastAPI runtime behavior
- Orthanc integration
- OHIF deployment
- Streamlit client flow
- backend REST responses
- deployment orchestration

## Local validation role

A final local inference/demo section is acceptable in the notebook as a sanity-check of the trained model.

That local section should be presented only as:
- model validation,
- artifact validation,
- and visual confirmation of behavior,

not as the production runtime path.

## Suggested repository usage

```text
e2e_rx_service/
├─ notebooks/
│  ├─ rsna_training_pipeline.ipynb
│  └─ README.md
```

## Related documentation

For a higher-level description of the trained model, dataset basis, and exported artifacts, see:

- `backend/docs/TRAINING_AND_MODEL.md`
