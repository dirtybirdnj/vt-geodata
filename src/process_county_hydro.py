#!/usr/bin/env python3
"""
Process county hydro data: create rivers/lakes datasets and punch holes in towns.

Usage:
    python process_county_hydro.py chittenden
    python process_county_hydro.py washington
"""

import os
import sys
import json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

# County FIPS codes for VT (state FIPS 50)
VT_COUNTIES = {
    'addison': '001',
    'bennington': '003',
    'caledonia': '005',
    'chittenden': '007',
    'essex': '009',
    'franklin': '011',
    'grand_isle': '013',
    'lamoille': '015',
    'orange': '017',
    'orleans': '019',
    'rutland': '021',
    'washington': '023',
    'windham': '025',
    'windsor': '027',
}

# Minimum area thresholds (in sq meters from AWATER field)
MIN_RIVER_AREA = 50000   # 0.05 sq km
MIN_LAKE_AREA = 50000    # 0.05 sq km


def load_shapefile_as_geojson(shp_path):
    """Convert shapefile to GeoJSON using ogr2ogr."""
    import subprocess
    import tempfile

    # Create temp file in /tmp with unique name
    temp_path = f"/tmp/ogr2ogr_{os.getpid()}_{os.path.basename(shp_path)}.json"

    try:
        # Remove if exists
        if os.path.exists(temp_path):
            os.remove(temp_path)

        result = subprocess.run([
            'ogr2ogr', '-f', 'GeoJSON', temp_path, shp_path
        ], check=True, capture_output=True, text=True)

        with open(temp_path) as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        print(f"ogr2ogr error: {e.stderr}")
        raise
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def categorize_water(feature):
    """Categorize water feature as river or lake based on name.
    Returns None for features that should be excluded (Lake Champlain, Memphremagog)."""
    props = feature.get('properties', {})
    name = (props.get('FULLNAME') or '').lower()

    # Exclude Lake Champlain and Memphremagog (handled separately)
    if 'champlain' in name or 'memphremagog' in name:
        return None

    # River indicators
    river_keywords = ['riv', 'river', 'brook', 'creek', 'stream', 'branch', 'run']
    for kw in river_keywords:
        if kw in name:
            return 'river'

    # Lake/pond indicators (or default for unnamed)
    return 'lake'


