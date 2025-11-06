"""
Generate multiple Vermont maps from different data sources for comparison
Focus on Lake Champlain islands and water features
"""

import folium
import geopandas as gpd
from pathlib import Path
import sys


def create_counties_map(output_path: str = 'output/vermont_counties.html'):
    """
    Vermont counties map - helps see geographic divisions
    """
    print("\n" + "=" * 60)
    print("Creating Vermont Counties Map")
    print("=" * 60)

    try:
        print("  Downloading county boundaries...")
        url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
        counties = gpd.read_file(url)

        # Filter for Vermont (FIPS 50)
        vt_counties = counties[counties['STATEFP'] == '50'].copy()

        if vt_counties.crs != 'EPSG:4326':
            vt_counties = vt_counties.to_crs('EPSG:4326')

        print(f"  Found {len(vt_counties)} counties")

        # Center on Vermont
        bounds = vt_counties.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        # Add counties with different colors
        folium.GeoJson(
            vt_counties,
            name='Counties',
            style_function=lambda x: {
                'fillColor': '#90c695',
                'color': '#2c5f2d',
                'weight': 2,
                'fillOpacity': 0.4
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'NAMELSAD'],
                aliases=['County:', 'Full Name:']
            )
        ).add_to(m)

        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 320px;
                    background-color: white; border: 2px solid #2c5f2d;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2c5f2d;">Vermont Counties</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                14 Counties in the Green Mountain State<br>
                <i>Data: US Census TIGER/Line 2023</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Counties map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_water_areas_map(output_path: str = 'output/vermont_water_areas.html'):
    """
    Water areas including Lake Champlain - this should show islands!
    """
    print("\n" + "=" * 60)
    print("Creating Vermont Water Areas Map (Census AREAWATER)")
    print("=" * 60)

    try:
        print("  Downloading water areas data...")
        url = "https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_50_areawater.zip"
        water = gpd.read_file(url)

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        print(f"  Found {len(water)} water features")

        # Calculate area in sq km for filtering
        water['area_sqkm'] = water.geometry.area * 111 * 111

        # Filter for significant water bodies
        large_water = water[water['area_sqkm'] > 0.1].copy()
        print(f"  Filtered to {len(large_water)} significant water bodies")

        # Focus on Lake Champlain area
        # Champlain extends from ~73.45W to ~73.0W, ~43.5N to ~45.1N
        champlain_water = water[
            (water.geometry.centroid.x < -73.0) &
            (water.geometry.centroid.x > -73.5) &
            (water.geometry.centroid.y > 43.5) &
            (water.geometry.centroid.y < 45.2)
        ].copy()

        print(f"  Lake Champlain area features: {len(champlain_water)}")

        # Create map centered on Lake Champlain
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Add all Vermont water
        folium.GeoJson(
            large_water,
            name='All Water Bodies',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#2e5f8a',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'MTFCC'],
                aliases=['Name:', 'Feature Type:']
            ) if 'FULLNAME' in large_water.columns else None
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 380px;
                    background-color: white; border: 2px solid #4a90e2;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2e5f8a;">Vermont Water Areas</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Census AREAWATER polygons - water surface areas<br>
                <b>Note:</b> Islands appear as "gaps" in the water<br>
                <i>Data: US Census TIGER/Line 2023</i>
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
        return None


