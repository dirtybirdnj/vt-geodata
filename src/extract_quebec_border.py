#!/usr/bin/env python3
"""
Extract Quebec MRCs (regional county municipalities) near the Vermont border.
Converts from shapefile to GeoJSON and filters to the border region.
"""

import json
import os
import shapefile

# Vermont's northern border is roughly at 45.0°N
# We'll filter Quebec MRCs that extend south of 45.5°N (buffer zone)
SOUTH_LATITUDE_FILTER = 45.5

def read_shapefile_to_geojson(shp_path):
    """Read shapefile and convert to GeoJSON features."""
    sf = shapefile.Reader(shp_path)
    fields = [field[0] for field in sf.fields[1:]]  # Skip DeletionFlag

    features = []
    for shaperec in sf.shapeRecords():
        # Get geometry
        geom = shaperec.shape.__geo_interface__

        # Get properties
        props = dict(zip(fields, shaperec.record))

        features.append({
            'type': 'Feature',
            'properties': props,
            'geometry': geom
        })

    return {
        'type': 'FeatureCollection',
        'features': features
    }

def transform_coords(coords, from_crs='nad83'):
    """
    Transform coordinates from Quebec Lambert to WGS84.
    Quebec data is typically in NAD83 / Quebec Lambert (EPSG:32198).
    This is a simplified transformation - may have slight offset.
    """
    try:
        from pyproj import Transformer
        transformer = Transformer.from_crs("EPSG:32198", "EPSG:4326", always_xy=True)

        if isinstance(coords[0], (int, float)):
            # Single point
            return list(transformer.transform(coords[0], coords[1]))
        else:
            # List of coords
            return [transform_coords(c, from_crs) for c in coords]
    except ImportError:
        # Fallback: assume already in WGS84-ish coords
        return coords

def transform_geometry(geom):
    """Transform geometry coordinates."""
    if geom['type'] == 'Polygon':
        geom['coordinates'] = [transform_coords(ring) for ring in geom['coordinates']]
    elif geom['type'] == 'MultiPolygon':
        geom['coordinates'] = [[transform_coords(ring) for ring in poly] for poly in geom['coordinates']]
    return geom

def get_bounds(geometry):
    """Get the bounding box of a geometry."""
    def extract_coords(coords):
        if isinstance(coords[0], (int, float)):
            return [coords]
        result = []
        for c in coords:
            result.extend(extract_coords(c))
        return result

    all_coords = extract_coords(geometry['coordinates'])
    lons = [c[0] for c in all_coords]
    lats = [c[1] for c in all_coords]

    return {
        'min_lon': min(lons),
        'max_lon': max(lons),
        'min_lat': min(lats),
        'max_lat': max(lats)
    }

def main():
    # Paths
    mrc_shp = 'data/quebec_admin/Bdat/SHP/mrc_s.shp'
    mrc_geojson_border = 'docs/json/quebec_border_mrc.json'

    print("Reading Quebec MRC shapefile...")
    data = read_shapefile_to_geojson(mrc_shp)
    print(f"  Read {len(data['features'])} MRC features")

    # Check if coordinates need transformation
    sample_bounds = get_bounds(data['features'][0]['geometry'])
    needs_transform = abs(sample_bounds['min_lon']) > 180 or abs(sample_bounds['min_lat']) > 90

    if needs_transform:
        print("Transforming coordinates from Quebec Lambert to WGS84...")
        try:
            from pyproj import Transformer
            for feat in data['features']:
                feat['geometry'] = transform_geometry(feat['geometry'])
            print("  Transformation complete")
        except ImportError:
            print("  WARNING: pyproj not available, coordinates may be incorrect!")

    # Filter to border region
    print(f"\nFiltering to MRCs south of {SOUTH_LATITUDE_FILTER}°N...")
    border_features = []
    for feat in data['features']:
        bounds = get_bounds(feat['geometry'])
        if bounds['min_lat'] < SOUTH_LATITUDE_FILTER:
            # This feature extends into the border region
            border_features.append(feat)
            props = feat['properties']
            name = props.get('MUS_NM_MRC', props.get('MRS_NM_MRC', 'Unknown'))
            print(f"  Including: {name} (south to {bounds['min_lat']:.2f}°N)")

    output = {
        'type': 'FeatureCollection',
        'features': border_features
    }

    # Write output
    print(f"\nWriting {len(border_features)} border MRCs...")
    with open(mrc_geojson_border, 'w') as f:
        json.dump(output, f)

    size_kb = os.path.getsize(mrc_geojson_border) / 1024
    print(f"Output: {mrc_geojson_border} ({size_kb:.1f} KB)")

if __name__ == '__main__':
    main()
