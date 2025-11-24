#!/usr/bin/env python3
"""
Generate visualization maps for complete VT towns with water cutouts
"""

import folium
import json
from pathlib import Path


def create_vt_towns_cutout_map(output_path: str = 'docs/vt_towns_with_water_cutouts.html'):
    """
    Create complete VT towns map with water-trimmed towns highlighted
    """
    print("\n" + "=" * 60)
    print("Creating: VT Towns with Water Cutouts Map")
    print("=" * 60)

    try:
        # Load water cutout data
        print("  Loading VT towns with water cutouts...")
        with open('docs/json/vt_towns_with_water_cutouts.json', 'r') as f:
            towns_data = json.load(f)

        metadata = towns_data.get('metadata', {})
        print(f"  Total towns: {metadata.get('total_towns', 'Unknown')}")
        print(f"  Towns with cutouts: {metadata.get('towns_with_cutouts', 'Unknown')}")

        # Create map centered on Vermont
        m = folium.Map(
            location=[44.0, -72.7],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

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

        # Style function - all towns use county colors, cutout towns have thicker border
        def style_function(feature):
            props = feature['properties']
            county = props.get('county_name', 'Unknown')
            has_cutout = props.get('water_cutout_applied', False)

            if has_cutout:
                # Water-cutout towns in county color with thicker border
                return {
                    'fillColor': county_colors.get(county, '#cccccc'),
                    'color': '#27ae60',
                    'weight': 2.5,
                    'fillOpacity': 0.8
                }
            else:
                # Regular towns in county colors
                return {
                    'fillColor': county_colors.get(county, '#cccccc'),
                    'color': '#2c5f2d',
                    'weight': 1,
                    'fillOpacity': 0.4
                }

        # Add towns
        folium.GeoJson(
            towns_data,
            name='Vermont Towns',
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'county_name', 'water_cutout_applied', 'new_land_area_sqkm'],
                aliases=['Town:', 'County:', 'Water Cutout:', 'Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add interactive selection panel
        interactive_script = '''
        <div id="jsonDisplay" style="position: fixed; bottom: 20px; right: 20px; width: 400px; max-height: 400px;
                                      background-color: white; border: 2px solid #000; border-radius: 5px;
                                      z-index: 9999; padding: 15px; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-size: 14px;">Selected Towns</h4>
                <button onclick="clearAllSelections()"
                        style="background: #000; color: white; border: none; padding: 5px 10px;
                               border-radius: 3px; cursor: pointer; font-size: 12px;">Clear All</button>
            </div>
            <div style="font-size: 9px; color: #666; margin-bottom: 8px; font-style: italic;">
                Click towns to select. Click again to deselect. Format: "GEOID": "NAME"
            </div>
            <pre id="jsonContent" style="margin: 0; font-size: 10px; white-space: pre-wrap;
                                         word-wrap: break-word; background: #f5f5f5; padding: 10px;
                                         border-radius: 3px; max-height: 280px; overflow-y: auto;">{}</pre>
        </div>

        <script>
        // Track selected features as { "GEOID": "NAME" }
        const selectedFeatures = {};

        function updateJSONDisplay() {
            const jsonContent = document.getElementById('jsonContent');
            jsonContent.textContent = JSON.stringify(selectedFeatures, null, 2);
        }

        function clearAllSelections() {
            // Reset all selected layers
            Object.keys(selectedFeatures).forEach(geoid => {
                delete selectedFeatures[geoid];
            });

            // Reset all layer styles
            if (window.allLayers) {
                window.allLayers.forEach(featureLayer => {
                    featureLayer.setStyle(featureLayer.originalStyle);
                });
            }

            updateJSONDisplay();
        }

        window.addEventListener('load', function() {
            // Find the Folium map object
            let mapObj = null;
            for (let key in window) {
                if (key.startsWith('map_') && window[key] instanceof L.Map) {
                    mapObj = window[key];
                    break;
                }
            }

            if (!mapObj) {
                console.error('Could not find map object');
                return;
            }

            // Store all layers globally for clear function
            window.allLayers = [];

            // County colors (must match the style_function in Python)
            const countyColors = {
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
            };

            // Iterate through all layers to find GeoJSON layers
            mapObj.eachLayer(function(layer) {
                if (layer instanceof L.GeoJSON) {
                    // Iterate through individual features
                    layer.eachLayer(function(featureLayer) {
                        const props = featureLayer.feature.properties;
                        const county = props.county_name || 'Unknown';
                        const geoid = props.GEOID || 'Unknown';
                        const name = props.NAME || 'Unnamed';
                        const hasCutout = props.water_cutout_applied || false;

                        // Store layer reference
                        window.allLayers.push(featureLayer);

                        // Store original style based on county and cutout status
                        featureLayer.originalStyle = {
                            fillColor: countyColors[county] || '#cccccc',
                            color: '#27ae60',
                            weight: hasCutout ? 2.5 : 1,
                            fillOpacity: hasCutout ? 0.8 : 0.4
                        };

                        // Add click handler
                        featureLayer.on('click', function(e) {
                            L.DomEvent.stopPropagation(e);

                            // Check if already selected
                            if (selectedFeatures[geoid]) {
                                // Deselect
                                delete selectedFeatures[geoid];
                                featureLayer.setStyle(featureLayer.originalStyle);
                            } else {
                                // Select
                                selectedFeatures[geoid] = name;
                                featureLayer.setStyle({
                                    fillColor: '#ff1493',
                                    fillOpacity: 0.8,
                                    color: '#c90076',
                                    weight: 2
                                });
                            }

                            updateJSONDisplay();
                        });

                        // Add hover effect
                        featureLayer.on('mouseover', function(e) {
                            if (!selectedFeatures[geoid]) {
                                featureLayer.setStyle({
                                    fillOpacity: 0.8,
                                    weight: 2
                                });
                            }
                        });

                        featureLayer.on('mouseout', function(e) {
                            if (!selectedFeatures[geoid]) {
                                featureLayer.setStyle(featureLayer.originalStyle);
                            }
                        });
                    });
                }
            });
        });
        </script>
        '''
        m.get_root().html.add_child(folium.Element(interactive_script))

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 520px;
                    background-color: white; border: 2px solid #27ae60;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #27ae60;">Vermont Towns - Complete with Water Cutouts</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b style="color: #27ae60;">Green Border:</b> {metadata.get('towns_with_cutouts', 0)} towns with water cutouts (Champlain shoreline)<br>
                <b style="color: #666;">Regular Border:</b> {metadata.get('towns_unchanged', 0)} towns with original Census boundaries<br>
                <b>All towns colored by county</b> • <b style="color: #ff1493;">Click towns to select!</b>
            </p>
            <div style="margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 4px; font-size: 11px;">
                <b>Water Removed:</b> {metadata.get('water_removed_sqkm', 0):.2f} sq km from {metadata.get('towns_with_cutouts', 0)} towns
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Complete 256-town dataset with accurate Champlain shoreline boundaries
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


def create_vt_towns_cutout_vector_map(output_path: str = 'docs/vt_towns_with_water_cutouts_vector.html'):
    """
    Create vector-only version of VT towns with water cutouts
    """
    print("\n" + "=" * 60)
    print("Creating: VT Towns with Water Cutouts Vector Map")
    print("=" * 60)

    try:
        # Load water cutout data
        print("  Loading VT towns with water cutouts...")
        with open('docs/json/vt_towns_with_water_cutouts.json', 'r') as f:
            towns_data = json.load(f)

        metadata = towns_data.get('metadata', {})

        # Create map with no tiles (vector only)
        m = folium.Map(
            location=[44.0, -72.7],
            zoom_start=8,
            tiles=None,
            attr='Vector Data Only'
        )

        # Add white background
        m.get_root().html.add_child(folium.Element(
            '<style>body { background-color: white; } .leaflet-container { background: white; }</style>'
        ))

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

        # Style function - all towns use county colors, cutout towns have thicker border
        def style_function(feature):
            props = feature['properties']
            county = props.get('county_name', 'Unknown')
            has_cutout = props.get('water_cutout_applied', False)

            if has_cutout:
                return {
                    'fillColor': county_colors.get(county, '#cccccc'),
                    'color': '#27ae60',
                    'weight': 3,
                    'fillOpacity': 0.8
                }
            else:
                return {
                    'fillColor': county_colors.get(county, '#cccccc'),
                    'color': '#000000',
                    'weight': 1.5,
                    'fillOpacity': 0.6
                }

        folium.GeoJson(
            towns_data,
            name='Vermont Towns',
            style_function=style_function
        ).add_to(m)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Vermont Towns - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                Complete 256-town dataset - all colored by county<br>
                <b style="color: #27ae60;">Green Border:</b> {metadata.get('towns_with_cutouts', 0)} towns with water cutouts<br>
                <b>Black Border:</b> {metadata.get('towns_unchanged', 0)} unchanged towns
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
    print("VT Towns with Water Cutouts Map Generator")
    print("=" * 60)

    maps_created = []

    result = create_vt_towns_cutout_map()
    if result:
        maps_created.append(result)

    result = create_vt_towns_cutout_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
