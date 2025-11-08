#!/usr/bin/env python3
"""
Apply manual categorization edits to water datasets.

This script takes the categorized_water_edits.json file created by the
interactive editor and applies those changes to generate corrected datasets.
"""

import json
from pathlib import Path


def apply_edits(edits_file: str = 'docs/json/categorized_water_edits.json',
                output_dir: str = 'docs/json'):
    """
    Apply manual edits to water categorization datasets.
    """
    print("\n" + "=" * 60)
    print("🔧 Applying Manual Water Categorization Edits")
    print("=" * 60)

    # Load the edits file
    edits_path = Path(edits_file)
    if not edits_path.exists():
        print(f"❌ Error: Edits file not found: {edits_file}")
        print("   Please save your edits from the interactive editor first.")
        return

    with open(edits_path, 'r') as f:
        edits_data = json.load(f)

    edits = edits_data['edits']
    print(f"\n📝 Loaded {len(edits)} edits from {edits_file}")
    print(f"   Created: {edits_data['metadata']['created']}")

    # Load the three category datasets
    output_path = Path(output_dir)

    datasets = {
        'Big Lake': 'champlain_big_lake.json',
        'River': 'champlain_rivers.json',
        'Small Pond': 'champlain_small_ponds.json'
    }

    # Load all datasets
    data = {}
    for category, filename in datasets.items():
        filepath = output_path / filename
        with open(filepath, 'r') as f:
            data[category] = json.load(f)
        print(f"   Loaded {data[category]['metadata']['features_count']} features from {filename}")

    # Create a mapping of HYDROID to feature for easy lookup
    feature_map = {}
    for category, dataset in data.items():
        for feature in dataset['features']:
            hydroid = feature['properties']['HYDROID']
            feature_map[hydroid] = {
                'feature': feature,
                'current_category': category,
                'dataset': dataset
            }

    # Apply edits
    print(f"\n🔄 Applying edits...")
    moves = {}  # Track features to move between datasets

    for edit in edits:
        hydroid = edit['hydroid']
        from_cat = edit['from']
        to_cat = edit['to']

        if hydroid not in feature_map:
            print(f"   ⚠️  Warning: HYDROID {hydroid} not found, skipping")
            continue

        # Track the move
        if hydroid not in moves:
            moves[hydroid] = {
                'feature': feature_map[hydroid]['feature'],
                'from': from_cat,
                'to': to_cat,
                'name': edit['name']
            }
        else:
            # Update to the latest destination
            moves[hydroid]['to'] = to_cat

    # Execute the moves
    print(f"\n📦 Moving {len(moves)} features between categories...")

    for hydroid, move_info in moves.items():
        from_cat = move_info['from']
        to_cat = move_info['to']
        feature = move_info['feature']
        name = move_info['name']

        # Remove from source dataset
        data[from_cat]['features'] = [
            f for f in data[from_cat]['features']
            if f['properties']['HYDROID'] != hydroid
        ]

        # Add to destination dataset
        data[to_cat]['features'].append(feature)

        print(f"   ✓ {name or 'Unnamed'} ({hydroid}): {from_cat} → {to_cat}")

    # Update metadata and save
    print(f"\n💾 Saving corrected datasets...")

    for category, filename in datasets.items():
        dataset = data[category]

        # Update metadata
        features = dataset['features']
        dataset['metadata']['features_count'] = len(features)

        # Recalculate area stats
        if len(features) > 0:
            areas = [f['properties']['area_sqkm'] for f in features]
            dataset['metadata']['total_area_sqkm'] = sum(areas)
            dataset['metadata']['avg_area_sqkm'] = sum(areas) / len(areas)
        else:
            dataset['metadata']['total_area_sqkm'] = 0
            dataset['metadata']['avg_area_sqkm'] = 0

        # Add edit metadata
        dataset['metadata']['manual_edits_applied'] = {
            'edits_file': str(edits_file),
            'edits_count': len([m for m in moves.values() if m['to'] == category or m['from'] == category]),
            'applied_at': edits_data['metadata']['created']
        }

        # Save
        filepath = output_path / filename
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)

        print(f"   ✓ {filename}: {len(features)} features")

    print("\n" + "=" * 60)
    print("✅ Edits applied successfully!")
    print("=" * 60)
    print(f"\n📊 Final counts:")
    for category, filename in datasets.items():
        count = data[category]['metadata']['features_count']
        print(f"   {category}: {count} features")


def main():
    apply_edits()


if __name__ == '__main__':
    main()
