from __future__ import annotations

import base64
from io import BytesIO
from typing import Any, Dict, List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image
import yaml

from app.image_normalize import normalize_image
from app.spec_builder import build_spec
from app.validators import validate_spec


router = APIRouter(prefix="/api", tags=["analyze"])


def _image_to_data_url(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=92)
    payload = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{payload}"


def _build_analysis_payload(
    image_bytes: bytes,
    marketplace: str,
    source_url: str,
) -> Dict[str, Any]:
    normalized_image, source_resolution = normalize_image(image_bytes)
    overlay_elements: List[Dict[str, Any]] = []

    spec = build_spec(
        marketplace=marketplace,
        source_url=source_url,
        source_resolution=source_resolution,
        normalized_image=normalized_image,
        overlay_elements=overlay_elements,
    )
    validation_errors = validate_spec(spec)
    spec_yaml = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)

    return {
        "ok": len(validation_errors) == 0,
        "normalized": {
            "aspect_ratio": "3:4",
            "resolution_px": [900, 1200],
            "preview_data_url": _image_to_data_url(normalized_image),
        },
        "spec": spec,
        "spec_yaml": spec_yaml,
        "validation": {
            "errors": validation_errors,
            "warnings": [
                "MVP extractor returns placeholder structural/semantic fields.",
            ],
        },
    }


@router.post("/analyze")
async def analyze_card(
    image: UploadFile = File(...),
    marketplace: str = Form("other"),
    source_url: str = Form(""),
) -> Dict[str, Any]:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return _build_analysis_payload(
        image_bytes=image_bytes,
        marketplace=marketplace,
        source_url=source_url,
    )


@router.post("/analyze.yaml")
async def analyze_card_yaml(
    image: UploadFile = File(...),
    marketplace: str = Form("other"),
    source_url: str = Form(""),
) -> Response:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    payload = _build_analysis_payload(
        image_bytes=image_bytes,
        marketplace=marketplace,
        source_url=source_url,
    )
    return Response(content=payload["spec_yaml"], media_type="application/x-yaml")
