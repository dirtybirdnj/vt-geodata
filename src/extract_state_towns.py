#!/usr/bin/env python3
"""
Extract town/township boundaries from Census TIGER county subdivision data.
Filters to counties we have in our existing county GeoJSON files.
"""

import json
import os
import shapefile

# FIPS codes for counties in our existing files
# NY: 22 counties from ny_counties_grey.json
NY_COUNTIES = {
    '001': 'Albany',
    '009': 'Clinton',
    '017': 'Chenango',
    '019': 'Columbia',
    '021': 'Delaware',
    '025': 'Dutchess',
    '031': 'Essex',
    '035': 'Fulton',
    '039': 'Greene',
    '041': 'Hamilton',
    '043': 'Herkimer',
    '045': 'Jefferson',
    '049': 'Lewis',
    '057': 'Montgomery',
    '065': 'Oneida',
    '073': 'Otsego',
    '083': 'Rensselaer',
    '091': 'Saratoga',
    '093': 'Schenectady',
    '095': 'Schoharie',
    '089': 'St. Lawrence',
    '111': 'Ulster',
    '113': 'Warren',
    '115': 'Washington',
}

# NH: All 10 counties
NH_COUNTIES = {
    '001': 'Belknap',
    '003': 'Carroll',
    '005': 'Cheshire',
    '007': 'Coos',
    '009': 'Grafton',
    '011': 'Hillsborough',
    '013': 'Merrimack',
    '015': 'Rockingham',
    '017': 'Strafford',
    '019': 'Sullivan',
}

# MA: Only Berkshire and Franklin border VT
MA_COUNTIES = {
    '003': 'Berkshire',
    '011': 'Franklin',
}


def extract_towns(shapefile_path, county_fips_dict, state_fips, output_path):
    """Extract towns from counties we care about."""
    sf = shapefile.Reader(shapefile_path)
    fields = [f[0] for f in sf.fields[1:]]

    features = []
    for sr in sf.shapeRecords():
        rec = dict(zip(fields, sr.record))
        county_fips = rec.get('COUNTYFP', '')

        if county_fips in county_fips_dict:
            # Convert shapefile geometry to GeoJSON
            geom = sr.shape.__geo_interface__

            props = {
                'NAME': rec.get('NAME', ''),
                'NAMELSAD': rec.get('NAMELSAD', ''),
                'GEOID': rec.get('GEOID', ''),
                'STATEFP': rec.get('STATEFP', ''),
                'COUNTYFP': county_fips,
                'county_name': county_fips_dict[county_fips],
            }

            features.append({
                'type': 'Feature',
                'properties': props,
                'geometry': geom
            })

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    return len(features)


def main():
    print("Extracting town boundaries...")

    # NY towns
    print("\nNY towns from 22 counties...")
    count = extract_towns(
        'data/tiger_cousub/tl_2023_36_cousub.shp',
        NY_COUNTIES,
        '36',
        'docs/json/ny_towns.json'
    )
    size = os.path.getsize('docs/json/ny_towns.json') / 1024
    print(f"  Extracted {count} towns ({size:.0f} KB)")

    # NH towns
    print("\nNH towns from all 10 counties...")
    count = extract_towns(
        'data/tiger_cousub/tl_2023_33_cousub.shp',
        NH_COUNTIES,
        '33',
        'docs/json/nh_towns.json'
    )
    size = os.path.getsize('docs/json/nh_towns.json') / 1024
    print(f"  Extracted {count} towns ({size:.0f} KB)")

    # MA towns
    print("\nMA towns from Berkshire & Franklin counties...")
    count = extract_towns(
        'data/tiger_cousub/tl_2023_25_cousub.shp',
        MA_COUNTIES,
        '25',
        'docs/json/ma_towns.json'
    )
    size = os.path.getsize('docs/json/ma_towns.json') / 1024
    print(f"  Extracted {count} towns ({size:.0f} KB)")

    print("\nDone!")


if __name__ == '__main__':
    main()
