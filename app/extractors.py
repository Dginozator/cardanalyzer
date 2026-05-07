from __future__ import annotations

from typing import Any, Dict, List

from PIL import Image


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def extract_palette(image: Image.Image) -> Dict[str, Any]:
    quantized = image.convert("RGB").quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    counts = sorted(quantized.getcolors() or [], reverse=True)
    dominant: List[str] = []
    for _count, color_index in counts[:3]:
        i = color_index * 3
        rgb = (palette[i], palette[i + 1], palette[i + 2])
        dominant.append(_rgb_to_hex(rgb))
    while len(dominant) < 3:
        dominant.append("#808080")
    accents = dominant[1:]
    return {"dominant": dominant, "accents": accents}


def bootstrap_structural_elements() -> List[Dict[str, Any]]:
    # MVP: placeholder element layout before VLM/CV markup.
    return [
        {
            "element_id": "e_product_main_1",
            "role": "product_main",
            "group_id": None,
            "bbox": [0.2, 0.2, 0.6, 0.55],
            "anchor": "center",
            "z_order": 1,
            "shape": "rectangle",
            "arrangement": None,
            "product_view": "catalog",
            "content": {"text": None},
            "visual": {
                "fill_color": None,
                "stroke_color": None,
                "text_color": None,
                "has_icon": False,
                "icon_concept": None,
                "has_shadow": False,
                "contrast_level": "medium",
            },
            "relations": {"parent": None, "aligned_with": [], "overlaps": []},
            "notes": "MVP placeholder",
        }
    ]
