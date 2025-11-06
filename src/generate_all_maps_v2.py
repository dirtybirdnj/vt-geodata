"""
Generate multiple Vermont maps from different data sources for comparison
Using 2022 Census data (2023 URLs are not yet fully available)
"""

import folium
import geopandas as gpd
from pathlib import Path
import sys


def create_water_areas_map(output_path: str = 'output/vermont_water_areas.html'):
    """
    Water areas including Lake Champlain - this should show islands!
    """
    print("\n" + "=" * 60)
    print("Creating Vermont Water Areas Map")
    print("=" * 60)

    try:
        print("  Downloading water areas data (2022)...")
        url = "https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_50_areawater.zip"
        water = gpd.read_file(url)

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        print(f"  Found {len(water)} water features")

        # Calculate area for filtering
        water['area_sqkm'] = water.geometry.area * 111 * 111

        # Show all significant water
        large_water = water[water['area_sqkm'] > 0.05].copy()
        print(f"  Showing {len(large_water)} water bodies > 0.05 sq km")

        # Create map centered on Lake Champlain
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Add water bodies
        folium.GeoJson(
            large_water,
            name='Water Bodies',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#2e5f8a',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'MTFCC'] if 'FULLNAME' in large_water.columns else [],
                aliases=['Name:', 'Type:']
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 420px;
                    background-color: white; border: 2px solid #4a90e2;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2e5f8a;">Vermont Water Areas (AREAWATER)</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Water surface areas from Census Bureau<br>
                <b>Key: Islands = gaps in water polygons</b><br>
                Zoom to Lake Champlain to see island outlines<br>
                <i>Data: US Census TIGER/Line 2022</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Water areas map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_linear_water_map(output_path: str = 'output/vermont_rivers.html'):
    """
    Linear water features - rivers and streams
    """
    print("\n" + "=" * 60)
    print("Creating Vermont Rivers & Streams Map")
    print("=" * 60)

    try:
        print("  Downloading linear water features (2022)...")
        url = "https://www2.census.gov/geo/tiger/TIGER2022/LINEARWATER/tl_2022_50_linearwater.zip"
        linear_water = gpd.read_file(url)

        if linear_water.crs != 'EPSG:4326':
            linear_water = linear_water.to_crs('EPSG:4326')

        print(f"  Found {len(linear_water)} linear water features")

        # Sample for web performance
        sample_size = min(1500, len(linear_water))
        if len(linear_water) > sample_size:
            print(f"  Sampling {sample_size} features for web display...")
            linear_water = linear_water.sample(n=sample_size, random_state=42)

        bounds = linear_water.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            linear_water,
            name='Rivers & Streams',
            style_function=lambda x: {
                'color': '#3498db',
                'weight': 2,
                'opacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME'] if 'FULLNAME' in linear_water.columns else []
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 350px;
                    background-color: white; border: 2px solid #3498db;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2e5f8a;">Vermont Rivers & Streams</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Linear water features (sample)<br>
                <i>Data: US Census TIGER/Line 2022</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Rivers map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_champlain_focus_map(output_path: str = 'output/lake_champlain_islands.html'):
    """
    Zoomed in on Lake Champlain to see islands clearly
    """
    print("\n" + "=" * 60)
    print("Creating Lake Champlain Islands Focus Map")
    print("=" * 60)

    try:
        print("  Downloading water areas...")
        water = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_50_areawater.zip")

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        # Get state boundary for context
        print("  Downloading state boundary...")
        states = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip")
        vt_state = states[states['STATEFP'] == '50'].copy()
        if vt_state.crs != 'EPSG:4326':
            vt_state = vt_state.to_crs('EPSG:4326')

        # Filter water to Champlain region
        champlain_bbox = (-73.5, 43.5, -73.0, 45.2)
        champlain_water = water.cx[champlain_bbox[0]:champlain_bbox[2], champlain_bbox[1]:champlain_bbox[3]].copy()

        print(f"  Found {len(champlain_water)} water features in Lake Champlain area")

        # Create map zoomed to Champlain
        m = folium.Map(
            location=[44.6, -73.25],
            zoom_start=10,
            tiles='OpenStreetMap'
        )

        # Add VT boundary for context
        folium.GeoJson(
            vt_state,
            name='Vermont Boundary',
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#2c5f2d',
                'weight': 2,
                'fillOpacity': 0
            }
        ).add_to(m)

        # Add water - islands will show as gaps
        folium.GeoJson(
            champlain_water,
            name='Lake Water',
            style_function=lambda x: {
                'fillColor': '#1e88e5',
                'color': '#0d47a1',
                'weight': 1,
                'fillOpacity': 0.8
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME'] if 'FULLNAME' in champlain_water.columns else []
            )
        ).add_to(m)

        folium.LayerControl().add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #1e88e5;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #0d47a1;">Lake Champlain Islands</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Zoomed view of Lake Champlain<br>
                <b>Islands visible as gaps in blue water polygons</b><br>
                Look for: Grand Isle, North Hero, South Hero<br>
                <i>Data: US Census TIGER/Line 2022</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Champlain islands map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_combined_overview(output_path: str = 'output/vermont_combined.html'):
    """
    All layers combined for comparison
    """
    print("\n" + "=" * 60)
    print("Creating Combined Overview Map")
    print("=" * 60)

    try:
        m = folium.Map(
            location=[44.0, -72.7],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        # State boundary
        print("  Adding state boundary...")
        states = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip")
        vt_state = states[states['STATEFP'] == '50'].copy()
        if vt_state.crs != 'EPSG:4326':
            vt_state = vt_state.to_crs('EPSG:4326')

        folium.GeoJson(
            vt_state,
            name='State Boundary',
            style_function=lambda x: {
                'fillColor': '#e8f5e9',
                'color': '#2c5f2d',
                'weight': 3,
                'fillOpacity': 0.2
            }
        ).add_to(m)

        # Counties
        print("  Adding counties...")
        counties = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip")
        vt_counties = counties[counties['STATEFP'] == '50'].copy()
        if vt_counties.crs != 'EPSG:4326':
            vt_counties = vt_counties.to_crs('EPSG:4326')

        folium.GeoJson(
            vt_counties,
            name='Counties',
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#666',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME'])
        ).add_to(m)

        # Water areas
        print("  Adding water areas...")
        water = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_50_areawater.zip")
        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')
        water['area_sqkm'] = water.geometry.area * 111 * 111
        large_water = water[water['area_sqkm'] > 0.5].copy()

        folium.GeoJson(
            large_water,
            name='Water Bodies',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#2e5f8a',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        folium.LayerControl().add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 380px;
                    background-color: white; border: 2px solid #2c5f2d;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2c5f2d;">Vermont Combined Overview</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                All layers: Boundary + Counties + Water<br>
                Toggle layers with control (top right)<br>
                <i>Data: US Census TIGER/Line 2022-2023</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Combined map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("Vermont Multi-Dataset Map Generator v2")
    print("Using Census TIGER/Line 2022-2023 data")
    print("=" * 60)

    maps_created = []

    # Generate all maps
    result = create_water_areas_map()
    if result:
        maps_created.append(result)

    result = create_linear_water_map()
    if result:
        maps_created.append(result)

    result = create_champlain_focus_map()
    if result:
        maps_created.append(result)

    result = create_combined_overview()
    if result:
        maps_created.append(result)

    # Summary
    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")

    print("\nNext steps:")
    print("1. Open in browser - islands show as gaps in water")
    print("2. Copy to docs/: cp output/*.html docs/")
    print("3. Push to GitHub")
