/**
 * Map Core
 * Initialize and manage the Leaflet map
 */

class MapCore {
    constructor(containerId = 'map') {
        this.containerId = containerId;
        this.map = null;
        this.baseTiles = null;
    }

    /**
     * Initialize the map with configuration
     */
    initialize(config) {
        const mapConfig = config.map;

        // Create map instance
        this.map = L.map(this.containerId, {
            center: mapConfig.center,
            zoom: mapConfig.zoom,
            zoomControl: true,
            preferCanvas: false,
            attributionControl: mapConfig.attributionControl
        });

        // Add base tiles if not vector-only
        if (mapConfig.tiles && mapConfig.tiles !== 'none' && mapConfig.tiles !== null) {
            this.addBaseTiles(mapConfig.tiles);
        } else {
            // Vector-only mode: white background
            this.setVectorOnlyMode();
        }

        return this.map;
    }

    /**
     * Add base tile layer
     */
    addBaseTiles(tileSource) {
        const tileLayers = {
            'OpenStreetMap': {
                url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                options: {
                    maxZoom: 19,
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }
            },
            'CartoDB': {
                url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                options: {
                    maxZoom: 19,
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                }
            }
        };

        const tileConfig = tileLayers[tileSource] || tileLayers['OpenStreetMap'];
        this.baseTiles = L.tileLayer(tileConfig.url, tileConfig.options);
        this.baseTiles.addTo(this.map);
    }

    /**
     * Set vector-only mode (no tiles, white background)
     */
    setVectorOnlyMode() {
        // Add white background style
        const style = document.createElement('style');
        style.textContent = `
            body { background-color: white; }
            .leaflet-container { background: white !important; }
        `;
        document.head.appendChild(style);
    }

    /**
     * Get the map instance
     */
    getMap() {
        return this.map;
    }

    /**
     * Fit map bounds to layers
     */
    fitBounds(bounds) {
        if (this.map && bounds) {
            this.map.fitBounds(bounds);
        }
    }
}

// Export for use in other modules
window.MapCore = MapCore;
