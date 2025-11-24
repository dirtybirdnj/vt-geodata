#!/usr/bin/env python3
"""
Generate Towns Over Champlain HYDROIDs mashup map
Third-order transformation showing VT towns with water cutouts over combined TIGER HYDROIDs
"""

import folium
import json
from pathlib import Path


def create_towns_over_hydroids_map(output_path: str = 'docs/towns_over_hydroids.html'):
    """
    Create mashup map with VT towns over combined Champlain TIGER HYDROIDs
    """
    print("\n" + "=" * 60)
    print("Creating: Towns Over Champlain HYDROIDs Map")
    print("=" * 60)

    try:
        # Load combined Champlain TIGER HYDROIDs (bottom layer)
        print("  Loading combined Champlain TIGER HYDROIDs...")
        with open('docs/json/champlain_tiger_hydroids_combined.json', 'r') as f:
            water_data = json.load(f)

        water_metadata = water_data.get('metadata', {})

        # Load VT towns with water cutouts (top layer)
        print("  Loading VT towns with water cutouts...")
        with open('docs/json/vt_towns_with_water_cutouts.json', 'r') as f:
            towns_data = json.load(f)

        towns_metadata = towns_data.get('metadata', {})

        # Create map centered on Vermont/Champlain
        m = folium.Map(
            location=[44.3, -73.2],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        # Add combined water features first (bottom layer) - VT in blue, NY in red
        def water_style_function(feature):
            state = feature['properties'].get('state', 'Unknown')
            if state == 'VT':
                return {
                    'fillColor': '#1976d2',
                    'color': '#0d47a1',
                    'weight': 1,
                    'fillOpacity': 0.5
                }
            else:  # NY
                return {
                    'fillColor': '#d32f2f',
                    'color': '#b71c1c',
                    'weight': 1,
                    'fillOpacity': 0.5
                }

        folium.GeoJson(
            water_data,
            name='Champlain TIGER HYDROIDs (VT+NY)',
            style_function=water_style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'state', 'HYDROID', 'area_sqkm'],
                aliases=['Name:', 'State:', 'Hydro ID:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # County colors for towns
        county_colors = {
            'Addison': '#66bb6a',
            'Bennington': '#42a5f5',
            'Caledonia': '#ab47bc',
            'Chittenden': '#ef5350',
            'Essex': '#ffa726',
            'Franklin': '#26c6da',
            'Grand Isle': '#7e57c2',
            'Lamoille': '#ec407a',
            'Orange': '#5c6bc0',
            'Orleans': '#9ccc65',
            'Rutland': '#29b6f6',
            'Washington': '#ff7043',
            'Windham': '#26a69a',
            'Windsor': '#ffd54f'
        }

        # Add VT towns on top - all with BLACK borders (cutout and non-cutout)
        def town_style_function(feature):
            props = feature['properties']
            county = props.get('county_name', 'Unknown')
            has_cutout = props.get('water_cutout_applied', False)

            # All towns use county colors with black borders
            # Cutout towns have slightly thicker borders
            return {
                'fillColor': county_colors.get(county, '#cccccc'),
                'color': '#000000',
                'weight': 2.5 if has_cutout else 1.5,
                'fillOpacity': 0.6
            }

        folium.GeoJson(
            towns_data,
            name='VT Towns (with Water Cutouts)',
            style_function=town_style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'county_name', 'water_cutout_applied', 'new_land_area_sqkm'],
                aliases=['Town:', 'County:', 'Water Cutout:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 540px;
                    background-color: white; border: 2px solid #5c6bc0;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #5c6bc0;">Towns Over Champlain HYDROIDs</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                VT towns with water cutouts overlaid on combined Champlain TIGER water features<br>
                <b>Towns colored by county</b> • Water in blue (VT) and red (NY)
            </p>
            <div style="margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 4px; font-size: 11px;">
                <b>Towns:</b> {towns_metadata.get('total_towns', 0)} total ({towns_metadata.get('towns_with_cutouts', 0)} with cutouts)<br>
                <b>Water:</b> {water_metadata.get('total_features', 0)} features ({water_metadata.get('total_area_sqkm', 0):.0f} sq km)
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Third-Order Transformation: Mashup visualization for analysis
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #5c6bc0; font-weight: 600;
                                     font-size: 14px; display: flex; align-items: center; gap: 5px;">
            <span>←</span>
            <span>Back to Index</span>
        </a>
        '''
        m.get_root().html.add_child(folium.Element(back_button_html))

        # Save map
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_towns_over_hydroids_vector_map(output_path: str = 'docs/towns_over_hydroids_vector.html'):
    """
    Create vector-only version of towns over HYDROIDs
    """
    print("\n" + "=" * 60)
    print("Creating: Towns Over HYDROIDs Vector-Only Map")
    print("=" * 60)

    try:
        # Load combined Champlain TIGER HYDROIDs
        print("  Loading combined Champlain TIGER HYDROIDs...")
        with open('docs/json/champlain_tiger_hydroids_combined.json', 'r') as f:
            water_data = json.load(f)

        # Load VT towns with water cutouts
        print("  Loading VT towns with water cutouts...")
        with open('docs/json/vt_towns_with_water_cutouts.json', 'r') as f:
            towns_data = json.load(f)

        towns_metadata = towns_data.get('metadata', {})

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.3, -73.2],
            zoom_start=8,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Add water features first (bottom) - VT in blue, NY in red
        def water_style_function(feature):
            state = feature['properties'].get('state', 'Unknown')
            if state == 'VT':
                return {
                    'fillColor': '#1976d2',
                    'color': '#0d47a1',
                    'weight': 1,
                    'fillOpacity': 0.6
                }
            else:  # NY
                return {
                    'fillColor': '#d32f2f',
                    'color': '#b71c1c',
                    'weight': 1,
                    'fillOpacity': 0.6
                }

        folium.GeoJson(
            water_data,
            name='Champlain Water',
            style_function=water_style_function
        ).add_to(m)

        # County colors
        county_colors = {
            'Addison': '#66bb6a',
            'Bennington': '#42a5f5',
            'Caledonia': '#ab47bc',
            'Chittenden': '#ef5350',
            'Essex': '#ffa726',
            'Franklin': '#26c6da',
            'Grand Isle': '#7e57c2',
            'Lamoille': '#ec407a',
            'Orange': '#5c6bc0',
            'Orleans': '#9ccc65',
            'Rutland': '#29b6f6',
            'Washington': '#ff7043',
            'Windham': '#26a69a',
            'Windsor': '#ffd54f'
        }

        # Add towns on top - all with black borders
        def town_style_function(feature):
            props = feature['properties']
            county = props.get('county_name', 'Unknown')
            has_cutout = props.get('water_cutout_applied', False)

            return {
                'fillColor': county_colors.get(county, '#cccccc'),
                'color': '#000000',
                'weight': 2.5 if has_cutout else 1.5,
                'fillOpacity': 0.7
            }

        folium.GeoJson(
            towns_data,
            name='VT Towns',
            style_function=town_style_function
        ).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Towns Over Champlain HYDROIDs - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                <b>Towns:</b> {towns_metadata.get('total_towns', 0)} (colored by county)<br>
                <b>Water:</b> Blue (VT) and Red (NY)
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #000; font-weight: 600;
                                     font-size: 14px; display: flex; align-items: center; gap: 5px;">
            <span>←</span>
            <span>Back to Index</span>
        </a>
        '''
        m.get_root().html.add_child(folium.Element(back_button_html))

        # Save map
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output))

        print(f"✓ Saved to {output_path}")
        return str(output)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("Towns Over Champlain HYDROIDs Map Generator")
    print("=" * 60)

    maps_created = []

    result = create_towns_over_hydroids_map()
    if result:
        maps_created.append(result)

    result = create_towns_over_hydroids_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