def create_coastline_map(output_path: str = 'output/vermont_coastline.html'):
    """
    Coastline/shoreline data - might show islands as separate features
    """
    print("\n" + "=" * 60)
    print("Creating Vermont Coastline Map (Census COASTLINE)")
    print("=" * 60)

    try:
        print("  Downloading coastline data...")
        url = "https://www2.census.gov/geo/tiger/TIGER2023/COASTLINE/tl_2023_us_coastline.zip"
        coastline = gpd.read_file(url)

        if coastline.crs != 'EPSG:4326':
            coastline = coastline.to_crs('EPSG:4326')

        # Filter for Vermont area
        vt_bounds = (-73.5, 42.7, -71.4, 45.1)
        vt_coastline = coastline.cx[vt_bounds[0]:vt_bounds[2], vt_bounds[1]:vt_bounds[3]]

        print(f"  Found {len(vt_coastline)} coastline features in VT area")

        if len(vt_coastline) == 0:
            print("  No coastline data in Vermont area (expected for landlocked state)")
            return None

        m = folium.Map(
            location=[44.0, -72.7],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            vt_coastline,
            name='Coastline',
            style_function=lambda x: {
                'color': '#e74c3c',
                'weight': 2,
                'opacity': 0.8
            }
        ).add_to(m)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Coastline map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_linear_water_map(output_path: str = 'output/vermont_linear_water.html'):
    """
    Linear water features - rivers and streams
    """
    print("\n" + "=" * 60)
    print("Creating Vermont Linear Water Features Map")
    print("=" * 60)

    try:
        print("  Downloading linear water features...")
        url = "https://www2.census.gov/geo/tiger/TIGER2023/LINEARWATER/tl_2023_50_linearwater.zip"
        linear_water = gpd.read_file(url)

        if linear_water.crs != 'EPSG:4326':
            linear_water = linear_water.to_crs('EPSG:4326')

        print(f"  Found {len(linear_water)} linear water features")

        # Sample subset for performance
        if len(linear_water) > 1000:
            print(f"  Sampling 1000 features for web display...")
            linear_water = linear_water.sample(n=1000, random_state=42)

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
                'opacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME'] if 'FULLNAME' in linear_water.columns else []
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 320px;
                    background-color: white; border: 2px solid #3498db;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2e5f8a;">Vermont Rivers & Streams</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Linear water features (sample)<br>
                <i>Data: US Census TIGER/Line 2023</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Linear water map saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_combined_overview(output_path: str = 'output/vermont_overview.html'):
    """
    Combined overview with multiple layers for comparison
    """
    print("\n" + "=" * 60)
    print("Creating Combined Overview Map")
    print("=" * 60)

    try:
        # Create base map
        m = folium.Map(
            location=[44.0, -72.7],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        # Add state boundary
        print("  Adding state boundary...")
        states = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip")
        vt_state = states[states['STATEFP'] == '50'].copy()
        if vt_state.crs != 'EPSG:4326':
            vt_state = vt_state.to_crs('EPSG:4326')

        folium.GeoJson(
            vt_state,
            name='State Boundary',
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#2c5f2d',
                'weight': 3,
                'fillOpacity': 0
            }
        ).add_to(m)

        # Add water areas
        print("  Adding water areas...")
        water = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_50_areawater.zip")
        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')
        water['area_sqkm'] = water.geometry.area * 111 * 111
        large_water = water[water['area_sqkm'] > 1].copy()

        folium.GeoJson(
            large_water,
            name='Water Bodies',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#2e5f8a',
                'weight': 1,
                'fillOpacity': 0.6
            }
        ).add_to(m)

        # Add counties
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
            }
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 380px;
                    background-color: white; border: 2px solid #2c5f2d;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2c5f2d;">Vermont Overview - All Layers</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Combined view: Boundary + Water + Counties<br>
                Use layer control (top right) to toggle layers<br>
                <i>Data: US Census TIGER/Line 2023</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Combined overview saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("Vermont Multi-Dataset Map Generator")
    print("Generating maps from various Census TIGER/Line datasets")
    print("=" * 60)

    maps_created = []

    # Generate all maps
    result = create_counties_map()
    if result:
        maps_created.append(result)

    result = create_water_areas_map()
    if result:
        maps_created.append(result)

    result = create_coastline_map()
    if result:
        maps_created.append(result)

    result = create_linear_water_map()
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
    print("1. Open maps in browser to compare datasets")
    print("2. Copy to docs/: cp output/*.html docs/")
    print("3. Push to GitHub to publish")
