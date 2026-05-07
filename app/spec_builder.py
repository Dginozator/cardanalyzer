from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, List

from app.derived_fields import (
    compute_clustering_keys,
    compute_safe_areas,
    compute_tone_saturation_temperature,
)
from app.extractors import bootstrap_structural_elements, extract_palette


def build_spec(
    marketplace: str,
    source_url: str,
    source_resolution: tuple[int, int],
    normalized_image,
    overlay_elements: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    overlay_elements = overlay_elements or []
    palette = extract_palette(normalized_image)
    tone_fields = compute_tone_saturation_temperature(palette["dominant"])
    structural_elements = bootstrap_structural_elements()
    safe_areas = compute_safe_areas(overlay_elements)

    spec: Dict[str, Any] = {
        "schema_version": "1.4",
        "card_id": str(uuid4()),
        "source": {
            "url": source_url,
            "marketplace": marketplace,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        },
        "canvas": {
            "aspect_ratio": "3:4",
            "resolution_px": [source_resolution[0], source_resolution[1]],
            "safe_areas": safe_areas,
        },
        "structural": {
            "composition": {
                "archetype": "single_focus",
                "density": "medium",
            },
            "elements": structural_elements,
        },
        "visual": {
            "background": {"type": "solid", "colors": [palette["dominant"][0]], "notes": "auto"},
            "palette": {
                "dominant": palette["dominant"],
                "accents": palette["accents"],
                "tone": tone_fields["tone"],
                "saturation": tone_fields["saturation"],
                "temperature": tone_fields["temperature"],
            },
        },
        "semantic": {
            "product_category": "other",
            "text_content": {"full_text": "", "keywords": []},
            "image_meaning": {"scene_description": "MVP auto-generated description."},
        },
        "marketplace_overlay": {"elements": overlay_elements},
        "clustering_keys": {},
        "generation": {
            "hints": {
                "must_keep": [
                    "visual.background",
                    "visual.palette.dominant",
                    "structural.elements[role=product_main]",
                ],
                "free_to_change": [
                    "visual.palette.accents",
                    "structural.elements[role=text_feature]",
                ],
            },
            "constraints": {
                "min_text_contrast_ratio": 4.5,
                "max_density_pct": 65.0,
                "min_safe_area_clearance_pct": 2.0,
                "forbid_overlap_with_safe_area": True,
                "max_palette_colors": 8,
            },
        },
    }

    spec["clustering_keys"] = compute_clustering_keys(spec)
    return spec
