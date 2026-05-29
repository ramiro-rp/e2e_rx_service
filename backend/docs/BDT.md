# BDT - Basic Diagnostic Requirements

## Clinical task
Chest X-ray binary decision for `pneumonia_or_lung_opacity`.

## Output meaning
- `positive`: findings compatible with the target MVP class
- `negative`: the operational threshold is not exceeded

## Restrictions
- The Grad-CAM heatmap is an explanatory demo artifact.
- It does not replace clinical segmentation or exact localization.
- Visualization is produced on the image resized to `224x224`.
