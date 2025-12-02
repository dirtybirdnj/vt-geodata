"""
SVG generation from GeoJSON data.
"""

from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import shape
from shapely.ops import unary_union

from .geometry import simplify_geometry, count_vertices
from .colors import get_feature_color, VT_COUNTY_COLORS


def project_coords(
    lon: float,
    lat: float,
    bounds: Tuple[float, float, float, float],
    width: float,
    height: float
) -> Tuple[float, float]:
    """Project lon/lat to SVG coordinates."""
    min_lon, min_lat, max_lon, max_lat = bounds
    x = (lon - min_lon) / (max_lon - min_lon) * width
    y = height - (lat - min_lat) / (max_lat - min_lat) * height
    return x, y


def geometry_to_path(
    geom,
    bounds: Tuple[float, float, float, float],
    width: float,
    height: float
) -> List[str]:
    """Convert a Shapely geometry to SVG path data strings."""
    paths = []

    def coords_to_path(coords, close=False):
        if len(coords) < 2:
            return ""
        points = [project_coords(c[0], c[1], bounds, width, height) for c in coords]
        d = f"M {points[0][0]:.2f},{points[0][1]:.2f}"
        for p in points[1:]:
            d += f" L {p[0]:.2f},{p[1]:.2f}"
        if close:
            d += " Z"
        return d

    if geom.geom_type == 'Polygon':
        paths.append(coords_to_path(geom.exterior.coords, close=True))
        for interior in geom.interiors:
            paths.append(coords_to_path(interior.coords, close=True))
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            paths.extend(geometry_to_path(poly, bounds, width, height))
    elif geom.geom_type == 'LineString':
        paths.append(coords_to_path(geom.coords, close=False))
    elif geom.geom_type == 'MultiLineString':
        for line in geom.geoms:
            paths.append(coords_to_path(line.coords, close=False))

    return paths


def generate_svg(
    layers: Dict[str, Dict[str, Any]],
    layer_styles: Dict[str, Dict[str, Any]],
    bounds: Tuple[float, float, float, float],
    width_in: float,
    height_in: float,
    tolerance: float,
    dpi: int = 72,
    title: str = "Map"
) -> Tuple[str, Dict[str, Any]]:
    """
    Generate SVG content from layers.

    Args:
        layers: Dict of layer_name -> GeoJSON data
        layer_styles: Dict of layer_name -> style config
        bounds: (min_lon, min_lat, max_lon, max_lat)
        width_in: Output width in inches
        height_in: Output height in inches
        tolerance: Simplification tolerance
        dpi: DPI for pixel calculation
        title: SVG title

    Returns:
        Tuple of (svg_content, stats)
    """
    width = width_in * dpi
    height = height_in * dpi

    total_original = 0
    total_simplified = 0

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <title>{title}</title>
  <rect width="100%" height="100%" fill="white"/>

'''

    for layer_name, layer_data in layers.items():
        style = layer_styles.get(layer_name, {})
        default_fill = style.get('fill', 'none')
        stroke = style.get('stroke', '#000000')
        stroke_width = style.get('stroke_width', 0.5)
        fill_opacity = style.get('fill_opacity', 1.0)
        color_map = style.get('color_map')
        region = style.get('region')
        merge = style.get('merge_features', False)

        svg += f'  <!-- Layer: {layer_name} -->\n'
        svg += f'  <g id="{layer_name}">\n'

        if merge:
            # Merge all features into one
            geoms = []
            for f in layer_data['features']:
                g = shape(f['geometry'])
                if g.is_valid and not g.is_empty:
                    geoms.append(g)
                    total_original += count_vertices(g)

            if geoms:
                merged = unary_union(geoms)
                simplified = simplify_geometry(merged, tolerance)
                total_simplified += count_vertices(simplified)

                paths = geometry_to_path(simplified, bounds, width, height)
                fill = default_fill or 'none'
                fill_style = f'fill="{fill}" fill-opacity="{fill_opacity}"' if fill != 'none' else 'fill="none"'

                for path_d in paths:
                    if path_d:
                        svg += f'    <path d="{path_d}" {fill_style} stroke="{stroke}" stroke-width="{stroke_width}"/>\n'
        else:
            for feature in layer_data['features']:
                geom = shape(feature['geometry'])
                total_original += count_vertices(geom)

                simplified = simplify_geometry(geom, tolerance)
                total_simplified += count_vertices(simplified)

                paths = geometry_to_path(simplified, bounds, width, height)
                props = feature.get('properties', {})
                name = props.get('NAME', props.get('name', 'Unknown'))

                # Determine fill color
                if color_map and 'county_name' in props:
                    fill = color_map.get(props['county_name'], default_fill or 'none')
                elif region:
                    fill = get_feature_color(name, region=region)
                else:
                    fill = default_fill or 'none'

                fill_style = f'fill="{fill}" fill-opacity="{fill_opacity}"' if fill != 'none' else 'fill="none"'

                for path_d in paths:
                    if path_d:
                        svg += f'    <path d="{path_d}" {fill_style} stroke="{stroke}" stroke-width="{stroke_width}"/>\n'

        svg += '  </g>\n\n'

    svg += '</svg>'

    stats = {
        'original_vertices': total_original,
        'simplified_vertices': total_simplified,
        'reduction_pct': (1 - total_simplified / total_original) * 100 if total_original > 0 else 0
    }

    return svg, stats
