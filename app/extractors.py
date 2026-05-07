from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from skimage.color import deltaE_ciede2000, lab2rgb, rgb2lab


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


MAX_SIDE = 400
K_CLUSTERS = 8
KMEANS_N_INIT = 3
RANDOM_SEED = 42
DELTA_E_MERGE = 10.0
DELTA_E_ACCENT_MIN = 15.0
ACCENT_MIN_WEIGHT = 0.02
ACCENT_MAX_COUNT = 5


def _resize_for_palette(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGBA")
    w, h = rgb.size
    longest = max(w, h)
    if longest <= MAX_SIDE:
        return rgb
    scale = MAX_SIDE / float(longest)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return rgb.resize(new_size, Image.Resampling.LANCZOS)


def _lab_to_hex(lab_center: np.ndarray) -> str:
    lab = np.asarray(lab_center, dtype=np.float64).reshape(1, 1, 3)
    rgb = lab2rgb(lab)[0, 0]
    rgb_255 = tuple(int(round(v * 255.0)) for v in np.clip(rgb, 0.0, 1.0))
    return _rgb_to_hex(rgb_255)


def _merge_close_clusters(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = list(clusters)
    while len(merged) > 1:
        min_delta = None
        min_pair = None
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                delta = float(
                    deltaE_ciede2000(
                        merged[i]["center"].reshape(1, 1, 3),
                        merged[j]["center"].reshape(1, 1, 3),
                    )[0, 0]
                )
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    min_pair = (i, j)
        if min_delta is None or min_pair is None or min_delta >= DELTA_E_MERGE:
            break

        i, j = min_pair
        ci, cj = merged[i], merged[j]
        wi, wj = ci["weight"], cj["weight"]
        new_weight = wi + wj
        new_center = (ci["center"] * wi + cj["center"] * wj) / new_weight

        next_clusters: List[Dict[str, Any]] = []
        for idx, cluster in enumerate(merged):
            if idx in (i, j):
                continue
            next_clusters.append(cluster)
        next_clusters.append({"center": new_center, "weight": new_weight})
        merged = next_clusters
    return merged


def _accents_far_from_dominant(
    accents: List[Dict[str, Any]], dominant: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for accent in accents:
        min_delta = min(
            float(
                deltaE_ciede2000(
                    accent["center"].reshape(1, 1, 3),
                    dom["center"].reshape(1, 1, 3),
                )[0, 0]
            )
            for dom in dominant
        )
        if min_delta >= DELTA_E_ACCENT_MIN:
            filtered.append(accent)
    return filtered


def extract_palette(image: Image.Image) -> Dict[str, Any]:
    prepared = _resize_for_palette(image)
    pixels_rgba = np.asarray(prepared, dtype=np.uint8)

    if pixels_rgba.shape[-1] == 4:
        alpha = pixels_rgba[:, :, 3]
        rgb_pixels = pixels_rgba[:, :, :3][alpha >= 250]
    else:
        rgb_pixels = pixels_rgba.reshape(-1, 3)

    if rgb_pixels.size == 0:
        return {"dominant": ["#808080", "#808080", "#808080"], "accents": []}

    rgb_float = rgb_pixels.astype(np.float64) / 255.0
    lab_pixels = rgb2lab(rgb_float.reshape(-1, 1, 3)).reshape(-1, 3)

    n_samples = lab_pixels.shape[0]
    k = max(1, min(K_CLUSTERS, n_samples))
    kmeans = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=RANDOM_SEED)
    labels = kmeans.fit_predict(lab_pixels)

    counts = np.bincount(labels, minlength=k).astype(np.float64)
    weights = counts / counts.sum()
    clusters = [
        {"center": kmeans.cluster_centers_[i].astype(np.float64), "weight": float(weights[i])}
        for i in range(k)
        if counts[i] > 0
    ]

    clusters = _merge_close_clusters(clusters)
    clusters.sort(key=lambda c: c["weight"], reverse=True)

    dominant_clusters = clusters[:3]
    accent_candidates = [
        c for c in clusters[3:] if c["weight"] >= ACCENT_MIN_WEIGHT
    ][:ACCENT_MAX_COUNT]
    accents_clusters = _accents_far_from_dominant(accent_candidates, dominant_clusters)

    dominant_hex = [_lab_to_hex(c["center"]) for c in dominant_clusters]
    while len(dominant_hex) < 3:
        dominant_hex.append("#808080")
    accents_hex = [_lab_to_hex(c["center"]) for c in accents_clusters]

    return {"dominant": dominant_hex, "accents": accents_hex}


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
