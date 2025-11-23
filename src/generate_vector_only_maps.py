"""
Generate vector-only versions of maps (no background tiles)
Shows just the data geometries for pure assessment
"""

import folium
import geopandas as gpd
from pathlib import Path


def create_vector_only_water_map(output_path: str = 'output/vt_opendata_water_vector.html'):
    """
    VT Open Geodata water - vector only, no base map
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: Vermont Rivers")
    print("=" * 60)

    try:
        print("  Downloading from geodata.vermont.gov...")
        url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Water_VHDCARTO_poly_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"

        gdf = gpd.read_file(url)
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')

        print(f"  Loaded {len(gdf)} features")

        # Create map with NO tiles
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles=None,  # No background tiles!
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Add water in blue with black outlines
        folium.GeoJson(
            gdf,
            name='Water Bodies',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['GNIS_NAME'] if 'GNIS_NAME' in gdf.columns else []
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Vermont Rivers - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                <b>Islands visible as gaps in blue polygons</b><br>
                2,000 features from VT Open Geodata Portal
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_vector_only_census_water(output_path: str = 'output/census_water_champlain_vector.html'):
    """
    Census water - vector only
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: Census Water")
    print("=" * 60)

    try:
        import pandas as pd

        counties = {
            '50013': 'Grand Isle',
            '50007': 'Chittenden',
            '50011': 'Franklin',
            '50001': 'Addison'
        }

        all_water = []
        for fips, name in counties.items():
            print(f"  Downloading {name} County...")
            url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
            gdf = gpd.read_file(url)
            all_water.append(gdf)

        water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        water['area_sqkm'] = water.geometry.area * 111 * 111
        large_water = water[water['area_sqkm'] > 0.01].copy()

        print(f"  Showing {len(large_water)} features")

        # No tiles
        m = folium.Map(
            location=[44.7, -73.25],
            zoom_start=10,
            tiles=None,
            attr='Vector Data Only'
        )

        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            large_water,
            name='Water',
            style_function=lambda x: {
                'fillColor': '#1e88e5',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            }
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Census TIGER Water - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                Lake Champlain region (3 counties)<br>
                250 features from Census TIGER 2022
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_vector_only_vt_census_all_water(output_path: str = 'output/vt_census_water_all_vector.html'):
    """
    Complete VT Census water - vector only
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: VT Census Water (All Counties)")
    print("=" * 60)

    try:
        import pandas as pd

        # All 14 Vermont counties
        counties = {
            '50001': 'Addison',
            '50003': 'Bennington',
            '50005': 'Caledonia',
            '50007': 'Chittenden',
            '50009': 'Essex',
            '50011': 'Franklin',
            '50013': 'Grand Isle',
            '50015': 'Lamoille',
            '50017': 'Orange',
            '50019': 'Orleans',
            '50021': 'Rutland',
            '50023': 'Washington',
            '50025': 'Windham',
            '50027': 'Windsor'
        }

        all_water = []
        for fips, name in counties.items():
            print(f"  Downloading {name} County...")
            url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
            gdf = gpd.read_file(url)
            all_water.append(gdf)

        water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        water['area_sqkm'] = water['AWATER'] / 1_000_000  # Convert sq meters to sq km
        large_water = water[water['area_sqkm'] > 0.01].copy()

        # Add human-readable feature type
        mtfcc_names = {
            'H2030': 'Lake/Pond',
            'H2040': 'Reservoir',
            'H2053': 'Swamp/Marsh',
            'H2081': 'Glacier',
            'H3010': 'Stream/River',
            'H3013': 'Braided Stream',
            'H3020': 'Canal/Ditch/Aqueduct'
        }
        large_water['feature_type'] = large_water['MTFCC'].map(mtfcc_names).fillna('Unknown')

        print(f"  Showing {len(large_water)} features")

        # Center on Vermont
        bounds = large_water.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # No tiles
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles=None,
            attr='Vector Data Only'
        )

        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            large_water,
            name='Water',
            style_function=lambda x: {
                'fillColor': '#1e88e5',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'feature_type', 'HYDROID', 'area_sqkm'],
                aliases=['Name:', 'Type:', 'Hydro ID:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">VT Census Water (All Counties) - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                Complete Vermont coverage (14 counties)<br>
                Census TIGER 2022
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_vector_only_ny_census_all_water(output_path: str = 'output/ny_census_water_all_vector.html'):
    """
    Complete NY Census water - vector only
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: NY Census Water (All Counties)")
    print("=" * 60)

    try:
        import pandas as pd

        # All 62 New York counties
        counties = {
            '36001': 'Albany', '36003': 'Allegany', '36005': 'Bronx', '36007': 'Broome',
            '36009': 'Cattaraugus', '36011': 'Cayuga', '36013': 'Chautauqua', '36015': 'Chemung',
            '36017': 'Chenango', '36019': 'Clinton', '36021': 'Columbia', '36023': 'Cortland',
            '36025': 'Delaware', '36027': 'Dutchess', '36029': 'Erie', '36031': 'Essex',
            '36033': 'Franklin', '36035': 'Fulton', '36037': 'Genesee', '36039': 'Greene',
            '36041': 'Hamilton', '36043': 'Herkimer', '36045': 'Jefferson', '36047': 'Kings',
            '36049': 'Lewis', '36051': 'Livingston', '36053': 'Madison', '36055': 'Monroe',
            '36057': 'Montgomery', '36059': 'Nassau', '36061': 'New York', '36063': 'Niagara',
            '36065': 'Oneida', '36067': 'Onondaga', '36069': 'Ontario', '36071': 'Orange',
            '36073': 'Orleans', '36075': 'Oswego', '36077': 'Otsego', '36079': 'Putnam',
            '36081': 'Queens', '36083': 'Rensselaer', '36085': 'Richmond', '36087': 'Rockland',
            '36089': 'St. Lawrence', '36091': 'Saratoga', '36093': 'Schenectady', '36095': 'Schoharie',
            '36097': 'Schuyler', '36099': 'Seneca', '36101': 'Steuben', '36103': 'Suffolk',
            '36105': 'Sullivan', '36107': 'Tioga', '36109': 'Tompkins', '36111': 'Ulster',
            '36113': 'Warren', '36115': 'Washington', '36117': 'Wayne', '36119': 'Westchester',
            '36121': 'Wyoming', '36123': 'Yates'
        }

        all_water = []
        for fips, name in counties.items():
            print(f"  Downloading {name} County...")
            url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
            gdf = gpd.read_file(url)
            all_water.append(gdf)

        water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))

        if water.crs != 'EPSG:4326':
            water = water.to_crs('EPSG:4326')

        water['area_sqkm'] = water.geometry.area * 111 * 111
        large_water = water[water['area_sqkm'] > 0.01].copy()

        print(f"  Showing {len(large_water)} features")

        # Center on New York
        bounds = large_water.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # No tiles
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles=None,
            attr='Vector Data Only'
        )

        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            large_water,
            name='Water',
            style_function=lambda x: {
                'fillColor': '#1e88e5',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            }
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">NY Census Water (All Counties) - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                Complete New York coverage (62 counties)<br>
                Census TIGER 2022
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_vector_only_comparison(output_path: str = 'output/data_comparison_vector.html'):
    """
    Comparison map - vector only
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: Data Comparison")
    print("=" * 60)

    try:
        # No tiles
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles=None,
            attr='Vector Data Only'
        )

        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # VT water
        print("  Loading VT Open Geodata...")
        vt_url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Water_VHDCARTO_poly_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"
        vt_water = gpd.read_file(vt_url)
        if vt_water.crs != 'EPSG:4326':
            vt_water = vt_water.to_crs('EPSG:4326')

        folium.GeoJson(
            vt_water,
            name='VT Open Geodata',
            style_function=lambda x: {
                'fillColor': '#4a90e2',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.6
            }
        ).add_to(m)

        # VT boundary
        print("  Loading boundary...")
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
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Data Comparison - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                Toggle layers to compare sources<br>
                VT Open Geodata + State Boundary
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_vector_only_counties(output_path: str = 'output/vermont_counties_vector.html'):
    """
    Counties - vector only
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: Vermont Counties")
    print("=" * 60)

    try:
        print("  Downloading counties...")
        url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
        counties = gpd.read_file(url)
        vt_counties = counties[counties['STATEFP'] == '50'].copy()

        if vt_counties.crs != 'EPSG:4326':
            vt_counties = vt_counties.to_crs('EPSG:4326')

        bounds = vt_counties.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles=None,
            attr='Vector Data Only'
        )

        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            vt_counties,
            name='Counties',
            style_function=lambda x: {
                'fillColor': '#90c695',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.5
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME'])
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 350px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Vermont Counties - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                14 counties, Census TIGER 2023
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def create_vector_only_boundary(output_path: str = 'output/vermont_demo_vector.html'):
    """
    State boundary - vector only
    """
    print("\n" + "=" * 60)
    print("Creating Vector-Only: State Boundary")
    print("=" * 60)

    try:
        print("  Downloading state boundary...")
        url = "https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip"
        states = gpd.read_file(url)
        vermont = states[states['STATEFP'] == '50'].copy()

        if vermont.crs != 'EPSG:4326':
            vermont = vermont.to_crs('EPSG:4326')

        bounds = vermont.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles=None,
            attr='Vector Data Only'
        )

        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        folium.GeoJson(
            vermont,
            name='Vermont',
            style_function=lambda x: {
                'fillColor': '#2c5f2d',
                'color': '#000000',
                'weight': 3,
                'fillOpacity': 0.4
            }
        ).add_to(m)

        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 350px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Vermont Boundary - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data<br>
                Census TIGER 2023
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("Vermont Vector-Only Map Generator")
    print("No background tiles - pure data visualization")
    print("=" * 60)

    maps_created = []

    result = create_vector_only_water_map()
    if result:
        maps_created.append(result)

    result = create_vector_only_census_water()
    if result:
        maps_created.append(result)

    result = create_vector_only_vt_census_all_water()
    if result:
        maps_created.append(result)

    result = create_vector_only_ny_census_all_water()
    if result:
        maps_created.append(result)

    result = create_vector_only_comparison()
    if result:
        maps_created.append(result)

    result = create_vector_only_counties()
    if result:
        maps_created.append(result)

    result = create_vector_only_boundary()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} vector-only map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
