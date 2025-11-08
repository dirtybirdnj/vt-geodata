#!/usr/bin/env python3
"""
Add edits to categorized_water_edits.json from a JSON input.
Usage: python add_edits_from_json.py edits.json
"""

import json
import sys
from pathlib import Path


def add_edits(new_edits_file, edits_file='docs/json/categorized_water_edits.json'):
    """Add new edits to the categorized_water_edits.json file."""

    # Load current edits
    with open(edits_file, 'r') as f:
        data = json.load(f)

    # Load new edits
    with open(new_edits_file, 'r') as f:
        new_edits = json.load(f)

    # Merge - deduplicate by HYDROID (keep latest)
    seen = {}
    for edit in data['edits']:
        seen[edit['hydroid']] = edit

    added = 0
    updated = 0
    for edit in new_edits:
        if edit['hydroid'] in seen:
            updated += 1
        else:
            added += 1
        seen[edit['hydroid']] = edit

    # Convert back to list
    data['edits'] = list(seen.values())
    data['metadata']['total_edits'] = len(data['edits'])

    # Update timestamp to latest edit
    if new_edits:
        latest_timestamp = max(e['timestamp'] for e in new_edits)
        data['metadata']['last_updated'] = latest_timestamp

    # Save
    with open(edits_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Added {added} new edits")
    print(f"✓ Updated {updated} existing edits")
    print(f"✓ Total edits: {len(data['edits'])}")

    return data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python add_edits_from_json.py new_edits.json")
        sys.exit(1)

    new_edits_file = sys.argv[1]
    add_edits(new_edits_file)
