#!/usr/bin/env python3
"""
Generate viewer configs for per-county road data.
"""

import json
from pathlib import Path

# County info with approximate map centers
COUNTIES = {
    'addison': {'name': 'Addison', 'center': [44.05, -73.15], 'zoom': 10},
    'bennington': {'name': 'Bennington', 'center': [43.0, -73.1], 'zoom': 10},
    'caledonia': {'name': 'Caledonia', 'center': [44.4, -72.1], 'zoom': 10},
    'chittenden': {'name': 'Chittenden', 'center': [44.45, -73.1], 'zoom': 10},
    'essex': {'name': 'Essex', 'center': [44.7, -71.7], 'zoom': 10},
    'franklin': {'name': 'Franklin', 'center': [44.85, -72.9], 'zoom': 10},
    'grand_isle': {'name': 'Grand Isle', 'center': [44.75, -73.3], 'zoom': 11},
    'lamoille': {'name': 'Lamoille', 'center': [44.6, -72.6], 'zoom': 10},
    'orange': {'name': 'Orange', 'center': [44.0, -72.35], 'zoom': 10},
    'orleans': {'name': 'Orleans', 'center': [44.8, -72.2], 'zoom': 10},
    'rutland': {'name': 'Rutland', 'center': [43.55, -72.95], 'zoom': 10},
    'washington': {'name': 'Washington', 'center': [44.25, -72.55], 'zoom': 10},
    'windham': {'name': 'Windham', 'center': [43.0, -72.6], 'zoom': 10},
    'windsor': {'name': 'Windsor', 'center': [43.55, -72.45], 'zoom': 10},
}

def generate_county_config(county_key: str, county_info: dict) -> dict:
    """Generate a viewer config for a county's roads."""
    return {
        "id": f"{county_key}_roads",
        "version": "1.0",
        "title": f"{county_info['name']} County Roads",
        "description": f"All roads in {county_info['name']} County from Census TIGER/Line 2023",

        "map": {
            "center": county_info['center'],
            "zoom": county_info['zoom'],
            "tiles": "CartoDB"
        },

        "ui": {
            "colorScheme": "#e65100",
            "infoBox": {
                "width": "350px",
                "content": {
                    "subtitle": f"Road network for {county_info['name']} County",
                    "stats": [],
                    "footer": "Data: US Census TIGER/Line 2023"
                }
            }
        },

        "layers": [
            {
                "id": "local_roads",
                "name": "Local Roads",
                "source": f"../json/roads/{county_key}_roads.json",
                "zIndex": 1,
                "style": {
                    "type": "colorMap",
                    "property": "MTFCC",
                    "colorMap": {
                        "S1100": "#d32f2f",  # Interstate - red
                        "S1200": "#ff9800",  # Highway - orange
                        "S1400": "#666666",  # Local - gray
                        "S1500": "#8d6e63",  # Trail - brown
                        "S1630": "#9c27b0",  # Ramp - purple
                        "S1640": "#607d8b",  # Service - blue-gray
                        "S1730": "#bdbdbd",  # Alley - light gray
                        "S1740": "#a5d6a7",  # Private - light green
                        "S1780": "#90a4ae",  # Parking - gray
                        "S1820": "#4caf50"   # Bike - green
                    },
                    "color": "#666666",
                    "weight": 1.5,
                    "opacity": 0.8
                },
                "tooltip": {
                    "fields": ["FULLNAME", "MTFCC"],
                    "aliases": ["Road:", "Type:"]
                }
            }
        ],

        "features": {
            "clickToSelect": {"enabled": False},
            "jsonDisplay": {"enabled": False},
            "layerControl": {"enabled": False}
        },

        "metadata": {
            "dataSources": ["US Census TIGER/Line Roads 2023"],
            "tags": ["roads", "county", county_info['name'].lower(), "transportation"]
        }
    }


def main():
    """Generate configs for all counties."""
    output_dir = Path(__file__).parent.parent / 'docs' / 'viewer' / 'configs'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating county road configs...")

    for county_key, county_info in COUNTIES.items():
        config = generate_county_config(county_key, county_info)
        output_path = output_dir / f"{county_key}_roads.json"

        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"  Created: {county_key}_roads.json")

    print(f"\nGenerated {len(COUNTIES)} county road configs")


if __name__ == '__main__':
    main()
