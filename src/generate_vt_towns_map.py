#!/usr/bin/env python3
"""
Generate Vermont Towns/Cities boundary maps
"""

import folium
import json
from pathlib import Path


def create_vt_towns_map(output_path: str = 'docs/vt_towns.html'):
    """
    Create Vermont towns boundary map with OpenStreetMap base layer
    """
    print("\n" + "=" * 60)
    print("Creating: Vermont Towns/Cities Boundary Map")
    print("=" * 60)

    try:
        # Load VT towns data
        print("  Loading Vermont towns data...")
        with open('docs/json/vt_towns.json', 'r') as f:
            vt_towns = json.load(f)

        print(f"  Towns/Cities: {vt_towns['metadata']['total_towns']}")

        # Create map centered on Vermont
        m = folium.Map(
            location=[44.0, -72.7],
            zoom_start=8,
            tiles='OpenStreetMap'
        )

        # Color palette for counties (14 colors)
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

        # Add towns with color by county
        def style_function(feature):
            county = feature['properties'].get('county_name', 'Unknown')
            return {
                'fillColor': county_colors.get(county, '#cccccc'),
                'color': '#2c5f2d',
                'weight': 1.5,
                'fillOpacity': 0.4
            }

        folium.GeoJson(
            vt_towns,
            name='Vermont Towns',
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'county_name', 'land_area_sqkm', 'water_area_sqkm', 'total_area_sqkm'],
                aliases=['Town:', 'County:', 'Land Area (sq km):', 'Water Area (sq km):', 'Total Area (sq km):'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title and legend
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 500px;
                    background-color: white; border: 2px solid #2c5f2d;
                    border-radius: 8px; z-index: 9999; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0; color: #2c5f2d;">Vermont - Towns & Cities</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                All 256 Vermont towns and cities with municipal boundaries<br>
                <b>Colored by county</b> - Hover over any town for details
            </p>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                <div style="font-size: 11px; font-weight: bold; margin-bottom: 5px;">Counties:</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3px; font-size: 10px;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #66bb6a; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Addison</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #42a5f5; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Bennington</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #ab47bc; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Caledonia</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #ef5350; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Chittenden</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #ffa726; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Essex</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #26c6da; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Franklin</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #7e57c2; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Grand Isle</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #ec407a; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Lamoille</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #5c6bc0; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Orange</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #9ccc65; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Orleans</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #29b6f6; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Rutland</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #ff7043; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Washington</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #26a69a; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Windham</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #ffd54f; border: 1px solid #2c5f2d; margin-right: 5px;"></div>
                        <span>Windsor</span>
                    </div>
                </div>
            </div>
            <p style="margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;">
                Source: US Census TIGER/Line County Subdivisions 2023
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add back button
        back_button_html = '''
        <a href="index.html" style="position: fixed; top: 10px; left: 10px; background: white;
                                     padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                                     z-index: 9999; text-decoration: none; color: #2c5f2d; font-weight: 600;
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


def create_vt_towns_vector_map(output_path: str = 'docs/vt_towns_vector.html'):
    """
    Create vector-only version of Vermont towns map
    """
    print("\n" + "=" * 60)
    print("Creating: Vermont Towns Vector-Only Map")
    print("=" * 60)

    try:
        # Load VT towns data
        print("  Loading Vermont towns data...")
        with open('docs/json/vt_towns.json', 'r') as f:
            vt_towns = json.load(f)

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

        # County colors (same as above)
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

        # Add towns with black outlines
        def style_function(feature):
            county = feature['properties'].get('county_name', 'Unknown')
            return {
                'fillColor': county_colors.get(county, '#cccccc'),
                'color': '#000000',
                'weight': 1.5,
                'fillOpacity': 0.6
            }

        folium.GeoJson(
            vt_towns,
            name='Vermont Towns',
            style_function=style_function
        ).add_to(m)

        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Vermont Towns - Vector Data Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                256 Vermont towns colored by county<br>
                <b>Click any town to view data</b>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add JSON display panel and click functionality (multi-select like towns_over_champlain)
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

                        // Store layer reference
                        window.allLayers.push(featureLayer);

                        // Store original style based on county
                        featureLayer.originalStyle = {
                            fillColor: countyColors[county] || '#cccccc',
                            color: '#000000',
                            weight: 1.5,
                            fillOpacity: 0.6
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
    print("Vermont Towns Map Generator")
    print("=" * 60)

    maps_created = []

    result = create_vt_towns_map()
    if result:
        maps_created.append(result)

    result = create_vt_towns_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
