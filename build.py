#!/usr/bin/env python3
"""
Build script for VT Geodata project
Downloads first-order data sources and generates maps

This keeps large source data and comprehensive maps out of git while
allowing them to be regenerated locally when needed.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def build_essential_maps():
    """Generate essential maps that are committed to git"""
    print("=" * 70)
    print("BUILDING ESSENTIAL MAPS (committed to git)")
    print("=" * 70)

    # Import generation functions
    from categorize_water import categorize_champlain_water
    from get_ny_lake_champlain_data import main as get_ny_data
    from generate_champlain_ny_vt import create_champlain_ny_vt_map, create_champlain_ny_vt_vector_map

    print("\n1. Categorizing VT water features...")
    categorize_champlain_water()

    print("\n2. Getting NY Lake Champlain data...")
    get_ny_data()

    print("\n3. Generating Lake Champlain NY & VT combined maps...")
    create_champlain_ny_vt_map()
    create_champlain_ny_vt_vector_map()

    print("\n" + "=" * 70)
    print("✅ ESSENTIAL MAPS BUILT")
    print("=" * 70)


def build_comprehensive_maps():
    """Generate comprehensive reference maps (NOT committed to git)"""
    print("\n" + "=" * 70)
    print("BUILDING COMPREHENSIVE MAPS (local only, not committed)")
    print("=" * 70)

    from generate_comparison_maps import (
        create_ny_census_all_water_map,
        create_vt_census_all_water_map
    )
    from generate_vector_only_maps import (
        create_ny_census_water_vector,
        create_vt_census_water_vector
    )

    print("\n1. Generating NY census water maps (all 62 counties)...")
    create_ny_census_all_water_map('docs/ny_census_water_all.html')

    print("\n2. Generating VT census water maps (all 14 counties)...")
    create_vt_census_all_water_map('docs/vt_census_water_all.html')

    print("\n3. Generating vector versions...")
    create_ny_census_water_vector('docs/ny_census_water_all_vector.html')
    create_vt_census_water_vector('docs/vt_census_water_all_vector.html')

    print("\n" + "=" * 70)
    print("✅ COMPREHENSIVE MAPS BUILT")
    print("=" * 70)
    print("Note: These large files (50+ MB) are excluded from git")
    print("They are available locally for reference and debugging")


def main():
    """Main build process"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Build VT Geodata maps',
        epilog='Run with no arguments to build all maps'
    )
    parser.add_argument(
        '--essential-only',
        action='store_true',
        help='Build only essential maps (committed to git)'
    )
    parser.add_argument(
        '--comprehensive-only',
        action='store_true',
        help='Build only comprehensive maps (local reference, not committed)'
    )

    args = parser.parse_args()

    try:
        if args.essential_only:
            build_essential_maps()
        elif args.comprehensive_only:
            build_comprehensive_maps()
        else:
            # Build all maps
            build_essential_maps()
            build_comprehensive_maps()

        print("\n" + "=" * 70)
        print("🎉 BUILD COMPLETE!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
