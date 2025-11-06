"""
Export processed geodata to SVG format for pen plotting
"""

import geopandas as gpd
import svgwrite
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, MultiLineString
from shapely.affinity import scale, translate
from typing import Tuple, List
import json


class SVGPlotterExporter:
    """
    Export GeoDataFrames to SVG optimized for pen plotters
    """

    def __init__(self, width: float = 297, height: float = 210, units: str = 'mm'):
        """
        Initialize exporter with paper size

        Args:
            width: Paper width (default A4 landscape)
            height: Paper height (default A4 landscape)
            units: Units (mm, in, px)
        """
        self.width = width
        self.height = height
        self.units = units
        self.margin = 10  # margin in units

    def calculate_transform(self, gdf: gpd.GeoDataFrame) -> Tuple[float, float, float]:
        """
        Calculate scale and translation to fit geometry in bounds

        Args:
            gdf: Input GeoDataFrame

        Returns:
            (scale_factor, offset_x, offset_y)
        """
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]

        geo_width = bounds[2] - bounds[0]
        geo_height = bounds[3] - bounds[1]

        # Calculate scale to fit in drawable area
        drawable_width = self.width - 2 * self.margin
        drawable_height = self.height - 2 * self.margin

        scale_x = drawable_width / geo_width
        scale_y = drawable_height / geo_height
        scale_factor = min(scale_x, scale_y)

        # Calculate offsets to center
        scaled_width = geo_width * scale_factor
        scaled_height = geo_height * scale_factor

        offset_x = self.margin + (drawable_width - scaled_width) / 2 - bounds[0] * scale_factor
        offset_y = self.margin + (drawable_height - scaled_height) / 2 - bounds[1] * scale_factor

        return scale_factor, offset_x, offset_y

    def geometry_to_svg_path(self, geom, scale_factor: float, offset_x: float, offset_y: float) -> List[str]:
        """
        Convert Shapely geometry to SVG path commands

        Args:
            geom: Shapely geometry
            scale_factor: Coordinate scale factor
            offset_x: X offset
            offset_y: Y offset

        Returns:
            List of SVG path strings
        """
        paths = []

        def transform_coords(x, y):
            """Transform geographic coordinates to SVG coordinates"""
            svg_x = x * scale_factor + offset_x
            # Flip Y axis (SVG origin is top-left)
            svg_y = self.height - (y * scale_factor + offset_y)
            return svg_x, svg_y

        def polygon_to_path(poly):
            """Convert a single polygon to SVG path"""
            if poly.is_empty:
                return None

            # Exterior ring
            coords = list(poly.exterior.coords)
            if not coords:
                return None

            path_data = []
            x, y = transform_coords(*coords[0])
            path_data.append(f"M {x:.3f} {y:.3f}")

            for coord in coords[1:]:
                x, y = transform_coords(*coord)
                path_data.append(f"L {x:.3f} {y:.3f}")

            path_data.append("Z")  # Close path

            # Interior rings (holes)
            for interior in poly.interiors:
                coords = list(interior.coords)
                if coords:
                    x, y = transform_coords(*coords[0])
                    path_data.append(f"M {x:.3f} {y:.3f}")
                    for coord in coords[1:]:
                        x, y = transform_coords(*coord)
                        path_data.append(f"L {x:.3f} {y:.3f}")
                    path_data.append("Z")

            return " ".join(path_data)

        def linestring_to_path(line):
            """Convert linestring to SVG path"""
            if line.is_empty:
                return None

            coords = list(line.coords)
            if not coords:
                return None

            path_data = []
            x, y = transform_coords(*coords[0])
            path_data.append(f"M {x:.3f} {y:.3f}")

            for coord in coords[1:]:
                x, y = transform_coords(*coord)
                path_data.append(f"L {x:.3f} {y:.3f}")

            return " ".join(path_data)

        # Handle different geometry types
        if isinstance(geom, Polygon):
            path = polygon_to_path(geom)
            if path:
                paths.append(path)

        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                path = polygon_to_path(poly)
                if path:
                    paths.append(path)

        elif isinstance(geom, LineString):
            path = linestring_to_path(geom)
            if path:
                paths.append(path)

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                path = linestring_to_path(line)
                if path:
                    paths.append(path)

        return paths

    def export_layer(self, gdf: gpd.GeoDataFrame, output_path: str,
                    stroke_color: str = 'black', stroke_width: float = 0.3,
                    fill: str = 'none'):
        """
        Export a single layer to SVG

        Args:
            gdf: GeoDataFrame to export
            output_path: Output SVG file path
            stroke_color: Stroke color
            stroke_width: Stroke width in units
            fill: Fill color (use 'none' for pen plotting)
        """
        # Calculate transformation
        scale_factor, offset_x, offset_y = self.calculate_transform(gdf)

        # Create SVG drawing
        dwg = svgwrite.Drawing(
            output_path,
            size=(f"{self.width}{self.units}", f"{self.height}{self.units}"),
            profile='tiny'  # SVG Tiny profile for compatibility
        )

        # Add each geometry
        for idx, row in gdf.iterrows():
            geom = row.geometry
            paths = self.geometry_to_svg_path(geom, scale_factor, offset_x, offset_y)

            for path_data in paths:
                dwg.add(dwg.path(
                    d=path_data,
                    stroke=stroke_color,
                    stroke_width=stroke_width,
                    fill=fill,
                    stroke_linejoin='round',
                    stroke_linecap='round'
                ))

        # Save
        dwg.save()
        print(f"✓ Exported {len(gdf)} features to {output_path}")

    def export_multi_layer(self, layers: dict, output_path: str):
        """
        Export multiple layers to a single SVG with different colors

        Args:
            layers: Dictionary of {name: (gdf, color, stroke_width)}
            output_path: Output SVG file path
        """
        # Combine all layers to calculate bounds
        all_gdfs = [gdf for gdf, _, _ in layers.values()]
        combined = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))

        # Calculate transformation
        scale_factor, offset_x, offset_y = self.calculate_transform(combined)

        # Create SVG drawing
        dwg = svgwrite.Drawing(
            output_path,
            size=(f"{self.width}{self.units}", f"{self.height}{self.units}"),
            profile='tiny'
        )

        # Add each layer
        for layer_name, (gdf, color, stroke_width) in layers.items():
            print(f"  Adding layer: {layer_name}")
            group = dwg.g(id=layer_name.replace(' ', '_'))

            for idx, row in gdf.iterrows():
                geom = row.geometry
                paths = self.geometry_to_svg_path(geom, scale_factor, offset_x, offset_y)

                for path_data in paths:
                    group.add(dwg.path(
                        d=path_data,
                        stroke=color,
                        stroke_width=stroke_width,
                        fill='none',
                        stroke_linejoin='round',
                        stroke_linecap='round'
                    ))

            dwg.add(group)

        dwg.save()
        print(f"✓ Exported multi-layer SVG to {output_path}")


