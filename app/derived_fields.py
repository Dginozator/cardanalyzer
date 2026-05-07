from __future__ import annotations

import colorsys
from typing import Any, Dict, List, Tuple


THRESHOLD = 0.05


def clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_safe_areas(overlay_elements: List[Dict[str, Any]] | None) -> Dict[str, float]:
    if not overlay_elements:
        return {"top": 0.0, "right": 0.0, "bottom": 0.0, "left": 0.0}

    top_candidates: List[float] = []
    bottom_candidates: List[float] = []
    left_candidates: List[float] = []
    right_candidates: List[float] = []

    for element in overlay_elements:
        bbox = element.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x, y, w, h = [float(v) for v in bbox]
        if y < THRESHOLD:
            top_candidates.append(y + h)
        if (y + h) > (1.0 - THRESHOLD):
            bottom_candidates.append(1.0 - y)
        if x < THRESHOLD:
            left_candidates.append(x + w)
        if (x + w) > (1.0 - THRESHOLD):
            right_candidates.append(1.0 - x)

    return {
        "top": round(clamp_01(max(top_candidates) if top_candidates else 0.0), 4),
        "right": round(clamp_01(max(right_candidates) if right_candidates else 0.0), 4),
        "bottom": round(clamp_01(max(bottom_candidates) if bottom_candidates else 0.0), 4),
        "left": round(clamp_01(max(left_candidates) if left_candidates else 0.0), 4),
    }


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    raw = hex_color.strip().lower().lstrip("#")
    if len(raw) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    r = int(raw[0:2], 16) / 255.0
    g = int(raw[2:4], 16) / 255.0
    b = int(raw[4:6], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue = (h * 360.0) % 360.0
    return hue, s, l


def compute_tone_saturation_temperature(dominant: List[str]) -> Dict[str, str]:
    hsl = [hex_to_hsl(color) for color in dominant]
    mean_s = sum(v[1] for v in hsl) / len(hsl)
    mean_l = sum(v[2] for v in hsl) / len(hsl)

    if mean_l > 0.66:
        tone = "light"
    elif mean_l < 0.33:
        tone = "dark"
    else:
        tone = "medium"

    if mean_s < 0.25:
        saturation = "muted"
    elif mean_s > 0.65:
        saturation = "vivid"
    else:
        saturation = "moderate"

    if mean_s < 0.15:
        temperature = "neutral"
    else:
        warm_count = 0
        cool_count = 0
        for hue, sat, _light in hsl:
            if sat < 0.15:
                continue
            is_warm = (0.0 <= hue <= 60.0) or (300.0 <= hue <= 360.0)
            if is_warm:
                warm_count += 1
            elif 60.0 < hue < 300.0:
                cool_count += 1
        if warm_count >= 2:
            temperature = "warm"
        elif warm_count <= 1 and cool_count >= 1:
            temperature = "cool"
        else:
            temperature = "neutral"

    return {"tone": tone, "saturation": saturation, "temperature": temperature}


def compute_clustering_keys(spec: Dict[str, Any]) -> Dict[str, str]:
    structural_elements = spec.get("structural", {}).get("elements", [])
    composition = spec.get("structural", {}).get("composition", {})
    visual = spec.get("visual", {})
    semantic = spec.get("semantic", {})

    def first_anchor(role: str) -> str:
        for element in structural_elements:
            if element.get("role") == role:
                return str(element.get("anchor") or "none")
        return "none"

    def group_main_anchor() -> str:
        groups = [e for e in structural_elements if e.get("role") == "group"]
        if not groups:
            return "none"
        winner = max(groups, key=lambda e: float(e.get("bbox", [0, 0, 0, 0])[2]) * float(e.get("bbox", [0, 0, 0, 0])[3]))
        return str(winner.get("anchor") or "none")

    product_main = next((e for e in structural_elements if e.get("role") == "product_main"), None)
    product_anchor = str(product_main.get("anchor")) if product_main else "none"
    product_view = str(product_main.get("product_view")) if product_main else "none"

    structural_key = (
        f"{composition.get('archetype', 'no_focus')}__"
        f"{product_anchor}__"
        f"{product_view}__"
        f"{group_main_anchor()}__"
        f"{first_anchor('brand_logo')}__"
        f"{first_anchor('trust_mark')}__"
        f"{first_anchor('promo_offer')}"
    )

    palette = visual.get("palette", {})
    background = visual.get("background", {})
    visual_key = (
        f"bg:{background.get('type', 'solid')}__"
        f"tone:{palette.get('tone', 'medium')}__"
        f"sat:{palette.get('saturation', 'moderate')}__"
        f"temp:{palette.get('temperature', 'neutral')}__"
        f"density:{composition.get('density', 'medium')}"
    )

    semantic_key = f"cat:{semantic.get('product_category', 'other')}"
    full_key = f"{structural_key} | {visual_key} | {semantic_key}"

    return {
        "structural_key": structural_key,
        "visual_key": visual_key,
        "semantic_key": semantic_key,
        "full_key": full_key,
    }
