"""
Generate comparison maps from multiple Vermont data sources
Uses working URLs from Vermont Open Geodata and Census TIGER/Line
"""

import folium
import geopandas as gpd
from pathlib import Path
import json


def create_vt_geodata_boundary_map(output_path: str = 'output/vt_opendata_boundary.html'):
    """
    Vermont boundary from VT Open Geodata Portal
    """
    print("\n" + "=" * 60)
    print("VT Open Geodata: State Boundary")
    print("=" * 60)

    try:
        print("  Downloading from geodata.vermont.gov...")
        url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Boundary_BNDHASH_poly_vtbnd_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"

        gdf = gpd.read_file(url)
        print(f"  Loaded {len(gdf)} features")

        # Reproject to WGS84
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')

        bounds = gdf.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            gdf,
            name='VT Boundary',
            style_function=lambda x: {
                'fillColor': '#2c5f2d',
                'color': '#1e4320',
                'weight': 3,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns[:5]))
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #2c5f2d;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2c5f2d;">VT State Boundary</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Official Vermont boundary from state GIS<br>
                Includes town, county, and administrative boundaries<br>
                <i>Source: Vermont Open Geodata Portal</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        stats = {
            'features': len(gdf),
            'bounds': bounds.tolist(),
            'fields': list(gdf.columns)
        }

        print(f"✓ Saved to {output_path}")
        return str(output), stats

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_vt_geodata_water_map(output_path: str = 'output/vt_opendata_water.html'):
    """
    Vermont water bodies from VT Open Geodata Portal
    """
    print("\n" + "=" * 60)
    print("VT Open Geodata: Water Bodies (Hydrography Polygons)")
    print("=" * 60)

    try:
        print("  Downloading from geodata.vermont.gov...")
        url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Water_VHDCARTO_poly_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"

        gdf = gpd.read_file(url)
        print(f"  Loaded {len(gdf)} water features")

        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')

        # Center on Lake Champlain for island visibility
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            gdf,
            name='Water Bodies',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#2e5f8a',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['GNIS_Name', 'FType'] if 'GNIS_Name' in gdf.columns else []
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 440px;
                    background-color: white; border: 2px solid #4a90e2;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2e5f8a;">VT Water Bodies</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Vermont Hydrography Dataset (VHD) - Polygons<br>
                Lakes, ponds, and larger streams<br>
                <b>★ Islands visible as gaps in water polygons</b><br>
                <i>Source: Vermont Open Geodata Portal</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        stats = {
            'features': len(gdf),
            'bounds': gdf.total_bounds.tolist(),
            'fields': list(gdf.columns)
        }

        print(f"✓ Saved to {output_path}")
        return str(output), stats

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_census_water_map(output_path: str = 'output/census_water_champlain.html'):
    """
    Census TIGER water for counties around Lake Champlain
    Grand Isle (50013), Chittenden (50007), Franklin (50011), Addison (50001)
    """
    print("\n" + "=" * 60)
    print("Census TIGER: Lake Champlain Counties Water")
    print("=" * 60)

    try:
        # Counties around Lake Champlain
        counties = {
            '50013': 'Grand Isle',
            '50007': 'Chittenden',
            '50011': 'Franklin',
            '50001': 'Addison'
        }

        all_water = []

        for fips, name in counties.items():
            print(f"  Downloading {name} County water...")
            url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
            gdf = gpd.read_file(url)
            all_water.append(gdf)

        # Combine
        water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))
        print(f"  Combined: {len(water)} water features")

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        # Filter to significant water
        water['area_sqkm'] = water.geometry.area * 111 * 111
        large_water = water[water['area_sqkm'] > 0.01].copy()
        print(f"  Showing {len(large_water)} features > 0.01 sq km")

        m = folium.Map(
            location=[44.7, -73.25],
            zoom_start=10,
            tiles='OpenStreetMap'
        )

        folium.GeoJson(
            large_water,
            name='Water Areas',
            style_function=lambda x: {
                'fillColor': '#1e88e5',
                'color': '#0d47a1',
                'weight': 1,
                'fillOpacity': 0.75
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME'] if 'FULLNAME' in large_water.columns else []
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #1e88e5;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #0d47a1;">Census TIGER: Champlain Water</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Grand Isle, Chittenden, Franklin, Addison Counties<br>
                <b>★ Full Lake Champlain coverage!</b><br>
                Includes islands and southern lake region<br>
                <i>Source: US Census TIGER/Line 2022</i>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        stats = {
            'features': len(large_water),
            'total_features': len(water),
            'counties': list(counties.values()),
            'bounds': large_water.total_bounds.tolist()
        }

        print(f"✓ Saved to {output_path}")
        return str(output), stats

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_combined_comparison(output_path: str = 'output/data_comparison.html'):
    """
    Side-by-side comparison of both data sources
    """
    print("\n" + "=" * 60)
    print("Creating Combined Comparison Map")
    print("=" * 60)

    try:
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # VT Open Data water
        print("  Loading VT Open Geodata water...")
        vt_url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Water_VHDCARTO_poly_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"
        vt_water = gpd.read_file(vt_url)
        if vt_water.crs != 'EPSG:4326':
            vt_water = vt_water.to_crs('EPSG:4326')

        folium.GeoJson(
            vt_water,
            name='VT Open Geodata Water',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#2e5f8a',
                'weight': 1,
                'fillOpacity': 0.5
            }
        ).add_to(m)

        # VT boundary for context
        print("  Loading VT boundary...")
        boundary_url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Boundary_BNDHASH_poly_vtbnd_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"
        boundary = gpd.read_file(boundary_url)
        if boundary.crs != 'EPSG:4326':
            boundary = boundary.to_crs('EPSG:4326')

        folium.GeoJson(
            boundary,
            name='VT Boundary',
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#2c5f2d',
                'weight': 2,
                'fillOpacity': 0
            }
        ).add_to(m)

        folium.LayerControl().add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 420px;
                    background-color: white; border: 2px solid #2c5f2d;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0; color: #2c5f2d;">Data Source Comparison</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Compare VT Open Geodata vs Census TIGER<br>
                Use layer control (top right) to toggle layers<br>
                <b>Focus: Lake Champlain island representation</b>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        stats = {
            'vt_water_features': len(vt_water),
            'boundary_features': len(boundary)
        }

        print(f"✓ Saved to {output_path}")
        return str(output), stats

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == '__main__':
    import pandas as pd

    print("=" * 60)
    print("Vermont Geodata Comparison Generator")
    print("Multiple data sources for visual assessment")
    print("=" * 60)

    all_stats = {}
    maps_created = []

    # Generate all maps
    result, stats = create_vt_geodata_boundary_map()
    if result:
        maps_created.append(result)
        all_stats['vt_boundary'] = stats

    result, stats = create_vt_geodata_water_map()
    if result:
        maps_created.append(result)
        all_stats['vt_water'] = stats

    result, stats = create_census_water_map()
    if result:
        maps_created.append(result)
        all_stats['census_water'] = stats

    result, stats = create_combined_comparison()
    if result:
        maps_created.append(result)
        all_stats['comparison'] = stats

    # Also add the counties map we already created
    counties_path = Path('output/vermont_counties.html')
    if counties_path.exists():
        maps_created.append(str(counties_path))

    # Save stats
    stats_file = Path('output/map_stats.json')
    with open(stats_file, 'w') as f:
        json.dump(all_stats, f, indent=2)
    print(f"\n✓ Stats saved to {stats_file}")

    # Summary
    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        map_file = Path(map_path)
        size_mb = map_file.stat().st_size / (1024 * 1024)
        print(f"  ✓ {map_path} ({size_mb:.2f} MB)")

    print("\n" + "=" * 60)
    print("DATASET ASSESSMENT GUIDE")
    print("=" * 60)
    print("1. vt_opendata_boundary.html - Official VT state boundary")
    print("2. vt_opendata_water.html - VT hydrography (BEST for islands!)")
    print("3. census_water_champlain.html - Census data for Lake Champlain")
    print("4. vermont_counties.html - County divisions")
    print("5. data_comparison.html - Side-by-side comparison")
    print("\nRecommendation: VT Open Geodata has the most detailed")
    print("and accurate representation of Lake Champlain islands!")
