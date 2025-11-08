#!/usr/bin/env python3
"""
Categorize water features into distinct datasets:
1. Big Lake (Lake Champlain main body)
2. Rivers/Streams (linear features)
3. Small Lakes/Ponds (tiny specks)
"""

import json
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape


def calculate_elongation_ratio(geometry):
    """
    Calculate elongation ratio to identify rivers/streams.
    Ratio of length to width - higher values = more elongated (rivers).
    """
    bounds = geometry.bounds
    width = bounds[2] - bounds[0]  # max_x - min_x
    height = bounds[3] - bounds[1]  # max_y - min_y

    if width == 0 or height == 0:
        return 0

    # Return the ratio of longer side to shorter side
    return max(width, height) / min(width, height)


def categorize_champlain_water(output_dir: str = 'docs/json'):
    """
    Load Census TIGER water data and categorize into three datasets.
    """
    print("\n" + "=" * 60)
    print("🌊 Lake Champlain Water Categorization")
    print("=" * 60)

    # Load water data from the 4 counties
    counties = {
        '50013': 'Grand Isle',
        '50007': 'Chittenden',
        '50011': 'Franklin',
        '50001': 'Addison'
    }

    all_water = []
    for fips, name in counties.items():
        print(f"  Loading {name} County water...")
        url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
        gdf = gpd.read_file(url)
        all_water.append(gdf)

    # Combine all water features
    water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))
    print(f"  Combined: {len(water)} total water features")

    if water.crs != 'EPSG:4326':
        water = water.to_crs('EPSG:4326')

    # Calculate area in square kilometers (approximate)
    water['area_sqkm'] = water.geometry.area * 111 * 111

    # Calculate elongation ratio for identifying rivers
    water['elongation'] = water.geometry.apply(calculate_elongation_ratio)

    # Categorization thresholds
    BIG_LAKE_THRESHOLD = 100  # sq km - anything this big is the main lake
    UNNAMED_LARGE_THRESHOLD = 50  # sq km - unnamed features this big are likely lake parts
    SMALL_POND_THRESHOLD = 0.5  # sq km - anything smaller is a small pond
    RIVER_ELONGATION = 5  # ratio - features this elongated are rivers/streams

    # Category 1: Big Lake (Lake Champlain main body)
    # Include: Features >100 sq km OR named "Lk Champlain" OR unnamed >50 sq km
    big_lake = water[
        (water['area_sqkm'] >= BIG_LAKE_THRESHOLD) |
        (water['FULLNAME'].fillna('').str.contains('Champlain', case=False, na=False)) |
        ((water['FULLNAME'].isna()) & (water['area_sqkm'] >= UNNAMED_LARGE_THRESHOLD))
    ].copy()
    print(f"\n✅ Big Lake: {len(big_lake)} features")
    print(f"   Area range: {big_lake['area_sqkm'].min():.2f} - {big_lake['area_sqkm'].max():.2f} sq km")
    print(f"   Includes all 'Lk Champlain' named features")

    # Category 2: Rivers/Streams (elongated features)
    # Must be medium-sized and elongated
    rivers = water[
        (water['area_sqkm'] < BIG_LAKE_THRESHOLD) &
        (water['area_sqkm'] >= SMALL_POND_THRESHOLD) &
        (water['elongation'] >= RIVER_ELONGATION)
    ].copy()
    print(f"\n✅ Rivers/Streams: {len(rivers)} features")
    print(f"   Elongation range: {rivers['elongation'].min():.2f} - {rivers['elongation'].max():.2f}")

    # Category 3: Small Lakes/Ponds (small, compact features)
    # Everything that's not big lake or river
    small_ponds = water[
        ~water.index.isin(big_lake.index) &
        ~water.index.isin(rivers.index)
    ].copy()
    print(f"\n✅ Small Ponds/Lakes: {len(small_ponds)} features")
    print(f"   Area range: {small_ponds['area_sqkm'].min():.4f} - {small_ponds['area_sqkm'].max():.2f} sq km")

    # Apply manual edits if they exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    edits_file = output_path / 'categorized_water_edits.json'

    if edits_file.exists():
        print(f"\n🔧 Applying manual edits from {edits_file}...")
        with open(edits_file, 'r') as f:
            edits_data = json.load(f)

        edits = edits_data.get('edits', [])
        print(f"   Found {len(edits)} manual corrections")

        # Apply each edit
        moves_applied = 0
        for edit in edits:
            hydroid = edit['hydroid']
            from_cat = edit['from']
            to_cat = edit['to']

            # Normalize category names
            from_normalized = from_cat
            if 'Small Pond' in from_cat:
                from_normalized = 'Small Pond'
            elif 'River' in from_cat:
                from_normalized = 'River'
            elif 'Big Lake' in from_cat:
                from_normalized = 'Big Lake'

            to_normalized = to_cat
            if 'Small Pond' in to_cat:
                to_normalized = 'Small Pond'
            elif 'River' in to_cat:
                to_normalized = 'River'
            elif 'Big Lake' in to_cat:
                to_normalized = 'Big Lake'

            # Find the feature in the source category
            if from_normalized == 'Big Lake':
                from_df = big_lake
            elif from_normalized == 'River':
                from_df = rivers
            elif from_normalized == 'Small Pond':
                from_df = small_ponds
            else:
                print(f"   ⚠️  Unknown source category: {from_cat}")
                continue

            # Find the row with this HYDROID
            mask = from_df['HYDROID'] == hydroid
            if not mask.any():
                # Already moved or not found
                continue

            # Get the feature row
            feature_row = from_df[mask].copy()

            # Remove from source
            if from_normalized == 'Big Lake':
                big_lake = big_lake[~mask].copy()
            elif from_normalized == 'River':
                rivers = rivers[~mask].copy()
            elif from_normalized == 'Small Pond':
                small_ponds = small_ponds[~mask].copy()

            # Add to destination
            if to_normalized == 'Big Lake':
                big_lake = pd.concat([big_lake, feature_row], ignore_index=True)
            elif to_normalized == 'River':
                rivers = pd.concat([rivers, feature_row], ignore_index=True)
            elif to_normalized == 'Small Pond':
                small_ponds = pd.concat([small_ponds, feature_row], ignore_index=True)

            moves_applied += 1

        print(f"   ✓ Applied {moves_applied} corrections")
        print(f"\n📊 After manual edits:")
        print(f"   Big Lake: {len(big_lake)} features")
        print(f"   Rivers: {len(rivers)} features")
        print(f"   Small Ponds: {len(small_ponds)} features")

    categories = {
        'champlain_big_lake.json': {
            'data': big_lake,
            'name': 'Lake Champlain - Main Body',
            'description': 'Large lake features (>100 sq km)'
        },
        'champlain_rivers.json': {
            'data': rivers,
            'name': 'Lake Champlain - Rivers & Streams',
            'description': 'Elongated water features (rivers, streams, channels)'
        },
        'champlain_small_ponds.json': {
            'data': small_ponds,
            'name': 'Lake Champlain Region - Small Ponds & Lakes',
            'description': 'Small water bodies and ponds'
        }
    }

    for filename, category in categories.items():
        gdf = category['data']

        # Convert to GeoJSON
        geojson = json.loads(gdf.to_json())

        # Add metadata
        output = {
            'type': 'FeatureCollection',
            'metadata': {
                'name': category['name'],
                'description': category['description'],
                'features_count': len(gdf),
                'source': 'US Census TIGER/Line 2022',
                'counties': ['Grand Isle', 'Chittenden', 'Franklin', 'Addison'],
                'total_area_sqkm': float(gdf['area_sqkm'].sum()),
                'avg_area_sqkm': float(gdf['area_sqkm'].mean()),
                'thresholds': {
                    'big_lake_min': BIG_LAKE_THRESHOLD,
                    'unnamed_large_min': UNNAMED_LARGE_THRESHOLD,
                    'small_pond_max': SMALL_POND_THRESHOLD,
                    'river_elongation_min': RIVER_ELONGATION
                }
            },
            'features': geojson['features']
        }

        # Add area and elongation to each feature's properties
        for i, feature in enumerate(output['features']):
            feature['properties']['area_sqkm'] = float(gdf.iloc[i]['area_sqkm'])
            feature['properties']['elongation'] = float(gdf.iloc[i]['elongation'])

        # Save
        output_file = output_path / filename
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"   Saved: {filename}")

    print("\n" + "=" * 60)
    print("✅ Water categorization complete!")
    print("=" * 60)
    print(f"\n📂 Files saved to {output_dir}/")
    print("   - champlain_big_lake.json")
    print("   - champlain_rivers.json")
    print("   - champlain_small_ponds.json")


def main():
    categorize_champlain_water()


if __name__ == '__main__':
    main()
