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
            weight: 4,
            color: '#000',
            fillOpacity: 0.9
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
        const position = jsonConfig.position || 'bottom-left';

        // Create JSON display element
        this.jsonDisplay = document.createElement('div');
        this.jsonDisplay.className = `json-display json-display-${position}`;
        this.jsonDisplay.innerHTML = `
            <h4>Selected Features</h4>
            <pre id="json-output">{}</pre>
        `;

        document.body.appendChild(this.jsonDisplay);
    }

    /**
     * Update JSON display with selected features
     */
    updateJSONDisplay() {
        if (!this.jsonDisplay) return;

        const outputElement = this.jsonDisplay.querySelector('#json-output');

        if (this.selectedFeatures.size === 0) {
            outputElement.textContent = '{}';
            return;
        }

        // Build output object
        const output = {
            count: this.selectedFeatures.size,
            features: []
        };

        this.selectedFeatures.forEach((selection) => {
            output.features.push(selection.feature.properties);
        });

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
