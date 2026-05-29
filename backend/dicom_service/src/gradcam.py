from __future__ import annotations

import cv2
import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module) -> None:
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self.h1 = target_layer.register_forward_hook(self._forward_hook)
        self.h2 = target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, inp, out):
        self.activations = out.detach()

    def _backward_hook(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def close(self) -> None:
        self.h1.remove()
        self.h2.remove()

    def __call__(self, x: torch.Tensor) -> np.ndarray:
        self.model.zero_grad(set_to_none=True)
        logit = self.model(x).squeeze(1)
        logit.backward(torch.ones_like(logit))
        acts = self.activations
        grads = self.gradients
        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = (weights * acts).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)
        cam = cam.squeeze().detach().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam


def overlay_cam_on_rgb(rgb_uint8: np.ndarray, cam: np.ndarray, alpha: float = 0.35) -> np.ndarray:
    heat = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    return np.clip((1 - alpha) * rgb_uint8 + alpha * heat, 0, 255).astype(np.uint8)


def resize_cam_to_shape(cam: np.ndarray, width: int, height: int) -> np.ndarray:
    resized = cv2.resize(cam, (width, height), interpolation=cv2.INTER_LINEAR)
    resized = resized.astype(np.float32)
    return np.clip(resized, 0.0, 1.0)


def transparent_heatmap_rgba(cam: np.ndarray, alpha_scale: float = 0.45) -> np.ndarray:
    heat = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    alpha = np.clip(cam * 255.0 * alpha_scale, 0, 255).astype(np.uint8)
    return np.dstack([heat, alpha])


def transparent_heatmap_contour_rgba(
    cam: np.ndarray,
    threshold: float = 0.75,
    red: int = 255,
    green: int = 55,
    blue: int = 0,
    alpha: int = 230,
) -> np.ndarray:
    """
    Build a transparent RGBA contour from a normalized CAM in [0, 1].
    Only the high-activation region is kept, and only its border is rendered.
    """
    if cam.ndim != 2:
        raise ValueError("CAM must be a 2D array.")

    mask = cam >= threshold
    if not np.any(mask):
        h, w = cam.shape
        return np.zeros((h, w, 4), dtype=np.uint8)

    up = np.roll(mask, -1, axis=0)
    down = np.roll(mask, 1, axis=0)
    left = np.roll(mask, -1, axis=1)
    right = np.roll(mask, 1, axis=1)

    # Avoid wrap-around artifacts at borders
    up[-1, :] = False
    down[0, :] = False
    left[:, -1] = False
    right[:, 0] = False

    interior = mask & up & down & left & right
    contour = mask & (~interior)

    h, w = cam.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[contour, 0] = red
    rgba[contour, 1] = green
    rgba[contour, 2] = blue
    rgba[contour, 3] = alpha
    return rgba