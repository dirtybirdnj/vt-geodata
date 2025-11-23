#!/usr/bin/env python3
"""
Generate mashup maps - third order transformations
Combining multiple processed data sources to identify gaps and create composite views
"""

import folium
import json
from pathlib import Path


def create_towns_over_champlain_map(output_path: str = 'docs/towns_over_champlain.html'):
    """
    Overlay VT towns on Lake Champlain NY & VT water map
    This helps identify the Champlain Islands and see what's missing
    """
    print("\n" + "=" * 60)
    print("Creating: VT Towns Over Lake Champlain Waters")
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

        # Load VT towns data
        print("  Loading VT towns data...")
        with open('docs/json/vt_towns.json', 'r') as f:
            vt_towns = json.load(f)

        print(f"  VT Big Lake features: {vt_big_lake['metadata']['features_count']}")
        print(f"  VT Rivers features: {vt_rivers['metadata']['features_count']}")
        print(f"  VT Small Ponds features: {vt_small_ponds['metadata']['features_count']}")
        print(f"  NY Lake Champlain features: {ny_water['metadata']['total_features']}")
        print(f"  VT Towns: {vt_towns['metadata']['total_towns']}")

        # Create map centered on Lake Champlain
        m = folium.Map(
            location=[44.5, -73.3],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Add water layers first (bottom)
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

        # Add VT towns layer on top with semi-transparent fill and strong borders
        # Highlight Grand Isle County in a different color
        def style_towns(feature):
            county = feature['properties'].get('county_name', 'Unknown')
            if county == 'Grand Isle':
                return {
                    'fillColor': '#ff6b6b',  # Red for Champlain Islands
                    'color': '#c92a2a',
                    'weight': 3,
                    'fillOpacity': 0.3
                }
            else:
                return {
                    'fillColor': '#66bb6a',
                    'color': '#2c5f2d',
                    'weight': 2,
                    'fillOpacity': 0.2
                }

        folium.GeoJson(
            vt_towns,
            name='VT Towns (Grand Isle in Red)',
            style_function=style_towns,
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'county_name', 'land_area_sqkm', 'water_area_sqkm'],
                aliases=['Town:', 'County:', 'Land Area (sq km):', 'Water Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title and legend
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 520px;
                    background-color: white; border: 2px solid #ff6b6b;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #c92a2a;">🔬 Third Order: Towns Over Champlain Waters</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b>Mashup visualization to identify data gaps</b><br>
                VT Towns overlaid on Lake Champlain water features<br>
                <b style="color: #c92a2a;">★ Grand Isle County (Champlain Islands) shown in RED</b><br>
                Notice: Island land areas appear small relative to surrounding water
            </p>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                <div style="font-size: 11px; font-weight: bold; margin-bottom: 5px;">Data Layers:</div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #0d47a1; border: 1px solid #01579b; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">VT - Lake Champlain Main Body</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #5c6bc0; border: 1px solid #3949ab; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">NY - Lake Champlain</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #ff6b6b; border: 3px solid #c92a2a; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">Grand Isle County (Champlain Islands)</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 15px; height: 15px; background: #66bb6a; border: 2px solid #2c5f2d; margin-right: 8px;"></div>
                    <span style="font-size: 11px;">Other VT Towns</span>
                </div>
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Third Order Transformation: Combining processed data sources
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #c92a2a; font-weight: 600;
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
    print("Mashup Map Generator - Third Order Transformations")
    print("Combining processed data sources for analysis")
    print("=" * 60)

    maps_created = []

    result = create_towns_over_champlain_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} mashup map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
