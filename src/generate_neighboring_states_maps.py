#!/usr/bin/env python3
"""
Generate maps for neighboring states (NY, NH, MA)
Creates both regular and vector-only versions
"""

import folium
import geopandas as gpd
from pathlib import Path


def create_ny_maps():
    """Generate NY boundary and water maps"""
    print("\n" + "=" * 60)
    print("Creating New York Maps")
    print("=" * 60)

    try:
        # Load NY boundary
        print("  Loading NY boundary from JSON...")
        ny_boundary = gpd.read_file('docs/json/ny_boundary.json')

        # Load NY Lake Champlain water
        print("  Loading NY Lake Champlain water from JSON...")
        ny_water = gpd.read_file('docs/json/ny_lake_champlain_water.json')

        bounds = ny_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # Regular map with basemap
        print("  Creating regular map...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            ny_boundary,
            name='NY Boundary',
            style_function=lambda x: {
                'fillColor': '#1a237e',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME'])
        ).add_to(m)

        folium.GeoJson(
            ny_water,
            name='Lake Champlain Water',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        folium.LayerControl().add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">New York State</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                NY state boundary and Lake Champlain counties<br>
                Census TIGER 2022
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output_path = 'output/ny_boundary.html'
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        m.save(output_path)
        print(f"✓ Saved regular map to {output_path}")

        # Vector-only map
        print("  Creating vector-only map...")
        m_vector = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles=None,
            attr='Vector Data Only'
        )

        m_vector.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            ny_boundary,
            name='NY Boundary',
            style_function=lambda x: {
                'fillColor': '#1a237e',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.3
            }
        ).add_to(m_vector)

        folium.GeoJson(
            ny_water,
            name='Lake Champlain Water',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m_vector)

        folium.LayerControl().add_to(m_vector)

        title_html_vector = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">New York State - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                NY state boundary and Lake Champlain counties
            </p>
        </div>
        '''
        m_vector.get_root().html.add_child(folium.Element(title_html_vector))

        output_path_vector = 'output/ny_boundary_vector.html'
        m_vector.save(output_path_vector)
        print(f"✓ Saved vector map to {output_path_vector}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def create_nh_maps():
    """Generate NH boundary maps"""
    print("\n" + "=" * 60)
    print("Creating New Hampshire Maps")
    print("=" * 60)

    try:
        print("  Loading NH boundary from JSON...")
        nh_boundary = gpd.read_file('docs/json/nh_boundary.json')

        bounds = nh_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # Regular map with basemap
        print("  Creating regular map...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            nh_boundary,
            name='NH Boundary',
            style_function=lambda x: {
                'fillColor': '#c62828',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME'])
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">New Hampshire</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                NH state boundary - Eastern neighbor along Connecticut River<br>
                Census TIGER 2023
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output_path = 'output/nh_boundary.html'
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        m.save(output_path)
        print(f"✓ Saved regular map to {output_path}")

        # Vector-only map
        print("  Creating vector-only map...")
        m_vector = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles=None,
            attr='Vector Data Only'
        )

        m_vector.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            nh_boundary,
            name='NH Boundary',
            style_function=lambda x: {
                'fillColor': '#c62828',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.3
            }
        ).add_to(m_vector)

        title_html_vector = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">New Hampshire - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                NH state boundary
            </p>
        </div>
        '''
        m_vector.get_root().html.add_child(folium.Element(title_html_vector))

        output_path_vector = 'output/nh_boundary_vector.html'
        m_vector.save(output_path_vector)
        print(f"✓ Saved vector map to {output_path_vector}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def create_ma_maps():
    """Generate MA boundary maps"""
    print("\n" + "=" * 60)
    print("Creating Massachusetts Maps")
    print("=" * 60)

    try:
        print("  Loading MA boundary from JSON...")
        ma_boundary = gpd.read_file('docs/json/ma_boundary.json')

        bounds = ma_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # Regular map with basemap
        print("  Creating regular map...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            ma_boundary,
            name='MA Boundary',
            style_function=lambda x: {
                'fillColor': '#0d47a1',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME'])
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Massachusetts</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                MA state boundary - Southern neighbor for regional context<br>
                Census TIGER 2023
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output_path = 'output/ma_boundary.html'
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        m.save(output_path)
        print(f"✓ Saved regular map to {output_path}")

        # Vector-only map
        print("  Creating vector-only map...")
        m_vector = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles=None,
            attr='Vector Data Only'
        )

        m_vector.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            ma_boundary,
            name='MA Boundary',
            style_function=lambda x: {
                'fillColor': '#0d47a1',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.3
            }
        ).add_to(m_vector)

        title_html_vector = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Massachusetts - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                MA state boundary
            </p>
        </div>
        '''
        m_vector.get_root().html.add_child(folium.Element(title_html_vector))

        output_path_vector = 'output/ma_boundary_vector.html'
        m_vector.save(output_path_vector)
        print(f"✓ Saved vector map to {output_path_vector}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Neighboring States Map Generator")
    print("=" * 60)

    success_count = 0

    if create_ny_maps():
        success_count += 1

    if create_nh_maps():
        success_count += 1

    if create_ma_maps():
        success_count += 1

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated maps for {success_count}/3 states")
    print("=" * 60)
