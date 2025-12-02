#!/usr/bin/env python3
"""
Rebuild all data files for the Vermont print maps (12x18 and 12x24).

This script regenerates all upstream data from Census TIGER sources:
1. Vermont towns with water cutouts
2. Combined Lake Champlain (VT + NY)
3. Surrounding counties (NY, NH, MA)
4. Vermont boundary

Run this script whenever you need to refresh the data from upstream sources
or after making corrections to the water cutouts.

Usage:
    python src/rebuild_print_maps.py [--all] [--counties] [--champlain] [--towns]
"""

import subprocess
import sys
from pathlib import Path
import argparse

# Script dependencies for each data type
REBUILD_SCRIPTS = {
    'counties': {
        'script': 'src/get_regional_counties.py',
        'description': 'Surrounding counties (NY, NH, MA)',
        'outputs': [
            'docs/json/ny_champlain_counties.json',
            'docs/json/ny_adjacent_counties.json',
            'docs/json/ny_regional_counties.json',
            'docs/json/nh_counties.json',
            'docs/json/ma_counties.json',
            'docs/json/surrounding_counties.json',
        ]
    },
    'champlain': {
        'script': 'src/create_combined_champlain.py',
        'description': 'Combined Lake Champlain (VT + NY)',
        'outputs': [
            'docs/json/lake_champlain_combined.json',
            'docs/json/lake_champlain_combined_multi.json',
        ],
        'depends_on': [
            'docs/json/lake_champlain_water.json',
            'docs/json/ny_lake_champlain_water.json',
        ]
    },
    'towns': {
        'script': 'src/create_vt_towns_with_water_cutouts.py',
        'description': 'Vermont towns with water cutouts',
        'outputs': [
            'docs/json/vt_towns_with_water_cutouts.json',
        ]
    },
    'ny_champlain_water': {
        'script': 'src/get_ny_lake_champlain_data.py',
        'description': 'NY Lake Champlain water features',
        'outputs': [
            'docs/json/ny_lake_champlain_water.json',
        ]
    },
    'vt_champlain_hydroids': {
        'script': 'src/get_champlain_tiger_hydroids.py',
        'description': 'VT Lake Champlain TIGER HYDROIDs',
        'outputs': [
            'docs/json/lake_champlain_water.json',
            'docs/json/vt_champlain_tiger_hydroids.json',
        ]
    }
}

# Rebuild order matters - some scripts depend on others
FULL_REBUILD_ORDER = [
    'vt_champlain_hydroids',
    'ny_champlain_water',
    'champlain',
    'counties',
    'towns',
]


def run_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status"""
    print(f"\n{'='*70}")
    print(f"REBUILDING: {description}")
    print(f"Script: {script_path}")
    print('='*70)

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def check_outputs(outputs: list) -> bool:
    """Check if output files exist"""
    base_path = Path(__file__).parent.parent
    all_exist = True
    for output in outputs:
        path = base_path / output
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  ✓ {output} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {output} (MISSING)")
            all_exist = False
    return all_exist


def rebuild_all():
    """Rebuild all data files in correct order"""
    print("\n" + "="*70)
    print("FULL REBUILD - Vermont Print Maps Data")
    print("="*70)
    print("\nThis will regenerate all data from Census TIGER sources.")
    print("Rebuild order:", " -> ".join(FULL_REBUILD_ORDER))

    results = {}
    for name in FULL_REBUILD_ORDER:
        info = REBUILD_SCRIPTS[name]
        success = run_script(info['script'], info['description'])
        results[name] = success

        print(f"\nOutput files for {name}:")
        check_outputs(info['outputs'])

        if not success:
            print(f"\n⚠️  WARNING: {name} failed, continuing with next step...")

    # Summary
    print("\n" + "="*70)
    print("REBUILD SUMMARY")
    print("="*70)
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {REBUILD_SCRIPTS[name]['description']}")

    all_success = all(results.values())
    if all_success:
        print("\n✅ All rebuilds completed successfully!")
    else:
        print("\n⚠️  Some rebuilds failed. Check output above for details.")

    return all_success


def rebuild_specific(targets: list):
    """Rebuild specific data types"""
    print("\n" + "="*70)
    print(f"REBUILDING: {', '.join(targets)}")
    print("="*70)

    results = {}
    for name in targets:
        if name not in REBUILD_SCRIPTS:
            print(f"\n⚠️  Unknown target: {name}")
            print(f"   Available targets: {', '.join(REBUILD_SCRIPTS.keys())}")
            continue

        info = REBUILD_SCRIPTS[name]
        success = run_script(info['script'], info['description'])
        results[name] = success

        print(f"\nOutput files for {name}:")
        check_outputs(info['outputs'])

    return all(results.values())


def list_configs():
    """List the print map configs that use this data"""
    configs_dir = Path(__file__).parent.parent / 'docs/viewer/configs'
    print("\n" + "="*70)
    print("PRINT MAP CONFIGURATIONS")
    print("="*70)

    print("\n12x18 Vermont Map (2:3 aspect ratio):")
    print("  Config: docs/viewer/configs/vermont_12x18.json")
    print("  URL: map-viewer.html?config=vermont_12x18")
    print("  Uses:")
    print("    - vt_towns_with_water_cutouts.json")
    print("    - lake_champlain_combined.json")
    print("    - surrounding_counties.json")
    print("    - vermont_boundary_detailed.json")

    print("\n12x24 Lake Champlain Map (1:2 aspect ratio):")
    print("  Config: docs/viewer/configs/lake_champlain_12x24.json")
    print("  URL: map-viewer.html?config=lake_champlain_12x24")
    print("  Uses:")
    print("    - lake_champlain_combined.json")
    print("    - vt_towns_with_water_cutouts.json")
    print("    - ny_champlain_counties.json")

    print("\nRegional View (updated):")
    print("  Config: docs/viewer/configs/vermont_with_islands.json")
    print("  URL: map-viewer.html?config=vermont_with_islands")
    print("  Uses:")
    print("    - surrounding_counties.json")
    print("    - lake_champlain_combined.json")
    print("    - vermont_boundary_detailed.json")


def main():
    parser = argparse.ArgumentParser(
        description='Rebuild data files for Vermont print maps'
    )
    parser.add_argument('--all', action='store_true',
                       help='Rebuild all data files')
    parser.add_argument('--counties', action='store_true',
                       help='Rebuild surrounding counties')
    parser.add_argument('--champlain', action='store_true',
                       help='Rebuild combined Lake Champlain')
    parser.add_argument('--towns', action='store_true',
                       help='Rebuild VT towns with water cutouts')
    parser.add_argument('--list', action='store_true',
                       help='List available configs and their data dependencies')

    args = parser.parse_args()

    if args.list:
        list_configs()
        return

    if args.all:
        success = rebuild_all()
        sys.exit(0 if success else 1)

    targets = []
    if args.counties:
        targets.append('counties')
    if args.champlain:
        targets.append('champlain')
    if args.towns:
        targets.append('towns')

    if not targets:
        print("No rebuild target specified.")
        print("\nUsage:")
        print("  python src/rebuild_print_maps.py --all       # Rebuild everything")
        print("  python src/rebuild_print_maps.py --counties  # Just counties")
        print("  python src/rebuild_print_maps.py --champlain # Just Lake Champlain")
        print("  python src/rebuild_print_maps.py --towns     # Just VT towns")
        print("  python src/rebuild_print_maps.py --list      # Show configs")
        parser.print_help()
        return

    success = rebuild_specific(targets)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
