"""
GeoJSON file operations.
"""

import json
from typing import Dict, Any, List, Optional
from shapely.geometry import shape, mapping


def load_geojson(filepath: str) -> Dict[str, Any]:
    """Load a GeoJSON file."""
    with open(filepath) as f:
        return json.load(f)


def save_geojson(
    data: Dict[str, Any],
    filepath: str,
    indent: Optional[int] = None
) -> None:
    """Save data to a GeoJSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def create_feature(
    geometry,
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a GeoJSON feature from a Shapely geometry."""
    return {
        "type": "Feature",
        "properties": properties or {},
        "geometry": mapping(geometry)
    }


def create_feature_collection(
    features: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Create a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": features
    }


def filter_features(
    geojson: Dict[str, Any],
    predicate
) -> List[Dict[str, Any]]:
    """Filter features by a predicate function."""
    return [f for f in geojson['features'] if predicate(f)]


def get_bounds(geojson: Dict[str, Any]) -> tuple:
    """Get bounding box of all features: (min_lon, min_lat, max_lon, max_lat)."""
    from shapely.ops import unary_union
    geoms = [shape(f['geometry']) for f in geojson['features']]
    combined = unary_union(geoms)
    return combined.bounds
