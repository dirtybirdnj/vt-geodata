#!/usr/bin/env python3
"""
Export geospatial data to GeoJSON format.
Converts shapefiles to clean JSON with styling metadata.
"""

import json
import random
from pathlib import Path
import geopandas as gpd


def generate_random_color():
    """Generate a random hex color."""
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return f'#{r:02x}{g:02x}{b:02x}'


def calculate_centroid(geometry):
    """Calculate the centroid of a geometry and return as [lon, lat]."""
    centroid = geometry.centroid
    return [centroid.x, centroid.y]


def export_vt_border(output_path: str = 'docs/json/vt_border.json'):
    """
    Export Vermont state boundary to GeoJSON.
    """
    print("\n🗺️  Exporting Vermont Border...")

    # Download VT state boundary from Census
    url = "https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip"
    states = gpd.read_file(url)
    vt = states[states['STUSPS'] == 'VT'].copy()

    if vt.crs != 'EPSG:4326':
        vt = vt.to_crs('EPSG:4326')

    # Convert to GeoJSON dict
    geojson = json.loads(vt.to_json())

    # Add metadata
    output = {
        'type': 'FeatureCollection',
        'metadata': {
            'name': 'Vermont State Boundary',
            'source': 'US Census TIGER/Line 2023',
            'features_count': len(geojson['features'])
        },
        'features': geojson['features']
    }

    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Saved: {output_path}")
    print(f"   Features: {len(output['features'])}")


def export_vt_counties(output_path: str = 'docs/json/vt_counties.json'):
    """
    Export Vermont counties to GeoJSON with random colors and centroids.
    """
    print("\n🎨 Exporting Vermont Counties...")

    # Download VT counties from Census
    url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
    counties = gpd.read_file(url)
    vt_counties = counties[counties['STATEFP'] == '50'].copy()

    if vt_counties.crs != 'EPSG:4326':
        vt_counties = vt_counties.to_crs('EPSG:4326')

    # Sort by county name for consistent output
    vt_counties = vt_counties.sort_values('NAME')

    # Add styling properties
    features = []
    for idx, row in vt_counties.iterrows():
        # Calculate centroid for label placement
        centroid = calculate_centroid(row.geometry)

        # Generate random color
        color = generate_random_color()

        # Create feature with enhanced properties
        feature = {
            'type': 'Feature',
            'properties': {
                'name': row['NAME'],
                'fips': row['GEOID'],
                'state_fips': row['STATEFP'],
                'county_fips': row['COUNTYFP'],
                'color': color,
                'centroid': centroid
            },
            'geometry': json.loads(gpd.GeoSeries([row.geometry]).to_json())['features'][0]['geometry']
        }
        features.append(feature)

    # Create output with metadata
    output = {
        'type': 'FeatureCollection',
        'metadata': {
            'name': 'Vermont Counties',
            'source': 'US Census TIGER/Line 2023',
            'features_count': len(features),
            'counties': [f['properties']['name'] for f in features]
        },
        'features': features
    }

    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Saved: {output_path}")
    print(f"   Counties: {len(features)}")
    print(f"   Each county has: name, fips, color, centroid")


def main():
    """Main function to export all GeoJSON files."""
    print("=" * 60)
    print("🚀 Vermont GeoData → JSON Exporter")
    print("=" * 60)

    # Export border
    export_vt_border()

    # Export counties with colors
    export_vt_counties()

    print("\n" + "=" * 60)
    print("✅ JSON export complete!")
    print("=" * 60)
    print("\n📂 Files saved to docs/json/")
    print("   - vt_border.json")
    print("   - vt_counties.json")


if __name__ == '__main__':
    main()
