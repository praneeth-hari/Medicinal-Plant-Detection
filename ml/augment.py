"""
Background-swap augmentation
============================
The training photos have a strong background bias (e.g. every Neem photo is one
leaf on a stone floor, every Curry photo is a sprig on white paper), so the
classifier can learn "white background => Curry" instead of the leaf itself.

``BackgroundSwap`` cuts out the (green) leaf pixels and pastes them onto a random
new background, which breaks that shortcut. Backgrounds are plain colours, noise,
gradients, or the background of other training photos (with their leaves filled in).
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

_IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def green_mask(arr: np.ndarray) -> np.ndarray:
    """Boolean mask of leaf-like (green / yellow-green) pixels in an RGB uint8 array."""
    hsv = np.asarray(Image.fromarray(arr).convert("HSV")).astype(np.int16)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # PIL hue is 0-255 (360 deg): ~45-190 deg covers yellow-green through green/teal.
    mask = (h >= 32) & (h <= 135) & (s >= 45) & (v >= 25)
    return mask


def _grow(mask: np.ndarray, px: int = 2) -> np.ndarray:
    """Dilate a boolean mask a little so leaf edges keep their anti-aliased pixels."""
    img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * px + 1))
    return np.asarray(img) > 127


class BackgroundSwap:
    """Callable PIL transform: replace non-leaf pixels with a random background.

    Args:
        pool_dir: Folder of class sub-folders (e.g. ``data/train``) used to harvest
            real-world backgrounds.
        p: Probability of applying the swap.
        size: Working resolution (images are resized to ``size`` x ``size`` first).
        pool_size: How many background photos to cache in memory.
        seed: Seed for building the pool (sampling afterwards uses ``random``).
    """

    def __init__(self, pool_dir: str | Path, p: float = 0.7, size: int = 224,
                 pool_size: int = 300, seed: int = 0) -> None:
        self.p = p
        self.size = size
        self.backgrounds: list[np.ndarray] = []
        rng = random.Random(seed)
        files = [f for f in Path(pool_dir).rglob("*") if f.suffix.lower() in _IMG_EXT]
        rng.shuffle(files)
        for f in files[:pool_size]:
            try:
                arr = np.asarray(Image.open(f).convert("RGB").resize((size, size)))
            except Exception:
                continue
            self.backgrounds.append(self._fill_leaves(arr))

    @staticmethod
    def _fill_leaves(arr: np.ndarray) -> np.ndarray:
        """Remove leaf pixels from a photo by filling them with the mean background colour."""
        mask = _grow(green_mask(arr), 3)
        out = arr.copy()
        if (~mask).any():
            out[mask] = arr[~mask].mean(axis=0).astype(np.uint8)
        return out

    def _random_background(self) -> np.ndarray:
        s = self.size
        kind = random.random()
        if kind < 0.25:  # Neutral studio/paper background (white/off-white)
            base = random.choice([
                (255, 255, 255), (248, 248, 245), (240, 240, 235), (225, 225, 220)
            ])
            bg = np.empty((s, s, 3), np.uint8)
            bg[:] = base
        elif kind < 0.45:  # Natural outdoor earthy / garden tones (soil, mulch, stones)
            earthy_tones = [
                (75, 55, 40), (105, 80, 60), (130, 105, 80), (160, 135, 110),
                (45, 75, 35), (60, 95, 45), (35, 60, 30), (80, 110, 65)
            ]
            base = np.array(random.choice(earthy_tones), np.float32)
            bg = np.clip(base + np.random.randn(s, s, 3) * random.uniform(10, 35), 0, 255).astype(np.uint8)
        elif kind < 0.65:  # Outdoor light gradients / soft bokeh sunlight simulation
            a = np.array(random.choice([(180, 210, 230), (220, 210, 180), (70, 100, 50)]), np.float32)
            b = np.array(random.choice([(90, 120, 70), (140, 160, 120), (240, 240, 235)]), np.float32)
            t = np.linspace(0, 1, s, dtype=np.float32)[:, None, None]
            bg = np.clip(np.broadcast_to(a * (1 - t) + b * t, (s, s, 3)), 0, 255).astype(np.uint8)
        elif kind < 0.80:  # Noise / texture background
            base = np.array([random.randint(60, 200) for _ in range(3)], np.float32)
            bg = np.clip(base + np.random.randn(s, s, 3) * random.uniform(8, 40), 0, 255).astype(np.uint8)
        else:  # Another photo's real background from dataset
            bg = random.choice(self.backgrounds) if self.backgrounds else np.full((s, s, 3), 240, np.uint8)
            if random.random() < 0.5:
                bg = bg[:, ::-1]
        return np.ascontiguousarray(bg)

    def __call__(self, img: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return img
        img = img.convert("RGB").resize((self.size, self.size))
        arr = np.asarray(img)
        mask = _grow(green_mask(arr), 1)
        frac = mask.mean()
        if frac < 0.01 or frac > 0.85:  # no leaf found / whole frame is green: leave as is
            return img
        out = np.where(mask[..., None], arr, self._random_background())
        return Image.fromarray(out.astype(np.uint8))
