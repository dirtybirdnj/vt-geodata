"""
Color utilities for map styling.
"""

import hashlib
from typing import Dict, Tuple, Optional


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """
    Convert HSL to hex color.

    Args:
        h: Hue (0-360)
        s: Saturation (0-100)
        l: Lightness (0-100)

    Returns:
        Hex color string (e.g., '#ff5500')
    """
    s = s / 100
    l = l / 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)

    return f'#{r:02x}{g:02x}{b:02x}'


# Predefined regional color palettes
REGION_PALETTES = {
    'quebec': {'base_hue': (30, 15), 'lightness_range': (88, 96), 'saturation': 12},
    'ny': {'base_hue': (210, 20), 'lightness_range': (88, 95), 'saturation': 10},
    'nh': {'base_hue': (0, 0), 'lightness_range': (88, 95), 'saturation': 0},
    'ma': {'base_hue': (35, 18), 'lightness_range': (87, 94), 'saturation': 15},
    'me': {'base_hue': (150, 15), 'lightness_range': (88, 95), 'saturation': 10},
}


def get_feature_color(
    name: str,
    palette: Optional[Dict] = None,
    region: Optional[str] = None
) -> str:
    """
    Generate a consistent color for a feature based on its name.

    Uses MD5 hash for deterministic pseudo-random variation.

    Args:
        name: Feature name (used for hash)
        palette: Color palette dict with base_hue, lightness_range, saturation
        region: Region key to look up in REGION_PALETTES

    Returns:
        Hex color string
    """
    if palette is None:
        palette = REGION_PALETTES.get(region, REGION_PALETTES['nh'])

    # Hash name for consistent pseudo-random value
    hash_val = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    normalized = (hash_val % 1000) / 1000.0

    # Calculate lightness
    l_min, l_max = palette['lightness_range']
    lightness = l_min + (l_max - l_min) * normalized

    # Calculate hue with variation
    base_h, h_range = palette['base_hue']
    hue = base_h + (h_range * (normalized - 0.5))

    return hsl_to_hex(hue, palette['saturation'], lightness)


# Vermont county color map
VT_COUNTY_COLORS = {
    'Addison': '#66bb6a',
    'Bennington': '#42a5f5',
    'Caledonia': '#ab47bc',
    'Chittenden': '#ef5350',
    'Essex': '#ffa726',
    'Franklin': '#26c6da',
    'Grand Isle': '#7e57c2',
    'Lamoille': '#ec407a',
    'Orange': '#5c6bc0',
    'Orleans': '#9ccc65',
    'Rutland': '#29b6f6',
    'Washington': '#ff7043',
    'Windham': '#26a69a',
    'Windsor': '#ffd54f',
}
