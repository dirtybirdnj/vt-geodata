#!/usr/bin/env python3
"""
Check which JSON files contain specific HYDROIDs.
Usage: python check_hydroid_location.py HYDROID1 HYDROID2 ...
"""

import json
import sys
from pathlib import Path

def check_hydroid_locations(hydroids):
    """Check which category JSON files contain the given HYDROIDs."""

    files = {
        'Big Lake': 'docs/json/champlain_big_lake.json',
        'Rivers': 'docs/json/champlain_rivers.json',
        'Small Ponds': 'docs/json/champlain_small_ponds.json'
    }

    results = {}

    for category, filepath in files.items():
        with open(filepath, 'r') as f:
            data = json.load(f)

        for hydroid in hydroids:
            found = any(f['properties']['HYDROID'] == hydroid for f in data['features'])
            if found:
                if hydroid not in results:
                    results[hydroid] = []
                results[hydroid].append(category)

    # Print results
    print("\nHYDROID Locations:")
    print("=" * 60)

    for hydroid in hydroids:
        if hydroid in results:
            locations = ', '.join(results[hydroid])
            print(f"✓ {hydroid}: {locations}")
            if len(results[hydroid]) > 1:
                print(f"  ⚠️  WARNING: Found in multiple files (duplicate!)")
        else:
            print(f"✗ {hydroid}: NOT FOUND in any file")

    print("=" * 60)

    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_hydroid_location.py HYDROID1 HYDROID2 ...")
        sys.exit(1)

    hydroids = sys.argv[1:]
    check_hydroid_locations(hydroids)
