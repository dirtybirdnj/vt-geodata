#!/usr/bin/env python3
"""
Generate visualization maps for combined NY/VT Champlain TIGER HYDROIDs
"""

import folium
import json
from pathlib import Path


def create_combined_champlain_map(output_path: str = 'docs/champlain_tiger_hydroids_combined.html'):
    """
    Create combined NY/VT Champlain TIGER HYDROIDs map
    """
    print("\n" + "=" * 60)
    print("Creating: Combined Champlain TIGER HYDROIDs Map")
    print("=" * 60)

    try:
        # Load combined data
        print("  Loading combined Champlain TIGER HYDROIDs...")
        with open('docs/json/champlain_tiger_hydroids_combined.json', 'r') as f:
            combined_data = json.load(f)

        metadata = combined_data.get('metadata', {})
        print(f"  Total features: {metadata.get('total_features', 'Unknown')}")
        print(f"  Total area: {metadata.get('total_area_sqkm', 'Unknown')} sq km")

        # Create map centered on Lake Champlain
        m = folium.Map(
            location=[44.4, -73.3],
            zoom_start=9,
            tiles='OpenStreetMap'
        )

        # Style function - VT in blue, NY in red
        def style_function(feature):
            state = feature['properties'].get('state', 'Unknown')
            if state == 'VT':
                return {
                    'fillColor': '#1976d2',
                    'color': '#0d47a1',
                    'weight': 2,
                    'fillOpacity': 0.6
                }
            else:  # NY
                return {
                    'fillColor': '#d32f2f',
                    'color': '#b71c1c',
                    'weight': 2,
                    'fillOpacity': 0.6
                }

        # Add water features
        folium.GeoJson(
            combined_data,
            name='Champlain Water',
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['FULLNAME', 'HYDROID', 'state', 'area_sqkm'],
                aliases=['Name:', 'Hydro ID:', 'State:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 480px;
                    background-color: white; border: 2px solid #5c6bc0;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #5c6bc0;">Lake Champlain TIGER HYDROIDs (Combined)</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b style="color: #1976d2;">VT (Blue):</b> {metadata.get('vt_features', 0)} features ({metadata.get('vt_area_sqkm', 0):.2f} sq km)<br>
                <b style="color: #d32f2f;">NY (Red):</b> {metadata.get('ny_features', 0)} features ({metadata.get('ny_area_sqkm', 0):.2f} sq km)
            </p>
            <div style="margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 4px; font-size: 11px;">
                <b>Total:</b> {metadata.get('total_features', 0)} water features •
                {metadata.get('total_area_sqkm', 0):.2f} sq km
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Source: US Census TIGER/Line 2022 (Combined VT + NY HYDROIDs)
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


def create_combined_champlain_vector_map(output_path: str = 'docs/champlain_tiger_hydroids_combined_vector.html'):
    """
    Create vector-only version of combined NY/VT map
    """
    print("\n" + "=" * 60)
    print("Creating: Combined Champlain TIGER Vector Map")
    print("=" * 60)

    try:
        # Load combined data
        print("  Loading combined Champlain TIGER HYDROIDs...")
        with open('docs/json/champlain_tiger_hydroids_combined.json', 'r') as f:
            combined_data = json.load(f)

        metadata = combined_data.get('metadata', {})

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.4, -73.3],
            zoom_start=9,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

        # Style function - VT in blue, NY in red
        def style_function(feature):
            state = feature['properties'].get('state', 'Unknown')
            if state == 'VT':
                return {
                    'fillColor': '#1976d2',
                    'color': '#000000',
                    'weight': 2,
                    'fillOpacity': 0.7
                }
            else:  # NY
                return {
                    'fillColor': '#d32f2f',
                    'color': '#000000',
                    'weight': 2,
                    'fillOpacity': 0.7
                }

        folium.GeoJson(
            combined_data,
            name='Champlain Water',
            style_function=style_function
        ).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 420px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Champlain TIGER HYDROIDs - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector visualization<br>
                <b style="color: #1976d2;">Blue:</b> {metadata.get('vt_features', 0)} VT features •
                <b style="color: #d32f2f;">Red:</b> {metadata.get('ny_features', 0)} NY features
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
    print("Combined Champlain TIGER HYDROIDs Map Generator")
    print("=" * 60)

    maps_created = []

    result = create_combined_champlain_map()
    if result:
        maps_created.append(result)

    result = create_combined_champlain_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
