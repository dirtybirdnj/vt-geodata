#!/usr/bin/env python3
"""
Generate visualization maps for Champlain TIGER HYDROID data sources
Separate maps for VT and NY Champlain water features
"""

import folium
import json
from pathlib import Path


def create_vt_champlain_tiger_map(output_path: str = 'docs/vt_champlain_tiger.html'):
    """
    Create Vermont Champlain TIGER HYDROIDs map
    """
    print("\n" + "=" * 60)
    print("Creating: VT Champlain TIGER HYDROIDs Map")
    print("=" * 60)

    try:
        # Load VT Champlain TIGER data
        print("  Loading VT Champlain TIGER HYDROIDs data...")
        with open('docs/json/vt_champlain_tiger_hydroids.json', 'r') as f:
            vt_champlain = json.load(f)

        metadata = vt_champlain.get('metadata', {})
        print(f"  Features: {metadata.get('total_features', 'Unknown')}")
        print(f"  Total area: {metadata.get('total_area_sqkm', 'Unknown')} sq km")

        # Create map centered on Lake Champlain (VT side)
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Add water features
        folium.GeoJson(
            vt_champlain,
            name='VT Champlain Water',
            style_function=lambda x: {
                'fillColor': '#1976d2',
                'color': '#0d47a1',
                'weight': 2,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'HYDROID', 'area_sqkm'],
                aliases=['Name:', 'Hydro ID:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #1976d2;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #1976d2;">VT Champlain TIGER HYDROIDs</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                Water features touching Champlain Islands or VT coast<br>
                <b>{metadata.get('total_features', 0)} features</b> •
                <b>{metadata.get('total_area_sqkm', 0):.2f} sq km</b>
            </p>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Source: US Census TIGER/Line 2022 (Filtered by HYDROID)<br>
                Collection: Interactive selection from mashup map
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #1976d2; font-weight: 600;
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


def create_vt_champlain_tiger_vector_map(output_path: str = 'docs/vt_champlain_tiger_vector.html'):
    """
    Create vector-only version of VT Champlain TIGER map
    """
    print("\n" + "=" * 60)
    print("Creating: VT Champlain TIGER Vector-Only Map")
    print("=" * 60)

    try:
        # Load VT Champlain TIGER data
        print("  Loading VT Champlain TIGER HYDROIDs data...")
        with open('docs/json/vt_champlain_tiger_hydroids.json', 'r') as f:
            vt_champlain = json.load(f)

        metadata = vt_champlain.get('metadata', {})

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.5, -73.2],
            zoom_start=9,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Add water features with black outlines
        folium.GeoJson(
            vt_champlain,
            name='VT Champlain Water',
            style_function=lambda x: {
                'fillColor': '#1976d2',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">VT Champlain TIGER - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                {metadata.get('total_features', 0)} water features
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


def create_ny_champlain_tiger_map(output_path: str = 'docs/ny_champlain_tiger.html'):
    """
    Create New York Champlain TIGER HYDROIDs map
    """
    print("\n" + "=" * 60)
    print("Creating: NY Champlain TIGER HYDROIDs Map")
    print("=" * 60)

    try:
        # Load NY Champlain TIGER data
        print("  Loading NY Champlain TIGER HYDROIDs data...")
        with open('docs/json/ny_champlain_tiger_hydroids.json', 'r') as f:
            ny_champlain = json.load(f)

        metadata = ny_champlain.get('metadata', {})
        print(f"  Features: {metadata.get('total_features', 'Unknown')}")
        print(f"  Total area: {metadata.get('total_area_sqkm', 'Unknown')} sq km")

        # Create map centered on Lake Champlain (NY side)
        m = folium.Map(
            location=[44.3, -73.4],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Add water features
        folium.GeoJson(
            ny_champlain,
            name='NY Champlain Water',
            style_function=lambda x: {
                'fillColor': '#d32f2f',
                'color': '#b71c1c',
                'weight': 2,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'HYDROID', 'area_sqkm'],
                aliases=['Name:', 'Hydro ID:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #d32f2f;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #d32f2f;">NY Champlain TIGER HYDROIDs</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                Water features touching Lake Champlain on NY side<br>
                <b>{metadata.get('total_features', 0)} features</b> •
                <b>{metadata.get('total_area_sqkm', 0):.2f} sq km</b>
            </p>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Source: US Census TIGER/Line 2022 (Filtered by HYDROID)<br>
                Collection: Interactive selection from mashup map
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #d32f2f; font-weight: 600;
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


def create_ny_champlain_tiger_vector_map(output_path: str = 'docs/ny_champlain_tiger_vector.html'):
    """
    Create vector-only version of NY Champlain TIGER map
    """
    print("\n" + "=" * 60)
    print("Creating: NY Champlain TIGER Vector-Only Map")
    print("=" * 60)

    try:
        # Load NY Champlain TIGER data
        print("  Loading NY Champlain TIGER HYDROIDs data...")
        with open('docs/json/ny_champlain_tiger_hydroids.json', 'r') as f:
            ny_champlain = json.load(f)

        metadata = ny_champlain.get('metadata', {})

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.3, -73.4],
            zoom_start=9,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Add water features with black outlines
        folium.GeoJson(
            ny_champlain,
            name='NY Champlain Water',
            style_function=lambda x: {
                'fillColor': '#d32f2f',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">NY Champlain TIGER - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                {metadata.get('total_features', 0)} water features
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
    print("Champlain TIGER HYDROIDs Map Generator")
    print("=" * 60)

    maps_created = []

    # Create VT maps
    result = create_vt_champlain_tiger_map()
    if result:
        maps_created.append(result)

    result = create_vt_champlain_tiger_vector_map()
    if result:
        maps_created.append(result)

    # Create NY maps
    result = create_ny_champlain_tiger_map()
    if result:
        maps_created.append(result)

    result = create_ny_champlain_tiger_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
