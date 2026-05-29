from __future__ import annotations

import io
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError


class StandardImageReadError(Exception):
    """Raised when the uploaded payload cannot be parsed as a supported standard image."""


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_supported_standard_image(filename: str | None) -> bool:
    if not filename:
        return False
    return Path(filename).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def read_standard_image_from_bytes(payload: bytes) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(payload))
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise StandardImageReadError('invalid_standard_image') from exc
    return img.convert('RGB')


def image_to_uint8_array(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert('L')).astype(np.uint8)


def image_to_pil_and_array(img: Image.Image) -> Tuple[Image.Image, np.ndarray]:
    rgb = img.convert('RGB')
    arr = image_to_uint8_array(rgb)
    return rgb, arr
