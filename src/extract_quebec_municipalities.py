#!/usr/bin/env python3
"""
Extract Quebec municipality boundaries from MRCs we have in our border file.
"""

import json
import os
import shapefile

# MRC codes from our quebec_border_mrc.json file
# Focus on MRCs near the VT border
VT_BORDER_MRCS = {
    '30': 'Le Granit',
    '41': 'Le Haut-Saint-François',
    '44': 'Coaticook',
    '45': 'Memphrémagog',
    '46': 'Brome-Missisquoi',
    '56': 'Le Haut-Richelieu',
    '68': 'Les Jardins-de-Napierville',
    '69': 'Le Haut-Saint-Laurent',
}

# Extended set including Montreal corridor
ALL_BORDER_MRCS = {
    '30': 'Le Granit',
    '41': 'Le Haut-Saint-François',
    '42': 'Le Val-Saint-François',
    '43': 'Sherbrooke',
    '44': 'Coaticook',
    '45': 'Memphrémagog',
    '46': 'Brome-Missisquoi',
    '47': 'La Haute-Yamaska',
    '48': 'Acton',
    '54': 'Les Maskoutains',
    '55': 'Rouville',
    '56': 'Le Haut-Richelieu',
    '57': 'La Vallée-du-Richelieu',
    '58': 'Longueuil',
    '66': 'Montréal',
    '67': 'Roussillon',
    '68': 'Les Jardins-de-Napierville',
    '69': 'Le Haut-Saint-Laurent',
    '70': 'Beauharnois-Salaberry',
    '71': 'Vaudreuil-Soulanges',
    '72': 'Deux-Montagnes',
    '81': 'Gatineau',
    '82': "Les Collines-de-l'Outaouais",
    '84': 'Pontiac',
}


def extract_municipalities(shapefile_path, mrc_codes, output_path):
    """Extract municipalities from specified MRCs."""
    sf = shapefile.Reader(shapefile_path, encoding='latin-1')
    fields = [f[0] for f in sf.fields[1:]]

    features = []
    for sr in sf.shapeRecords():
        rec = dict(zip(fields, sr.record))
        mrc_code = rec.get('MUS_CO_MRC', '')

        if mrc_code in mrc_codes:
            geom = sr.shape.__geo_interface__

            props = {
                'NAME': rec.get('MUS_NM_MUN', ''),
                'MRC_CODE': mrc_code,
                'MRC_NAME': rec.get('MUS_NM_MRC', ''),
                'REGION': rec.get('MUS_NM_REG', ''),
                'TYPE': rec.get('MUS_DE_IND', ''),
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
    shapefile_path = 'data/quebec_municipalities/Bdat/SHP/munic_s.shp'

    print("Extracting Quebec municipality boundaries...")

    # VT border municipalities only
    print("\nVT border MRCs (8 MRCs closest to Vermont)...")
    count = extract_municipalities(
        shapefile_path,
        VT_BORDER_MRCS,
        'docs/json/quebec_municipalities.json'
    )
    size = os.path.getsize('docs/json/quebec_municipalities.json') / 1024
    print(f"  Extracted {count} municipalities ({size:.0f} KB)")

    # All border MRCs (extended)
    print("\nAll border MRCs (24 MRCs in border file)...")
    count = extract_municipalities(
        shapefile_path,
        ALL_BORDER_MRCS,
        'docs/json/quebec_municipalities_extended.json'
    )
    size = os.path.getsize('docs/json/quebec_municipalities_extended.json') / 1024
    print(f"  Extracted {count} municipalities ({size:.0f} KB)")

    print("\nDone!")


if __name__ == '__main__':
    main()
