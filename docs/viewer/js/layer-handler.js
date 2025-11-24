/**
 * Layer Handler
 * Load and style GeoJSON layers
 */

class LayerHandler {
    constructor(map, config) {
        this.map = map;
        this.config = config;
        this.layers = new Map();
        this.layerControl = null;
    }

    /**
     * Load all layers from configuration
     */
    async loadLayers() {
        const layers = this.config.layers || [];

        // Sort by zIndex to ensure proper ordering
        const sortedLayers = [...layers].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));

        for (const layerConfig of sortedLayers) {
            try {
                await this.loadLayer(layerConfig);
            } catch (error) {
                console.error(`Error loading layer ${layerConfig.id}:`, error);
            }
        }

        // Add layer control if enabled
        if (this.config.features.layerControl.enabled) {
            this.addLayerControl();
        }

        // Fit bounds to all layers
        this.fitMapToLayers();
    }

    /**
     * Load a single GeoJSON layer
     */
    async loadLayer(layerConfig) {
        const response = await fetch(layerConfig.source);
        if (!response.ok) {
            throw new Error(`Failed to load ${layerConfig.source}: ${response.status}`);
        }

        const geojsonData = await response.json();

        // Create Leaflet GeoJSON layer
        const layer = L.geoJSON(geojsonData, {
            style: (feature) => this.getFeatureStyle(feature, layerConfig),
            onEachFeature: (feature, layer) => this.onEachFeature(feature, layer, layerConfig)
        });

        // Store layer reference
        this.layers.set(layerConfig.id, {
            layer: layer,
            config: layerConfig,
            data: geojsonData
        });

        // Add to map
        layer.addTo(this.map);

        return layer;
    }

    /**
     * Get style for a feature
     */
    getFeatureStyle(feature, layerConfig) {
        const styleConfig = layerConfig.style;

        if (!styleConfig) {
            return {}; // Use default Leaflet styles
        }

        // Static style
        if (styleConfig.type === 'static' || !styleConfig.type) {
            return {
                fillColor: styleConfig.fillColor || '#3388ff',
                color: styleConfig.color || '#3388ff',
                weight: styleConfig.weight || 2,
                fillOpacity: styleConfig.fillOpacity || 0.5,
                opacity: styleConfig.opacity || 1.0
            };
        }

        // Function-based style (property-based coloring)
        if (styleConfig.type === 'function') {
            const property = styleConfig.property;
            const propertyValue = feature.properties[property];

            // Check for special rules first
            if (styleConfig.specialRules) {
                const specialProp = styleConfig.specialRules.property;
                const specialValue = styleConfig.specialRules.value;
                if (feature.properties[specialProp] === specialValue) {
                    return styleConfig.specialRules.style;
                }
            }

            // Check rules map
            if (styleConfig.rules && styleConfig.rules[propertyValue]) {
                return styleConfig.rules[propertyValue];
            }

            // Check color map
            if (styleConfig.colorMap) {
                const colorMap = this.config.colorMaps[styleConfig.colorMap] || {};
                const color = colorMap[propertyValue];

                if (color) {
                    return {
                        fillColor: color,
                        color: styleConfig.borderColor || '#000',
                        weight: styleConfig.weight || 2,
                        fillOpacity: styleConfig.fillOpacity || 0.6,
                        opacity: styleConfig.opacity || 1.0
                    };
                }
            }

            // Fallback to default
            return {
                fillColor: styleConfig.defaultColor || '#cccccc',
                color: styleConfig.borderColor || '#000',
                weight: styleConfig.weight || 2,
                fillOpacity: styleConfig.fillOpacity || 0.6,
                opacity: styleConfig.opacity || 1.0
            };
        }

        return {};
    }

    /**
     * Setup feature interactions
     */
    onEachFeature(feature, layer, layerConfig) {
        // Add tooltip if configured
        if (layerConfig.tooltip) {
            const tooltipContent = this.buildTooltip(feature, layerConfig.tooltip);
            layer.bindTooltip(tooltipContent);
        }

        // Store layer config on the layer for interaction handlers
        layer.layerConfig = layerConfig;
        layer.featureData = feature;
    }

    /**
     * Build tooltip HTML from feature properties
     */
    buildTooltip(feature, tooltipConfig) {
        const fields = tooltipConfig.fields || [];
        const aliases = tooltipConfig.aliases || fields;

        let html = '<table class="foliumtooltip"><tbody>';

        fields.forEach((field, index) => {
            const value = feature.properties[field];
            const alias = aliases[index] || field;

            if (value !== undefined && value !== null) {
                html += `<tr><th>${alias}</th><td>${value}</td></tr>`;
            }
        });

        html += '</tbody></table>';
        return html;
    }

    /**
     * Add layer control
     */
    addLayerControl() {
        const overlays = {};

        this.layers.forEach((layerInfo, id) => {
            const name = layerInfo.config.name || id;
            overlays[name] = layerInfo.layer;
        });

        const controlConfig = this.config.features.layerControl;
        this.layerControl = L.control.layers(null, overlays, {
            position: controlConfig.position,
            collapsed: controlConfig.collapsed
        });

        this.layerControl.addTo(this.map);
    }

    /**
     * Fit map to show all layers
     */
    fitMapToLayers() {
        const bounds = [];

        this.layers.forEach((layerInfo) => {
            const layerBounds = layerInfo.layer.getBounds();
            if (layerBounds.isValid()) {
                bounds.push(layerBounds);
            }
        });

        if (bounds.length > 0) {
            const combinedBounds = bounds.reduce((acc, bound) => acc.extend(bound));
            this.map.fitBounds(combinedBounds);
        }
    }

    /**
     * Get layer by ID
     */
    getLayer(id) {
        return this.layers.get(id);
    }

    /**
     * Get all layers
     */
    getAllLayers() {
        return this.layers;
    }
}

// Export for use in other modules
window.LayerHandler = LayerHandler;
