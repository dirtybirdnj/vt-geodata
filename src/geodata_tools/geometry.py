"""
Geometry operations for geographic data processing.
"""

from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union
from typing import List, Dict, Any, Optional


def simplify_geometry(geom, tolerance: float, preserve_topology: bool = True):
    """Simplify geometry using Douglas-Peucker algorithm."""
    return geom.simplify(tolerance, preserve_topology=preserve_topology)


def merge_features(features: List[Dict[str, Any]]) -> Any:
    """Merge multiple GeoJSON features into a single geometry."""
    geoms = []
    for feature in features:
        geom = shape(feature['geometry'])
        if geom.is_valid and not geom.is_empty:
            geoms.append(geom)
    return unary_union(geoms) if geoms else None


def cut_features_from_polygon(
    base_polygon,
    cut_features: List[Dict[str, Any]],
    min_area: float = 0.000001
) -> Any:
    """
    Cut feature geometries from a base polygon.

    Args:
        base_polygon: Shapely geometry to cut from
        cut_features: List of GeoJSON features whose geometries will be cut
        min_area: Minimum intersection area to include in cut

    Returns:
        Base polygon with cut areas removed
    """
    cut_geoms = []
    for feature in cut_features:
        geom = shape(feature['geometry'])
        if geom.intersects(base_polygon):
            intersection = geom.intersection(base_polygon)
            if not intersection.is_empty and intersection.area > min_area:
                cut_geoms.append(intersection)

    if not cut_geoms:
        return base_polygon

    cuts_union = unary_union(cut_geoms)
    result = base_polygon.difference(cuts_union)

    # Clean up GeometryCollection results
    if result.geom_type == 'GeometryCollection':
        polys = [g for g in result.geoms
                 if g.geom_type in ('Polygon', 'MultiPolygon') and g.area > min_area]
        result = unary_union(polys) if polys else base_polygon

    return result


def identify_islands(
    features: List[Dict[str, Any]],
    water_polygon,
    island_towns: Optional[List[str]] = None,
    max_island_area: float = 0.001,
    min_boundary_in_water: float = 0.8
) -> List[Dict[str, Any]]:
    """
    Identify island geometries from town features.

    Args:
        features: GeoJSON features (towns)
        water_polygon: Water body polygon
        island_towns: List of town names that are entirely islands
        max_island_area: Max area for auto-detected island parts
        min_boundary_in_water: Min fraction of boundary touching water

    Returns:
        List of dicts with 'geom', 'town', 'properties' for each island
    """
    island_towns = island_towns or []
    water_buffered = water_polygon.buffer(0.001)
    islands = []

    for feature in features:
        props = feature['properties']
        name = props.get('NAME', props.get('name', 'Unknown'))
        geom = shape(feature['geometry'])

        # Entire town is an island
        if name in island_towns:
            islands.append({
                'geom': geom,
                'town': name,
                'properties': props,
            })
            continue

        # Check MultiPolygon parts for small islands
        if geom.geom_type == 'MultiPolygon' and geom.intersects(water_polygon):
            for part in geom.geoms:
                if part.area < max_island_area:
                    # Check if mostly surrounded by water
                    if water_buffered.contains(part) or water_polygon.contains(part.centroid):
                        try:
                            boundary_in_water = part.boundary.intersection(water_buffered)
                            if boundary_in_water.length / part.boundary.length > min_boundary_in_water:
                                islands.append({
                                    'geom': part,
                                    'town': name,
                                    'properties': props,
                                })
                        except:
                            pass

    return islands


def count_vertices(geom) -> int:
    """Count total vertices in a geometry."""
    if geom.is_empty:
        return 0
    if geom.geom_type == 'Polygon':
        count = len(geom.exterior.coords)
        for interior in geom.interiors:
            count += len(interior.coords)
        return count
    elif geom.geom_type == 'MultiPolygon':
        return sum(count_vertices(poly) for poly in geom.geoms)
    elif geom.geom_type in ('LineString', 'LinearRing'):
        return len(geom.coords)
    elif geom.geom_type == 'MultiLineString':
        return sum(len(line.coords) for line in geom.geoms)
    return 0
