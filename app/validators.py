from __future__ import annotations

from typing import Any, Dict, List

from app.derived_fields import compute_safe_areas


def validate_spec(spec: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    structural_elements = spec.get("structural", {}).get("elements", [])
    product_main_count = sum(1 for e in structural_elements if e.get("role") == "product_main")
    if product_main_count > 1:
        errors.append("structural.elements: more than one product_main.")

    palette = spec.get("visual", {}).get("palette", {})
    if len(palette.get("dominant", [])) != 3:
        errors.append("visual.palette.dominant must have exactly 3 colors.")

    safe_areas = spec.get("canvas", {}).get("safe_areas", {})
    top = float(safe_areas.get("top", 0.0))
    bottom = float(safe_areas.get("bottom", 0.0))
    left = float(safe_areas.get("left", 0.0))
    right = float(safe_areas.get("right", 0.0))
    if top + bottom >= 1.0:
        errors.append("canvas.safe_areas: top + bottom must be < 1.0.")
    if left + right >= 1.0:
        errors.append("canvas.safe_areas: left + right must be < 1.0.")

    overlay_elements = spec.get("marketplace_overlay", {}).get("elements", [])
    expected_safe = compute_safe_areas(overlay_elements)
    for side in ("top", "right", "bottom", "left"):
        if round(float(safe_areas.get(side, 0.0)), 4) != round(float(expected_safe[side]), 4):
            errors.append(f"canvas.safe_areas.{side} mismatch with overlay-derived value.")

    return errors
