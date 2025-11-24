/**
 * Interaction Manager
 * Handle feature clicks, selections, and JSON display
 */

class InteractionManager {
    constructor(map, config, layerHandler) {
        this.map = map;
        this.config = config;
        this.layerHandler = layerHandler;
        this.selectedFeatures = new Map();
        this.jsonDisplay = null;
    }

    /**
     * Initialize interaction handlers
     */
    initialize() {
        const clickConfig = this.config.features.clickToSelect;

        if (clickConfig.enabled) {
            this.setupClickHandlers(clickConfig);
        }

        if (this.config.features.jsonDisplay.enabled) {
            this.setupJSONDisplay();
        }
    }

    /**
     * Setup click handlers for interactive layers
     */
    setupClickHandlers(clickConfig) {
        const interactiveLayers = clickConfig.layers || [];

        this.layerHandler.getAllLayers().forEach((layerInfo, layerId) => {
            // Check if this layer should be interactive
            if (interactiveLayers.length === 0 || interactiveLayers.includes(layerId)) {
                this.makeLayerInteractive(layerInfo, clickConfig);
            }
        });
    }

    /**
     * Make a layer interactive
     */
    makeLayerInteractive(layerInfo, clickConfig) {
        const layer = layerInfo.layer;

        layer.eachLayer((featureLayer) => {
            featureLayer.on('click', (e) => {
                this.handleFeatureClick(e, featureLayer, clickConfig);
            });

            // Add hover cursor
            featureLayer.on('mouseover', () => {
                featureLayer._path.style.cursor = 'pointer';
            });
        });
    }

    /**
     * Handle feature click
     */
    handleFeatureClick(e, featureLayer, clickConfig) {
        L.DomEvent.stopPropagation(e);

        const feature = featureLayer.featureData;
        const featureId = this.getFeatureId(feature);

        // Check if already selected
        if (this.selectedFeatures.has(featureId)) {
            // Deselect
            this.deselectFeature(featureId, featureLayer);
        } else {
            // Select
            if (!clickConfig.multiSelect) {
                // Single select: clear all other selections first
                this.clearAllSelections();
            }

            this.selectFeature(featureId, feature, featureLayer, clickConfig);
        }

        // Update JSON display
        this.updateJSONDisplay();
    }

    /**
     * Select a feature
     */
    selectFeature(featureId, feature, featureLayer, clickConfig) {
        // Store selection
        this.selectedFeatures.set(featureId, {
            feature: feature,
            layer: featureLayer
        });

        // Apply highlight style
        const highlightStyle = clickConfig.highlightStyle || {
            fillColor: clickConfig.highlightColor || '#ff1493',
            fillOpacity: clickConfig.highlightOpacity || 0.8,
            color: clickConfig.highlightBorderColor || '#c90076',
            weight: clickConfig.highlightBorderWeight || 2
        };

        featureLayer.setStyle(highlightStyle);
        featureLayer.bringToFront();
    }

    /**
     * Deselect a feature
     */
    deselectFeature(featureId, featureLayer) {
        this.selectedFeatures.delete(featureId);

        // Restore original style
        const originalStyle = this.layerHandler.getFeatureStyle(
            featureLayer.featureData,
            featureLayer.layerConfig
        );

        featureLayer.setStyle(originalStyle);
    }

    /**
     * Clear all selections
     */
    clearAllSelections() {
        this.selectedFeatures.forEach((selection, featureId) => {
            const featureLayer = selection.layer;
            const originalStyle = this.layerHandler.getFeatureStyle(
                featureLayer.featureData,
                featureLayer.layerConfig
            );

            featureLayer.setStyle(originalStyle);
        });

        this.selectedFeatures.clear();
        this.updateJSONDisplay();
    }

    /**
     * Get unique feature ID
     */
    getFeatureId(feature) {
        // Try to use a unique property, fall back to generating one
        return feature.properties.id ||
               feature.properties.NAME ||
               feature.properties.GEOID ||
               `feature_${Date.now()}_${Math.random()}`;
    }

    /**
     * Setup JSON display
     */
    setupJSONDisplay() {
        const jsonConfig = this.config.features.jsonDisplay;
        const position = jsonConfig.position || 'bottom-right';
        const width = jsonConfig.width || '400px';
        const maxHeight = jsonConfig.maxHeight || '400px';
        const title = jsonConfig.title || 'Selected Features';
        const instructions = jsonConfig.instructions || 'Click features to select';

        // Position styles
        const positionStyles = {
            'bottom-right': 'bottom: 20px; right: 20px;',
            'bottom-left': 'bottom: 20px; left: 20px;',
            'top-right': 'top: 20px; right: 20px;',
            'top-left': 'top: 80px; left: 20px;'
        };

        // Create JSON display element
        this.jsonDisplay = document.createElement('div');
        this.jsonDisplay.id = 'jsonDisplay';
        this.jsonDisplay.style.cssText = `
            position: fixed;
            ${positionStyles[position] || positionStyles['bottom-right']}
            width: ${width};
            max-height: ${maxHeight};
            background-color: white;
            border: 2px solid #000;
            border-radius: 5px;
            z-index: 9999;
            padding: 15px;
            overflow-y: auto;
        `;

        this.jsonDisplay.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-size: 14px;">${title}</h4>
                <button id="clearAllButton" style="background: #000; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px;">Clear All</button>
            </div>
            <div style="font-size: 9px; color: #666; margin-bottom: 8px; font-style: italic;">
                ${instructions}
            </div>
            <pre id="json-output" style="margin: 0; font-size: 10px; white-space: pre-wrap; word-wrap: break-word; background: #f5f5f5; padding: 10px; border-radius: 3px; max-height: 280px; overflow-y: auto;">{}</pre>
        `;

        document.body.appendChild(this.jsonDisplay);

        // Add Clear All button handler
        const clearButton = this.jsonDisplay.querySelector('#clearAllButton');
        clearButton.addEventListener('click', () => this.clearAllSelections());
    }

    /**
     * Update JSON display with selected features
     */
    updateJSONDisplay() {
        if (!this.jsonDisplay) return;

        const outputElement = this.jsonDisplay.querySelector('#json-output');
        const jsonConfig = this.config.features.jsonDisplay;
        const clickConfig = this.config.features.clickToSelect;
        const outputFields = clickConfig.outputFields || jsonConfig.outputFields || ['id', 'name'];
        const format = jsonConfig.format || 'object';

        if (this.selectedFeatures.size === 0) {
            outputElement.textContent = '{}';
            return;
        }

        // Build output based on format
        let output;

        if (format === 'object' && outputFields.length === 2) {
            // Format: { "GEOID": "NAME" }
            output = {};
            this.selectedFeatures.forEach((selection) => {
                const props = selection.feature.properties;
                const key = props[outputFields[0]];
                const value = props[outputFields[1]];
                if (key && value) {
                    output[key] = value;
                }
            });
        } else {
            // Format: array of full properties
            output = {
                count: this.selectedFeatures.size,
                features: []
            };

            this.selectedFeatures.forEach((selection) => {
                output.features.push(selection.feature.properties);
            });
        }

        // Pretty print JSON
        outputElement.textContent = JSON.stringify(output, null, 2);
    }

    /**
     * Get selected features
     */
    getSelectedFeatures() {
        return Array.from(this.selectedFeatures.values()).map(s => s.feature);
    }

    /**
     * Expose clear method for custom buttons
     */
    getClearFunction() {
        return () => this.clearAllSelections();
    }
}

// Export for use in other modules
window.InteractionManager = InteractionManager;
