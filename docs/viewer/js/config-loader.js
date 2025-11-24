/**
 * Configuration Loader
 * Loads and validates map configuration from JSON files
 */

class ConfigLoader {
    constructor(configBaseUrl = '../configs/') {
        this.configBaseUrl = configBaseUrl;
        this.config = null;
    }

    /**
     * Get configuration name from URL parameter
     */
    getConfigFromURL() {
        const params = new URLSearchParams(window.location.search);
        return params.get('config');
    }

    /**
     * Load configuration from JSON file
     */
    async loadConfig(configName) {
        if (!configName) {
            throw new Error('No configuration specified. Add ?config=map_name to URL');
        }

        const configUrl = `${this.configBaseUrl}${configName}.json`;

        try {
            const response = await fetch(configUrl);
            if (!response.ok) {
                throw new Error(`Configuration not found: ${configName} (${response.status})`);
            }

            const config = await response.json();
            this.config = this.validateAndEnhance(config);
            return this.config;
        } catch (error) {
            console.error('Error loading configuration:', error);
            throw error;
        }
    }

    /**
     * Validate configuration and add defaults
     */
    validateAndEnhance(config) {
        // Ensure required fields exist
        if (!config.id) {
            throw new Error('Configuration missing required field: id');
        }

        // Apply defaults
        const enhanced = {
            // Map defaults
            map: {
                center: config.map?.center || [44.0, -72.7],
                zoom: config.map?.zoom || 8,
                tiles: config.map?.tiles || 'OpenStreetMap',
                attributionControl: config.map?.attributionControl !== false,
                ...config.map
            },

            // UI defaults
            ui: {
                colorScheme: config.ui?.colorScheme || this.resolveColorScheme(config.ui?.colorScheme || '#5c6bc0'),
                infoBox: {
                    width: config.ui?.infoBox?.width || '450px',
                    ...config.ui?.infoBox
                },
                ...config.ui
            },

            // Feature defaults
            features: {
                clickToSelect: config.features?.clickToSelect || { enabled: false },
                jsonDisplay: config.features?.jsonDisplay || { enabled: false },
                customButtons: config.features?.customButtons || [],
                layerControl: {
                    enabled: config.features?.layerControl?.enabled !== false,
                    position: config.features?.layerControl?.position || 'topright',
                    collapsed: config.features?.layerControl?.collapsed || false,
                    ...config.features?.layerControl
                },
                ...config.features
            },

            // Pass through other fields
            id: config.id,
            version: config.version || '1.0',
            title: config.title || 'Map Viewer',
            description: config.description || '',
            layers: config.layers || [],
            colorMaps: config.colorMaps || {},
            metadata: config.metadata || {}
        };

        return enhanced;
    }

    /**
     * Resolve color scheme name to hex color
     */
    resolveColorScheme(colorScheme) {
        const schemes = {
            'vectorBlack': '#000',
            'waterBlue': '#1976d2',
            'townGreen': '#2c5f2d',
            'mashupIndigo': '#5c6bc0',
            'emphasizeRed': '#ff6b6b'
        };

        // If it's a named scheme, resolve it; otherwise assume it's a hex color
        return schemes[colorScheme] || colorScheme;
    }

    /**
     * Get the loaded configuration
     */
    getConfig() {
        return this.config;
    }
}

// Export for use in other modules
window.ConfigLoader = ConfigLoader;
