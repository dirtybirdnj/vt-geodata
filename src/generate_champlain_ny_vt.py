#!/usr/bin/env python3
"""
Generate Lake Champlain NY and VT combined map
Combines categorized VT water data with NY Lake Champlain data
"""

import folium
import json
from pathlib import Path


def create_champlain_ny_vt_map(output_path: str = 'docs/champlain_ny_vt.html'):
    """
    Create combined Lake Champlain map with VT categorized water and NY water
    """
    print("\n" + "=" * 60)
    print("Creating: Lake Champlain NY and VT Combined Map")
    print("=" * 60)

    try:
        # Load VT categorized water data
        print("  Loading VT categorized water data...")
        with open('docs/json/champlain_big_lake.json', 'r') as f:
            vt_big_lake = json.load(f)

        with open('docs/json/champlain_rivers.json', 'r') as f:
            vt_rivers = json.load(f)

        with open('docs/json/champlain_small_ponds.json', 'r') as f:
            vt_small_ponds = json.load(f)

        # Load NY Lake Champlain water data
        print("  Loading NY Lake Champlain water data...")
        with open('docs/json/ny_lake_champlain_water.json', 'r') as f:
            ny_water = json.load(f)

        # Load state boundaries for context
        print("  Loading state boundaries...")
        with open('docs/json/vermont_boundary.json', 'r') as f:
            vt_boundary = json.load(f)

        with open('docs/json/ny_boundary.json', 'r') as f:
            ny_boundary = json.load(f)

        print(f"  VT Big Lake features: {vt_big_lake['metadata']['features_count']}")
        print(f"  VT Rivers features: {vt_rivers['metadata']['features_count']}")
        print(f"  VT Small Ponds features: {vt_small_ponds['metadata']['features_count']}")
        print(f"  NY Lake Champlain features: {ny_water['metadata']['total_features']}")

        # Create map centered on Lake Champlain
        m = folium.Map(
            location=[44.5, -73.3],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Add state boundaries (subtle)
        folium.GeoJson(
            vt_boundary,
            name='Vermont Boundary',
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#2c5f2d',
                'weight': 2,
                'fillOpacity': 0,
                'dashArray': '5, 5'
            }
        ).add_to(m)

        folium.GeoJson(
            ny_boundary,
            name='New York Boundary',
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#1a237e',
                'weight': 2,
                'fillOpacity': 0,
                'dashArray': '5, 5'
            }
        ).add_to(m)

        # Add VT water features (categorized)
        folium.GeoJson(
            vt_big_lake,
            name='VT - Lake Champlain Main Body',
            style_function=lambda x: {
                'fillColor': '#0d47a1',
                'color': '#01579b',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'area_sqkm'],
                aliases=['Name:', 'Area (sq km):']
            )
        ).add_to(m)

        folium.GeoJson(
            vt_rivers,
            name='VT - Rivers & Streams',
            style_function=lambda x: {
                'fillColor': '#4fc3f7',
                'color': '#0288d1',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'area_sqkm'],
                aliases=['Name:', 'Area (sq km):']
            )
        ).add_to(m)

        folium.GeoJson(
            vt_small_ponds,
            name='VT - Small Ponds & Lakes',
            style_function=lambda x: {
                'fillColor': '#b3e5fc',
                'color': '#4fc3f7',
                'weight': 0.5,
                'fillOpacity': 0.5
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'area_sqkm'],
                aliases=['Name:', 'Area (sq km):']
            )
        ).add_to(m)

        # Add NY Lake Champlain water
        folium.GeoJson(
            ny_water,
            name='NY - Lake Champlain',
            style_function=lambda x: {
                'fillColor': '#5c6bc0',
                'color': '#3949ab',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME'],
                aliases=['Name:']
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title and legend
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 500px;
                    background-color: white; border: 2px solid #1e88e5;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #0d47a1;">Lake Champlain - NY & VT Combined</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                Complete Lake Champlain basin with categorized water features<br>
                <b>Vermont:</b> Categorized into main lake, rivers, and ponds<br>
                <b>New York:</b> Lake Champlain water features
            </p>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                <div style="font-size: 11px; font-weight: bold; margin-bottom: 5px;">Legend:</div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #0d47a1; border: 1px solid #01579b; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">VT - Lake Champlain Main Body</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #4fc3f7; border: 1px solid #0288d1; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">VT - Rivers & Streams</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #b3e5fc; border: 1px solid #4fc3f7; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">VT - Small Ponds & Lakes</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #5c6bc0; border: 1px solid #3949ab; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">NY - Lake Champlain</span>
                </div>
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Sources: VT Census TIGER 2022 (categorized), NY Census TIGER 2022
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #1e88e5; font-weight: 600;
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


def create_champlain_ny_vt_vector_map(output_path: str = 'docs/champlain_ny_vt_vector.html'):
    """
    Create vector-only version of Lake Champlain NY and VT map
    """
    print("\n" + "=" * 60)
    print("Creating: Lake Champlain NY and VT Vector-Only Map")
    print("=" * 60)

    try:
        # Load VT categorized water data
        print("  Loading VT categorized water data...")
        with open('docs/json/champlain_big_lake.json', 'r') as f:
            vt_big_lake = json.load(f)

        with open('docs/json/champlain_rivers.json', 'r') as f:
            vt_rivers = json.load(f)

        with open('docs/json/champlain_small_ponds.json', 'r') as f:
            vt_small_ponds = json.load(f)

        # Load NY Lake Champlain water data
        print("  Loading NY Lake Champlain water data...")
        with open('docs/json/ny_lake_champlain_water.json', 'r') as f:
            ny_water = json.load(f)

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.5, -73.3],
            zoom_start=9,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Add VT water features (categorized) with black outlines
        folium.GeoJson(
            vt_big_lake,
            name='VT - Lake Champlain Main Body',
            style_function=lambda x: {
                'fillColor': '#0d47a1',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            }
        ).add_to(m)

        folium.GeoJson(
            vt_rivers,
            name='VT - Rivers & Streams',
            style_function=lambda x: {
                'fillColor': '#4fc3f7',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        folium.GeoJson(
            vt_small_ponds,
            name='VT - Small Ponds & Lakes',
            style_function=lambda x: {
                'fillColor': '#b3e5fc',
                'color': '#000000',
                'weight': 0.5,
                'fillOpacity': 0.6
            }
        ).add_to(m)

        # Add NY Lake Champlain water
        folium.GeoJson(
            ny_water,
            name='NY - Lake Champlain',
            style_function=lambda x: {
                'fillColor': '#5c6bc0',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            }
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Lake Champlain NY & VT - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                VT: Categorized water features | NY: Lake Champlain water
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
    print("Lake Champlain NY & VT Map Generator")
    print("Combining categorized VT water with NY Lake Champlain data")
    print("=" * 60)

    maps_created = []

    result = create_champlain_ny_vt_map()
    if result:
        maps_created.append(result)

    result = create_champlain_ny_vt_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
