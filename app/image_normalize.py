from __future__ import annotations

from io import BytesIO
from typing import Tuple

from PIL import Image, ImageOps


TARGET_WIDTH = 900
TARGET_HEIGHT = 1200
TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT  # 3:4


def normalize_image(image_bytes: bytes) -> Tuple[Image.Image, Tuple[int, int]]:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    source_resolution = image.size

    normalized = ImageOps.fit(
        image,
        (TARGET_WIDTH, TARGET_HEIGHT),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    return normalized, source_resolution
