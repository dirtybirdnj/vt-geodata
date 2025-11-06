"""
Explore and visualize downloaded geospatial datasets
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from pathlib import Path
from typing import List, Dict, Optional
import json


def find_shapefiles(data_dir: str = 'data/raw') -> List[Path]:
    """
    Find all shapefiles in the data directory

    Args:
        data_dir: Directory to search

    Returns:
        List of shapefile paths
    """
    data_path = Path(data_dir)
    return sorted(data_path.rglob("*.shp"))


def inspect_shapefile(shapefile_path: Path) -> Dict:
    """
    Load and inspect a shapefile, returning metadata

    Args:
        shapefile_path: Path to shapefile

    Returns:
        Dictionary with shapefile metadata
    """
    try:
        gdf = gpd.read_file(shapefile_path)

        metadata = {
            'path': str(shapefile_path),
            'name': shapefile_path.stem,
            'crs': str(gdf.crs),
            'features': len(gdf),
            'geometry_types': gdf.geometry.type.unique().tolist(),
            'bounds': gdf.total_bounds.tolist(),  # [minx, miny, maxx, maxy]
            'columns': gdf.columns.tolist(),
            'sample_attributes': {}
        }

        # Get sample values for non-geometry columns
        for col in gdf.columns:
            if col != 'geometry':
                unique_vals = gdf[col].dropna().unique()
                if len(unique_vals) <= 10:
                    metadata['sample_attributes'][col] = unique_vals.tolist()
                else:
                    metadata['sample_attributes'][col] = f"{len(unique_vals)} unique values"

        return metadata

    except Exception as e:
        return {
            'path': str(shapefile_path),
            'error': str(e)
        }


def create_overview_map(shapefiles: List[Path], output_path: str = 'output/overview_map.html'):
    """
    Create an interactive Folium map showing all datasets

    Args:
        shapefiles: List of shapefile paths
        output_path: Where to save the HTML map
    """
    print("Creating interactive overview map...")

    # Center on Vermont
    m = folium.Map(
        location=[44.0, -72.7],  # Vermont center
        zoom_start=8,
        tiles='OpenStreetMap'
    )

    colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'lightred',
              'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink']

    for idx, shp_path in enumerate(shapefiles):
        try:
            print(f"  Adding {shp_path.stem}...")
            gdf = gpd.read_file(shp_path)

            # Reproject to WGS84 for Folium
            if gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')

            # Add to map with unique color
            color = colors[idx % len(colors)]

            # Simplify for web display
            gdf_simple = gdf.simplify(0.001)

            folium.GeoJson(
                gdf_simple,
                name=shp_path.stem,
                style_function=lambda x, color=color: {
                    'fillColor': color,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.3
                },
                tooltip=folium.GeoJsonTooltip(fields=gdf.columns[:5].tolist())
            ).add_to(m)

        except Exception as e:
            print(f"  ✗ Error adding {shp_path.stem}: {e}")

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save map
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output))
    print(f"\n✓ Interactive map saved to {output_path}")


def create_comparison_plot(shapefiles: List[Path], output_path: str = 'output/comparison.png'):
    """
    Create a matplotlib comparison plot of all datasets

    Args:
        shapefiles: List of shapefile paths
        output_path: Where to save the plot
    """
    print("\nCreating static comparison plot...")

    n_files = len(shapefiles)
    cols = 2
    rows = (n_files + 1) // 2

    fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 6))
    if rows == 1:
        axes = axes.reshape(1, -1)

    for idx, shp_path in enumerate(shapefiles):
        row = idx // cols
        col = idx % cols
        ax = axes[row, col]

        try:
            gdf = gpd.read_file(shp_path)

            # Plot
            gdf.plot(ax=ax, edgecolor='blue', facecolor='lightblue', linewidth=0.5)

            ax.set_title(f"{shp_path.stem}\n{len(gdf)} features, {gdf.crs}")
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')

            # Add bounds info
            bounds = gdf.total_bounds
            ax.text(0.02, 0.98, f"Bounds:\n{bounds[0]:.2f}, {bounds[1]:.2f}\n{bounds[2]:.2f}, {bounds[3]:.2f}",
                   transform=ax.transAxes, fontsize=8, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        except Exception as e:
            ax.text(0.5, 0.5, f"Error loading\n{shp_path.stem}\n{e}",
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(shp_path.stem)

    # Hide unused subplots
    for idx in range(n_files, rows * cols):
        row = idx // cols
        col = idx % cols
        axes[row, col].axis('off')

    plt.tight_layout()

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"✓ Comparison plot saved to {output_path}")


def explore_datasets(data_dir: str = 'data/raw', create_maps: bool = True):
    """
    Main exploration function - inspect all datasets and create visualizations

    Args:
        data_dir: Directory containing raw data
        create_maps: Whether to create visualization maps
    """
    print("=" * 60)
    print("VT GeoData Explorer")
    print("=" * 60)
    print()

    # Find all shapefiles
    shapefiles = find_shapefiles(data_dir)

    if not shapefiles:
        print(f"No shapefiles found in {data_dir}")
        print("Run 'python src/download.py' first to download datasets")
        return

    print(f"Found {len(shapefiles)} shapefile(s)\n")

    # Inspect each file
    all_metadata = []
    for shp_path in shapefiles:
        print(f"\n{'=' * 60}")
        print(f"Inspecting: {shp_path.stem}")
        print(f"{'=' * 60}")

        metadata = inspect_shapefile(shp_path)

        if 'error' in metadata:
            print(f"✗ Error: {metadata['error']}")
        else:
            print(f"CRS: {metadata['crs']}")
            print(f"Features: {metadata['features']}")
            print(f"Geometry types: {', '.join(metadata['geometry_types'])}")
            print(f"Bounds: {metadata['bounds']}")
            print(f"\nAttributes:")
            for col, vals in metadata['sample_attributes'].items():
                if isinstance(vals, list):
                    print(f"  {col}: {vals[:5]}")
                else:
                    print(f"  {col}: {vals}")

        all_metadata.append(metadata)

    # Save metadata to JSON
    metadata_path = Path('data/processed/metadata.json')
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    print(f"\n✓ Metadata saved to {metadata_path}")

    # Create visualizations
    if create_maps and shapefiles:
        print(f"\n{'=' * 60}")
        print("Creating visualizations...")
        print(f"{'=' * 60}")

        try:
            create_overview_map(shapefiles)
        except Exception as e:
            print(f"✗ Error creating overview map: {e}")

        try:
            create_comparison_plot(shapefiles)
        except Exception as e:
            print(f"✗ Error creating comparison plot: {e}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Explore Vermont geodata')
    parser.add_argument('--data-dir', default='data/raw',
                       help='Input directory with raw data')
    parser.add_argument('--no-maps', action='store_true',
                       help='Skip map generation')

    args = parser.parse_args()

    explore_datasets(args.data_dir, create_maps=not args.no_maps)
