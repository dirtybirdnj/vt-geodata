#!/usr/bin/env python3
"""
Generate visualization maps for VT towns with water cutouts
Shows before/after comparison
"""

import folium
import json
from pathlib import Path


def create_water_cutout_comparison_map(output_path: str = 'docs/vt_grand_isle_water_cutouts.html'):
    """
    Create comparison map showing original vs water-cutout town geometries
    """
    print("\n" + "=" * 60)
    print("Creating: Grand Isle Water Cutouts Comparison Map")
    print("=" * 60)

    try:
        # Load water cutout data
        print("  Loading water cutout data...")
        with open('docs/json/vt_grand_isle_water_cutouts.json', 'r') as f:
            cutout_data = json.load(f)

        # Load original towns for comparison
        print("  Loading original VT towns data...")
        with open('docs/json/vt_towns.json', 'r') as f:
            towns_data = json.load(f)

        metadata = cutout_data.get('metadata', {})
        print(f"  Towns: {metadata.get('total_towns', 'Unknown')}")
        print(f"  New total area: {metadata.get('new_area_sqkm', 0):.2f} sq km")

        # Create map centered on Grand Isle County
        m = folium.Map(
            location=[44.78, -73.3],
            zoom_start=11,
            tiles='OpenStreetMap'
        )

        # Add original towns (in red with low opacity)
        folium.GeoJson(
            {
                'type': 'FeatureCollection',
                'features': [f for f in towns_data['features'] if f['properties'].get('county_name') == 'Grand Isle']
            },
            name='Original Town Boundaries',
            style_function=lambda x: {
                'fillColor': '#ff0000',
                'color': '#8b0000',
                'weight': 1,
                'fillOpacity': 0.2
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'land_area_sqkm'],
                aliases=['Town (Original):', 'Original Land Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add new water-cutout towns (in green)
        folium.GeoJson(
            cutout_data,
            name='With Water Cutouts',
            style_function=lambda x: {
                'fillColor': '#2ecc71',
                'color': '#27ae60',
                'weight': 2,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'new_land_area_sqkm', 'water_removed_sqkm'],
                aliases=['Town:', 'New Area (sq km):', 'Area Difference (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add VT Champlain water for reference (in blue)
        print("  Loading VT Champlain water...")
        with open('docs/json/vt_champlain_tiger_hydroids.json', 'r') as f:
            water_data = json.load(f)

        folium.GeoJson(
            water_data,
            name='VT Champlain Water (TIGER)',
            style_function=lambda x: {
                'fillColor': '#3498db',
                'color': '#2980b9',
                'weight': 1,
                'fillOpacity': 0.4
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'area_sqkm'],
                aliases=['Water Feature:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 500px;
                    background-color: white; border: 2px solid #27ae60;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #27ae60;">Grand Isle County - Water Cutouts</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b style="color: #ff0000;">Red:</b> Original Census town boundaries (land only)<br>
                <b style="color: #2ecc71;">Green:</b> New geometries with water cut out<br>
                <b style="color: #3498db;">Blue:</b> VT Champlain TIGER water features<br>
            </p>
            <div style="margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 4px; font-size: 11px;">
                <b>Stats:</b> {metadata.get('total_towns', 0)} towns •
                {metadata.get('new_area_sqkm', 0):.2f} sq km total
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Method: Geometric difference (town polygons - water polygons)
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #27ae60; font-weight: 600;
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


def create_water_cutout_vector_map(output_path: str = 'docs/vt_grand_isle_water_cutouts_vector.html'):
    """
    Create vector-only version showing just the new island geometries
    """
    print("\n" + "=" * 60)
    print("Creating: Grand Isle Water Cutouts Vector-Only Map")
    print("=" * 60)

    try:
        # Load water cutout data
        print("  Loading water cutout data...")
        with open('docs/json/vt_grand_isle_water_cutouts.json', 'r') as f:
            cutout_data = json.load(f)

        metadata = cutout_data.get('metadata', {})

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.78, -73.3],
            zoom_start=11,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Add island shapes with different colors
        island_colors = {
            'Alburgh': '#e74c3c',
            'Grand Isle': '#3498db',
            'Isle La Motte': '#9b59b6',
            'North Hero': '#2ecc71',
            'South Hero': '#f39c12'
        }

        def style_function(feature):
            town_name = feature['properties'].get('NAME', 'Unknown')
            return {
                'fillColor': island_colors.get(town_name, '#95a5a6'),
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.7
            }

        folium.GeoJson(
            cutout_data,
            name='Champlain Islands',
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'new_land_area_sqkm'],
                aliases=['Island:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Champlain Islands - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure island geometries<br>
                {metadata.get('total_towns', 0)} islands with water cut out
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
    print("Grand Isle Water Cutouts Map Generator")
    print("=" * 60)

    maps_created = []

    result = create_water_cutout_comparison_map()
    if result:
        maps_created.append(result)

    result = create_water_cutout_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
