from __future__ import annotations

import numpy as np
import torch
from PIL import Image

from shared.config import settings


IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def pil_to_tensor(img: Image.Image) -> torch.Tensor:
    resized = img.resize((settings.image_size, settings.image_size))
    arr = np.asarray(resized).astype(np.float32) / 255.0
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD
    arr = np.transpose(arr, (2, 0, 1))
    return torch.from_numpy(arr).unsqueeze(0)


def resize_rgb_for_overlay(img: Image.Image) -> np.ndarray:
    return np.array(img.resize((settings.image_size, settings.image_size)))