def process_county(county_name):
    """Process a single county's hydro data."""
    county_name = county_name.lower().replace(' ', '_')

    if county_name not in VT_COUNTIES:
        print(f"Unknown county: {county_name}")
        print(f"Available: {', '.join(sorted(VT_COUNTIES.keys()))}")
        return

    fips = VT_COUNTIES[county_name]
    county_title = county_name.replace('_', ' ').title()

    print(f"\n{'='*60}")
    print(f"Processing {county_title} County")
    print('='*60)

    # Check for water data
    water_dir = f"data/{county_name}_water"
    shp_file = f"{water_dir}/tl_2023_50{fips}_areawater.shp"

    if not os.path.exists(shp_file):
        print(f"Water data not found: {shp_file}")
        print(f"Download with: curl -L -o data/{county_name}_water.zip 'https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_50{fips}_areawater.zip'")
        return

    # Load water data
    print(f"Loading water data from {shp_file}...")
    water_data = load_shapefile_as_geojson(shp_file)
    print(f"  Found {len(water_data['features'])} total water features")

    # Filter and categorize
    rivers = []
    lakes = []

    for feature in water_data['features']:
        props = feature.get('properties', {})
        awater = props.get('AWATER', 0) or 0

        if awater < MIN_LAKE_AREA:
            continue

        # Add area in sq km
        area_sqkm = awater / 1_000_000
        props['area_sqkm'] = round(area_sqkm, 4)
        props['county'] = county_title

        category = categorize_water(feature)
        if category is None:
            # Excluded (Lake Champlain, etc.)
            continue

        props['category'] = category

        if category == 'river':
            rivers.append(feature)
        else:
            lakes.append(feature)

    print(f"  Rivers (>= {MIN_RIVER_AREA/1e6:.2f} sq km): {len(rivers)}")
    print(f"  Lakes/Ponds (>= {MIN_LAKE_AREA/1e6:.2f} sq km): {len(lakes)}")

    # Save separate datasets
    os.makedirs('docs/json', exist_ok=True)

    rivers_file = f"docs/json/{county_name}_rivers.json"
    lakes_file = f"docs/json/{county_name}_lakes.json"

    # Sort by area descending
    rivers.sort(key=lambda f: f['properties'].get('area_sqkm', 0), reverse=True)
    lakes.sort(key=lambda f: f['properties'].get('area_sqkm', 0), reverse=True)

    with open(rivers_file, 'w') as f:
        json.dump({'type': 'FeatureCollection', 'features': rivers}, f)
    print(f"  Saved: {rivers_file}")

    with open(lakes_file, 'w') as f:
        json.dump({'type': 'FeatureCollection', 'features': lakes}, f)
    print(f"  Saved: {lakes_file}")

    # Now punch holes in town shapes
    print(f"\nPunching holes in town shapes...")

    # Load VT towns
    towns_file = 'docs/json/vt_towns.json'
    if not os.path.exists(towns_file):
        print(f"  Towns file not found: {towns_file}")
        return

    with open(towns_file) as f:
        towns_data = json.load(f)

    # Filter to this county's towns
    county_towns = [
        f for f in towns_data['features']
        if f.get('properties', {}).get('county_name', '').lower() == county_title.lower()
    ]
    print(f"  Found {len(county_towns)} towns in {county_title} County")

    # Combine all water for hole punching
    all_water = rivers + lakes

    if not all_water:
        print("  No water features to punch")
        return

    # Create union of water geometries
    water_geoms = []
    for f in all_water:
        try:
            g = shape(f['geometry'])
            if g.is_valid and not g.is_empty:
                water_geoms.append(g)
        except Exception as e:
            print(f"  Warning: Invalid geometry - {e}")

    if not water_geoms:
        print("  No valid water geometries")
        return

    water_union = unary_union(water_geoms)
    print(f"  Created water union from {len(water_geoms)} features")

    # Punch holes in each town
    towns_with_holes = []
    holes_punched = 0

    for town in county_towns:
        props = town['properties'].copy()
        town_name = props.get('NAME', 'Unknown')

        try:
            town_geom = shape(town['geometry'])

            if town_geom.intersects(water_union):
                # Punch holes
                new_geom = town_geom.difference(water_union)

                if new_geom.is_empty:
                    # Town entirely covered by water (unlikely)
                    towns_with_holes.append(town)
                else:
                    props['water_cutout_applied'] = True
                    holes_punched += 1
                    towns_with_holes.append({
                        'type': 'Feature',
                        'properties': props,
                        'geometry': mapping(new_geom)
                    })
            else:
                props['water_cutout_applied'] = False
                towns_with_holes.append({
                    'type': 'Feature',
                    'properties': props,
                    'geometry': town['geometry']
                })
        except Exception as e:
            print(f"  Warning: Error processing {town_name} - {e}")
            towns_with_holes.append(town)

    print(f"  Punched holes in {holes_punched} towns")

    # Save towns with holes
    output_file = f"docs/json/{county_name}_towns_with_hydro_cutouts.json"
    with open(output_file, 'w') as f:
        json.dump({'type': 'FeatureCollection', 'features': towns_with_holes}, f)
    print(f"  Saved: {output_file}")

    # Print summary
    print(f"\n{'-'*60}")
    print("Rivers:")
    for r in rivers[:5]:
        name = r['properties'].get('FULLNAME') or 'unnamed'
        area = r['properties'].get('area_sqkm', 0)
        print(f"  {name}: {area:.2f} sq km")
    if len(rivers) > 5:
        print(f"  ... and {len(rivers) - 5} more")

    print("\nLakes/Ponds:")
    for l in lakes[:5]:
        name = l['properties'].get('FULLNAME') or 'unnamed'
        area = l['properties'].get('area_sqkm', 0)
        print(f"  {name}: {area:.2f} sq km")
    if len(lakes) > 5:
        print(f"  ... and {len(lakes) - 5} more")

    return {
        'county': county_title,
        'rivers_count': len(rivers),
        'lakes_count': len(lakes),
        'towns_processed': len(towns_with_holes),
        'holes_punched': holes_punched,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_county_hydro.py <county_name>")
        print(f"Available counties: {', '.join(sorted(VT_COUNTIES.keys()))}")
        sys.exit(1)

    for county in sys.argv[1:]:
        process_county(county)
