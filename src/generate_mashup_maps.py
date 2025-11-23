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

        # Add JSON display panel
        json_display_html = '''
        <style>
            .json-display {
                position: fixed;
                bottom: 10px;
                left: 10px;
                z-index: 9999;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                font-family: 'Courier New', monospace;
                font-size: 12px;
                max-width: 500px;
                max-height: 40vh;
                overflow-y: auto;
            }
            .json-display h4 {
                margin: 0 0 10px 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                color: #c92a2a;
            }
            .json-display pre {
                margin: 0;
                white-space: pre-wrap;
                word-break: break-all;
            }
        </style>
        <div class="json-display">
            <h4>Selected Features</h4>
            <pre id="json-output">[]</pre>
            <p style="font-size: 10px; color: #999; margin: 10px 0 0 0;">Click water features to select. They will turn pink.</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(json_display_html))

        # Add JavaScript for click handlers
        click_script = '''
        <script>
        // Track selected features
        const selectedFeatures = [];
        const featureLayerMap = new Map();

        // Function to update JSON display
        function updateJSONDisplay() {
            const jsonOutput = document.getElementById('json-output');
            if (selectedFeatures.length === 0) {
                jsonOutput.textContent = '[]';
            } else {
                jsonOutput.textContent = JSON.stringify(selectedFeatures, null, 2);
            }
        }

        // Wait for the page to fully load
        window.addEventListener('load', function() {
            // Find the map object - Folium creates it as a global variable
            let mapObj = null;

            // Search for the map object in window
            for (let key in window) {
                if (key.startsWith('map_') && window[key] instanceof L.Map) {
                    mapObj = window[key];
                    console.log('Found map object:', key);
                    break;
                }
            }

            if (!mapObj) {
                console.error('Could not find map object!');
                return;
            }

            // Add click handlers after a delay to ensure all layers are loaded
            setTimeout(function() {
                console.log('Setting up click handlers...');
                let layerCount = 0;

                mapObj.eachLayer(function(layer) {
                // Check if this is a GeoJSON layer group
                if (layer instanceof L.GeoJSON) {
                    console.log('Found GeoJSON layer group');

                    // Iterate through each feature layer in the group
                    layer.eachLayer(function(featureLayer) {
                        if (featureLayer.feature && featureLayer.feature.properties) {
                            const props = featureLayer.feature.properties;
                            layerCount++;

                            // Store original style
                            const originalStyle = {
                                fillColor: featureLayer.options.fillColor,
                                fillOpacity: featureLayer.options.fillOpacity,
                                color: featureLayer.options.color,
                                weight: featureLayer.options.weight
                            };

                            featureLayer.originalStyle = originalStyle;

                            // Store layer reference by HYDROID if it exists
                            if (props.HYDROID) {
                                featureLayerMap.set(props.HYDROID, featureLayer);
                            }

                            // Add click handler
                            featureLayer.on('click', function(e) {
                                L.DomEvent.stopPropagation(e);

                                const hydroid = props.HYDROID;
                                const name = props.FULLNAME || props.NAME || 'Unnamed';

                                // Skip if no HYDROID (probably a town layer)
                                if (!hydroid) {
                                    console.log('Clicked non-water feature:', name);
                                    return;
                                }

                                console.log('Clicked water feature:', name, hydroid);

                                // Check if already selected
                                const existingIndex = selectedFeatures.findIndex(f => f.hydroid === hydroid);

                                if (existingIndex !== -1) {
                                    // Deselect - remove from list and reset color
                                    console.log('Deselecting:', name);
                                    selectedFeatures.splice(existingIndex, 1);
                                    featureLayer.setStyle(featureLayer.originalStyle);
                                } else {
                                    // Select - add to list and make pink
                                    console.log('Selecting:', name);
                                    featureLayer.setStyle({
                                        fillColor: '#ff1493',  // Deep pink
                                        fillOpacity: 0.8,
                                        color: '#c90076',
                                        weight: 2
                                    });

                                    selectedFeatures.push({
                                        hydroid: hydroid,
                                        name: name,
                                        area_sqkm: props.area_sqkm || 0,
                                        source: props.MTFCC ? 'Census' : 'VT OpenData',
                                        timestamp: new Date().toISOString()
                                    });
                                }

                                updateJSONDisplay();
                            });
                        }
                    });
                }
            });

            console.log('Click handlers attached to', layerCount, 'feature layers');
            }, 1000);  // Wait 1 second after page load for all layers to be added
        });
        </script>
        '''
        m.get_root().html.add_child(folium.Element(click_script))

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


def create_towns_over_champlain_vector_map(output_path: str = 'docs/towns_over_champlain_vector.html'):
    """
    Vector-only version: VT Towns Over Lake Champlain Waters
    """
    print("\n" + "=" * 60)
    print("Creating: VT Towns Over Champlain Waters (Vector Only)")
    print("=" * 60)

    try:
        # Load same data sources
        print("  Loading data sources...")
        with open('docs/json/champlain_big_lake.json', 'r') as f:
            vt_big_lake = json.load(f)
        with open('docs/json/champlain_rivers.json', 'r') as f:
            vt_rivers = json.load(f)
        with open('docs/json/champlain_small_ponds.json', 'r') as f:
            vt_small_ponds = json.load(f)
        with open('docs/json/ny_lake_champlain_water.json', 'r') as f:
            ny_water = json.load(f)
        with open('docs/json/vt_towns.json', 'r') as f:
            vt_towns = json.load(f)

        # Create map with NO tiles (vector only)
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

        # Add water layers with black outlines
        folium.GeoJson(
            vt_big_lake,
            name='VT - Lake Champlain',
            style_function=lambda x: {
                'fillColor': '#0d47a1',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.8
            }
        ).add_to(m)

        folium.GeoJson(
            vt_rivers,
            name='VT - Rivers',
            style_function=lambda x: {
                'fillColor': '#4fc3f7',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        folium.GeoJson(
            vt_small_ponds,
            name='VT - Ponds',
            style_function=lambda x: {
                'fillColor': '#b3e5fc',
                'color': '#000000',
                'weight': 0.5,
                'fillOpacity': 0.6
            }
        ).add_to(m)

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

        # Add VT towns on top
        def style_towns(feature):
            county = feature['properties'].get('county_name', 'Unknown')
            if county == 'Grand Isle':
                return {
                    'fillColor': '#ff6b6b',
                    'color': '#000000',
                    'weight': 3,
                    'fillOpacity': 0.4
                }
            else:
                return {
                    'fillColor': '#66bb6a',
                    'color': '#000000',
                    'weight': 2,
                    'fillOpacity': 0.3
                }

        folium.GeoJson(
            vt_towns,
            name='VT Towns',
            style_function=style_towns
        ).add_to(m)

        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 450px;
                    background-color: white; border: 2px solid #000;
                    border-radius: 5px; z-index: 9999; padding: 10px;">
            <h4 style="margin: 0;">Towns Over Champlain - Vector Only</h4>
            <p style="margin: 5px 0 0 0; font-size: 12px;">
                No base map - pure vector data visualization<br>
                Grand Isle County (Champlain Islands) in red
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
    print("Mashup Map Generator - Third Order Transformations")
    print("Combining processed data sources for analysis")
    print("=" * 60)

    maps_created = []

    result = create_towns_over_champlain_map()
    if result:
        maps_created.append(result)

    result = create_towns_over_champlain_vector_map()
    if result:
        maps_created.append(result)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(maps_created)} mashup map(s)")
    print("=" * 60)
    for map_path in maps_created:
        print(f"  ✓ {map_path}")