def export_all_layers(data_dir: str = 'data/processed', output_dir: str = 'output'):
    """
    Export all processed layers to SVG

    Args:
        data_dir: Directory with processed GeoJSON files
        output_dir: Output directory for SVG files
    """
    print("=" * 60)
    print("VT GeoData SVG Exporter")
    print("=" * 60)
    print()

    data_path = Path(data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all GeoJSON files
    geojson_files = list(data_path.glob("*.geojson"))

    if not geojson_files:
        print(f"No processed data found in {data_dir}")
        print("Run 'python src/process.py' first")
        return

    print(f"Found {len(geojson_files)} processed layer(s)\n")

    # Create exporter (A4 landscape, 297x210mm)
    exporter = SVGPlotterExporter(width=297, height=210, units='mm')

    # Export each layer individually
    print("Exporting individual layers...")
    layers = {}

    for geojson_file in geojson_files:
        layer_name = geojson_file.stem
        print(f"\n{layer_name}:")

        try:
            gdf = gpd.read_file(geojson_file)

            # Determine color and stroke based on layer type
            if 'boundary' in layer_name:
                color = 'black'
                stroke_width = 0.5
            elif 'champlain' in layer_name:
                color = 'blue'
                stroke_width = 0.3
            elif 'water' in layer_name:
                color = 'blue'
                stroke_width = 0.2
            else:
                color = 'black'
                stroke_width = 0.3

            # Export single layer
            svg_path = output_path / f"{layer_name}.svg"
            exporter.export_layer(gdf, str(svg_path), stroke_color=color, stroke_width=stroke_width)

            # Store for combined export
            layers[layer_name] = (gdf, color, stroke_width)

        except Exception as e:
            print(f"✗ Error exporting {layer_name}: {e}")

    # Export combined map
    if layers:
        print("\nExporting combined map...")
        combined_path = output_path / "vermont_combined.svg"
        exporter.export_multi_layer(layers, str(combined_path))

    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"\nSVG files saved to {output_dir}/")
    print("\nPen plotter tips:")
    print("- Files use 0.2-0.5mm stroke widths")
    print("- No fills, only strokes (ideal for pen plotting)")
    print("- SVG Tiny profile for compatibility")
    print("- A4 landscape (297x210mm)")


if __name__ == '__main__':
    import argparse
    import pandas as pd

    parser = argparse.ArgumentParser(description='Export geodata to SVG')
    parser.add_argument('--data-dir', default='data/processed',
                       help='Input directory with processed data')
    parser.add_argument('--output-dir', default='output',
                       help='Output directory for SVG files')
    parser.add_argument('--width', type=float, default=297,
                       help='SVG width in mm (default: 297)')
    parser.add_argument('--height', type=float, default=210,
                       help='SVG height in mm (default: 210)')

    args = parser.parse_args()

    export_all_layers(args.data_dir, args.output_dir)
