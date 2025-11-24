#!/usr/bin/env python3
"""
Combine NY and VT Champlain TIGER HYDROIDs into single dataset
First-order data source for complete Lake Champlain water features
"""

import geopandas as gpd
import json
from pathlib import Path

def create_combined_champlain_hydroids(
    output_json='docs/json/champlain_tiger_hydroids_combined.json'
):
    """
    Combine NY and VT Champlain TIGER HYDROID datasets
    """
    print("=" * 70)
    print("COMBINED CHAMPLAIN TIGER HYDROIDS - First Order Data Source")
    print("=" * 70)

    # Load VT Champlain water
    print("\n1. Loading VT Champlain TIGER HYDROIDs...")
    with open('docs/json/vt_champlain_tiger_hydroids.json', 'r') as f:
        vt_data = json.load(f)

    vt_water = gpd.GeoDataFrame.from_features(vt_data['features'])
    vt_water.crs = 'EPSG:4326'
    vt_water['state'] = 'VT'
    print(f"   VT features: {len(vt_water)}")
    print(f"   VT area: {vt_data['metadata']['total_area_sqkm']:.2f} sq km")

    # Load NY Champlain water
    print("\n2. Loading NY Champlain TIGER HYDROIDs...")
    with open('docs/json/ny_champlain_tiger_hydroids.json', 'r') as f:
        ny_data = json.load(f)

    ny_water = gpd.GeoDataFrame.from_features(ny_data['features'])
    ny_water.crs = 'EPSG:4326'
    ny_water['state'] = 'NY'
    print(f"   NY features: {len(ny_water)}")
    print(f"   NY area: {ny_data['metadata']['total_area_sqkm']:.2f} sq km")

    # Combine datasets
    print("\n3. Combining VT and NY water features...")
    combined_water = gpd.GeoDataFrame(
        pd.concat([vt_water, ny_water], ignore_index=True),
        crs='EPSG:4326'
    )

    total_features = len(combined_water)
    total_area = combined_water['area_sqkm'].sum()

    print(f"   Total features: {total_features}")
    print(f"   Total area: {total_area:.2f} sq km")

    # Feature breakdown by state
    vt_count = len(combined_water[combined_water['state'] == 'VT'])
    ny_count = len(combined_water[combined_water['state'] == 'NY'])
    print(f"\n   Breakdown:")
    print(f"   VT: {vt_count} features ({vt_count/total_features*100:.1f}%)")
    print(f"   NY: {ny_count} features ({ny_count/total_features*100:.1f}%)")

    # Export to GeoJSON
    print("\n4. Exporting to GeoJSON...")
    output_geojson = json.loads(combined_water.to_json())
    output_geojson['metadata'] = {
        'description': 'Combined NY and VT Champlain TIGER HYDROIDs',
        'total_features': total_features,
        'total_area_sqkm': float(total_area),
        'vt_features': vt_count,
        'ny_features': ny_count,
        'vt_area_sqkm': float(vt_data['metadata']['total_area_sqkm']),
        'ny_area_sqkm': float(ny_data['metadata']['total_area_sqkm']),
        'source': 'US Census TIGER/Line Shapefiles 2022',
        'method': 'Combined VT and NY Champlain TIGER HYDROID datasets',
        'vt_hydroids_count': len(vt_data['metadata']['hydroids']),
        'ny_hydroids_count': len(ny_data['metadata']['hydroids'])
    }

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(output_geojson, f, indent=2)

    file_size = Path(output_json).stat().st_size / 1024
    print(f"   ✓ Saved to {output_json}")
    print(f"   File size: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print(f"\nCombined dataset: {total_features} water features")
    print(f"  • VT: {vt_count} features ({vt_data['metadata']['total_area_sqkm']:.2f} sq km)")
    print(f"  • NY: {ny_count} features ({ny_data['metadata']['total_area_sqkm']:.2f} sq km)")
    print(f"  • Total: {total_area:.2f} sq km")

    return output_json, combined_water


if __name__ == '__main__':
    import pandas as pd
    create_combined_champlain_hydroids()
