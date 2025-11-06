"""
Quick demo visualization using Vermont census data
Generates a simple map to bootstrap the GitHub Pages site
"""

import folium
import geopandas as gpd
from pathlib import Path


def create_vermont_demo_map(output_path: str = 'output/vermont_demo.html'):
    """
    Create a simple demo map of Vermont using Census TIGER data

    Args:
        output_path: Where to save the HTML map
    """
    print("Creating Vermont demo map...")
    print("Downloading Vermont state boundary from Census Bureau...")

    # Use Census TIGER/Line data - publicly accessible
    tiger_url = "https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip"

    try:
        # Read directly from URL
        print("  Loading US states data...")
        states = gpd.read_file(tiger_url)

        # Filter for Vermont (FIPS code 50)
        print("  Filtering for Vermont...")
        vermont = states[states['STATEFP'] == '50'].copy()

        # Reproject to WGS84 for Folium
        if vermont.crs != 'EPSG:4326':
            vermont = vermont.to_crs('EPSG:4326')

        # Get Vermont centroid for map center
        centroid = vermont.geometry.centroid.iloc[0]
        center_lat, center_lon = centroid.y, centroid.x

        print(f"  Creating interactive map centered at {center_lat:.4f}, {center_lon:.4f}...")

        # Create Folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        # Add Vermont boundary
        folium.GeoJson(
            vermont,
            name='Vermont',
            style_function=lambda x: {
                'fillColor': '#2c5f2d',
                'color': '#1e4320',
                'weight': 3,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'STUSPS'],
                aliases=['State Name:', 'Abbreviation:']
            ),
            popup=folium.GeoJsonPopup(
                fields=['NAME', 'STUSPS', 'STATEFP'],
                aliases=['State:', 'Code:', 'FIPS:']
            )
        ).add_to(m)

        # Add a title
        title_html = '''
        <div style="position: fixed;
                    top: 10px;
                    left: 50px;
                    width: 300px;
                    height: 90px;
                    background-color: white;
                    border: 2px solid #2c5f2d;
                    border-radius: 5px;
                    z-index: 9999;
                    font-size: 14px;
                    padding: 10px;">
            <h4 style="margin: 0; color: #2c5f2d;">Vermont</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                The Green Mountain State<br>
                <i>Data: US Census Bureau TIGER/Line</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Save map
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"\n✓ Demo map saved to {output_path}")
        print(f"  Open in browser to view!")

        return str(output)

    except Exception as e:
        print(f"\n✗ Error creating demo map: {e}")
        return None


def create_water_demo_map(output_path: str = 'output/vermont_water.html'):
    """
    Create a demo map showing Vermont water bodies

    Args:
        output_path: Where to save the HTML map
    """
    print("\nCreating Vermont water bodies map...")
    print("Downloading water data from Census Bureau...")

    # Census water bodies for Vermont
    water_url = "https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_50_areawater.zip"

    try:
        print("  Loading Vermont water bodies...")
        water = gpd.read_file(water_url)

        # Reproject to WGS84
        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        # Filter for significant water bodies (> 1 sq km)
        water['area_sqkm'] = water.geometry.area * 111 * 111  # rough conversion
        large_water = water[water['area_sqkm'] > 1].copy()

        print(f"  Found {len(large_water)} significant water bodies...")

        # Get bounds for map center
        bounds = large_water.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
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
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME'] if 'FULLNAME' in large_water.columns else [],
                aliases=['Name:']
            )
        ).add_to(m)

        # Add title
        title_html = '''
        <div style="position: fixed;
                    top: 10px;
                    left: 50px;
                    width: 320px;
                    height: 90px;
                    background-color: white;
                    border: 2px solid #4a90e2;
                    border-radius: 5px;
                    z-index: 9999;
                    font-size: 14px;
                    padding: 10px;">
            <h4 style="margin: 0; color: #2e5f8a;">Vermont Water Bodies</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Lakes, ponds, and rivers<br>
                <i>Data: US Census Bureau TIGER/Line</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Save
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Water map saved to {output_path}")

        return str(output)

    except Exception as e:
        print(f"✗ Error creating water map: {e}")
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("Vermont Demo Map Generator")
    print("=" * 60)
    print()

    # Create demo maps
    maps_created = []

    demo_map = create_vermont_demo_map()
    if demo_map:
        maps_created.append(demo_map)

    water_map = create_water_demo_map()
    if water_map:
        maps_created.append(water_map)

    # Summary
    print("\n" + "=" * 60)
    print(f"Created {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  {map_path}")

    print("\nNext steps:")
    print("1. Open maps in browser to preview")
    print("2. Copy to docs/: cp output/*.html docs/")
    print("3. Push to GitHub to publish on GitHub Pages")
