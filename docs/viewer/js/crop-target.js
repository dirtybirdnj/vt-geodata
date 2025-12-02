/**
 * Crop Target
 * Draggable and resizable crop overlay for print maps
 * Shows geographic bounds that can be used for SVG generation
 */

class CropTarget {
    constructor(map, config) {
        this.map = map;
        this.config = config;
        this.printConfig = config.print || {};
        this.rectangle = null;
        this.panel = null;
        this.enabled = false;

        // Calculate aspect ratio from print config
        this.aspectRatio = this.calculateAspectRatio();

        // Latitude correction factor (at ~44°N)
        // 1° longitude = 1° latitude * cos(44°) in visual space
        this.latCorrection = Math.cos(44 * Math.PI / 180); // ~0.719
    }

    /**
     * Calculate aspect ratio from print config
     */
    calculateAspectRatio() {
        if (this.printConfig.aspectRatio) {
            const parts = this.printConfig.aspectRatio.split(':');
            return parseFloat(parts[1]) / parseFloat(parts[0]); // height/width
        }
        if (this.printConfig.width_in && this.printConfig.height_in) {
            return this.printConfig.height_in / this.printConfig.width_in;
        }
        // Default to 12x18 (2:3 ratio)
        return 1.5;
    }

    /**
     * Initialize crop target
     */
    initialize() {
        this.createPanel();
        this.createToggleButton();
    }

    /**
     * Create control panel
     */
    createPanel() {
        const panel = document.createElement('div');
        panel.id = 'crop-panel';
        panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            background: white;
            border: 2px solid #1565c0;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: none;
        `;

        panel.innerHTML = `
            <div style="font-weight: 600; color: #1565c0; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <span>Crop Target</span>
                <span style="font-size: 11px; color: #666;">Drag corners to resize</span>
            </div>
            <div style="font-size: 12px; margin-bottom: 8px;">
                <strong>Print Size:</strong> ${this.printConfig.size || '12x18'}"
                <span style="color: #666;">(${this.printConfig.aspectRatio || '2:3'})</span>
            </div>
            <div id="crop-bounds" style="font-family: monospace; font-size: 11px; background: #f5f5f5; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                <div><strong>West:</strong> <span id="crop-west">-</span></div>
                <div><strong>South:</strong> <span id="crop-south">-</span></div>
                <div><strong>East:</strong> <span id="crop-east">-</span></div>
                <div><strong>North:</strong> <span id="crop-north">-</span></div>
            </div>
            <div style="font-size: 11px; color: #666; margin-bottom: 10px;">
                <div><strong>Lon span:</strong> <span id="crop-lon-span">-</span>°</div>
                <div><strong>Lat span:</strong> <span id="crop-lat-span">-</span>°</div>
            </div>
            <div style="display: flex; gap: 8px;">
                <button id="crop-copy-btn" style="flex: 1; padding: 8px; background: #1565c0; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    Copy Bounds
                </button>
                <button id="crop-reset-btn" style="flex: 1; padding: 8px; background: #757575; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    Reset
                </button>
            </div>
            <div id="crop-copy-msg" style="font-size: 11px; color: #4caf50; text-align: center; margin-top: 8px; display: none;">
                Copied to clipboard!
            </div>
        `;

        document.body.appendChild(panel);
        this.panel = panel;

        // Wire up buttons
        document.getElementById('crop-copy-btn').addEventListener('click', () => this.copyBounds());
        document.getElementById('crop-reset-btn').addEventListener('click', () => this.resetBounds());
    }

    /**
     * Create toggle button
     */
    createToggleButton() {
        const button = document.createElement('button');
        button.id = 'crop-toggle-btn';
        button.innerHTML = '&#x2702; Crop';
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            padding: 10px 15px;
            background: white;
            border: 2px solid #1565c0;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            color: #1565c0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 9999;
        `;

        button.addEventListener('click', () => this.toggle());
        document.body.appendChild(button);
    }

    /**
     * Toggle crop target on/off
     */
    toggle() {
        if (this.enabled) {
            this.disable();
        } else {
            this.enable();
        }
    }

    /**
     * Enable crop target
     */
    enable() {
        this.enabled = true;
        this.panel.style.display = 'block';
        document.getElementById('crop-toggle-btn').style.background = '#1565c0';
        document.getElementById('crop-toggle-btn').style.color = 'white';

        // Create rectangle if not exists
        if (!this.rectangle) {
            this.createRectangle();
        }

        this.updatePanel();
    }

    /**
     * Disable crop target
     */
    disable() {
        this.enabled = false;
        this.panel.style.display = 'none';
        document.getElementById('crop-toggle-btn').style.background = 'white';
        document.getElementById('crop-toggle-btn').style.color = '#1565c0';

        // Remove rectangle
        if (this.rectangle) {
            this.map.removeLayer(this.rectangle);
            this.rectangle = null;
        }

        // Remove corner markers
        if (this.cornerMarkers) {
            this.cornerMarkers.forEach(m => this.map.removeLayer(m));
            this.cornerMarkers = null;
        }
    }

    /**
     * Create draggable rectangle
     */
    createRectangle() {
        // Calculate initial bounds based on current view and aspect ratio
        const center = this.map.getCenter();
        const bounds = this.map.getBounds();

        // Use 60% of current view as initial size
        const viewLatSpan = bounds.getNorth() - bounds.getSouth();
        const latSpan = viewLatSpan * 0.6;

        // Calculate lon span for correct aspect ratio
        // aspect = latSpan / (lonSpan * latCorrection)
        // lonSpan = latSpan / (aspect * latCorrection)
        const lonSpan = latSpan / (this.aspectRatio * this.latCorrection);

        const south = center.lat - latSpan / 2;
        const north = center.lat + latSpan / 2;
        const west = center.lng - lonSpan / 2;
        const east = center.lng + lonSpan / 2;

        const rectBounds = L.latLngBounds(
            L.latLng(south, west),
            L.latLng(north, east)
        );

        // Create rectangle
        this.rectangle = L.rectangle(rectBounds, {
            color: '#ff1493',
            weight: 3,
            fill: true,
            fillColor: '#ff1493',
            fillOpacity: 0.1,
            dashArray: '10, 5',
            interactive: true
        }).addTo(this.map);

        // Make rectangle draggable
        this.makeDraggable();

        // Create corner resize handles
        this.createCornerMarkers(rectBounds);
    }

    /**
     * Make rectangle draggable
     */
    makeDraggable() {
        let isDragging = false;
        let startLatLng = null;
        let startBounds = null;

        this.rectangle.on('mousedown', (e) => {
            // Only drag from center, not corners
            if (e.originalEvent.target.classList.contains('corner-marker')) return;

            isDragging = true;
            startLatLng = e.latlng;
            startBounds = this.rectangle.getBounds();
            this.map.dragging.disable();
            L.DomEvent.stopPropagation(e);
        });

        this.map.on('mousemove', (e) => {
            if (!isDragging) return;

            const latDiff = e.latlng.lat - startLatLng.lat;
            const lngDiff = e.latlng.lng - startLatLng.lng;

            const newBounds = L.latLngBounds(
                L.latLng(startBounds.getSouth() + latDiff, startBounds.getWest() + lngDiff),
                L.latLng(startBounds.getNorth() + latDiff, startBounds.getEast() + lngDiff)
            );

            this.rectangle.setBounds(newBounds);
            this.updateCornerMarkers(newBounds);
            this.updatePanel();
        });

        this.map.on('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                this.map.dragging.enable();
            }
        });
    }

    /**
     * Create corner resize markers
     */
    createCornerMarkers(bounds) {
        this.cornerMarkers = [];

        const corners = [
            { pos: 'sw', lat: bounds.getSouth(), lng: bounds.getWest() },
            { pos: 'nw', lat: bounds.getNorth(), lng: bounds.getWest() },
            { pos: 'ne', lat: bounds.getNorth(), lng: bounds.getEast() },
            { pos: 'se', lat: bounds.getSouth(), lng: bounds.getEast() }
        ];

        corners.forEach(corner => {
            const marker = L.marker([corner.lat, corner.lng], {
                icon: L.divIcon({
                    className: 'corner-marker',
                    html: `<div style="
                        width: 14px;
                        height: 14px;
                        background: #ff1493;
                        border: 2px solid white;
                        border-radius: 50%;
                        cursor: ${corner.pos === 'nw' || corner.pos === 'se' ? 'nwse-resize' : 'nesw-resize'};
                        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
                    "></div>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                }),
                draggable: true
            }).addTo(this.map);

            marker.cornerPos = corner.pos;
            marker.on('drag', (e) => this.onCornerDrag(e, corner.pos));

            this.cornerMarkers.push(marker);
        });
    }

    /**
     * Handle corner drag (resize maintaining aspect ratio)
     */
    onCornerDrag(e, cornerPos) {
        const newLatLng = e.target.getLatLng();
        const bounds = this.rectangle.getBounds();

        let south = bounds.getSouth();
        let north = bounds.getNorth();
        let west = bounds.getWest();
        let east = bounds.getEast();

        // Calculate new position based on which corner is being dragged
        // Maintain aspect ratio by calculating the other dimension

        if (cornerPos === 'sw') {
            south = newLatLng.lat;
            west = newLatLng.lng;
            // Adjust north/east to maintain aspect ratio from SW corner
            const latSpan = north - south;
            const lonSpan = latSpan / (this.aspectRatio * this.latCorrection);
            east = west + lonSpan;
        } else if (cornerPos === 'nw') {
            north = newLatLng.lat;
            west = newLatLng.lng;
            // Adjust south/east to maintain aspect ratio
            const latSpan = north - south;
            const lonSpan = latSpan / (this.aspectRatio * this.latCorrection);
            east = west + lonSpan;
        } else if (cornerPos === 'ne') {
            north = newLatLng.lat;
            east = newLatLng.lng;
            // Adjust south/west to maintain aspect ratio
            const latSpan = north - south;
            const lonSpan = latSpan / (this.aspectRatio * this.latCorrection);
            west = east - lonSpan;
        } else if (cornerPos === 'se') {
            south = newLatLng.lat;
            east = newLatLng.lng;
            // Adjust north/west to maintain aspect ratio
            const latSpan = north - south;
            const lonSpan = latSpan / (this.aspectRatio * this.latCorrection);
            west = east - lonSpan;
        }

        const newBounds = L.latLngBounds(
            L.latLng(south, west),
            L.latLng(north, east)
        );

        this.rectangle.setBounds(newBounds);
        this.updateCornerMarkers(newBounds);
        this.updatePanel();
    }

    /**
     * Update corner marker positions
     */
    updateCornerMarkers(bounds) {
        if (!this.cornerMarkers) return;

        const positions = {
            'sw': [bounds.getSouth(), bounds.getWest()],
            'nw': [bounds.getNorth(), bounds.getWest()],
            'ne': [bounds.getNorth(), bounds.getEast()],
            'se': [bounds.getSouth(), bounds.getEast()]
        };

        this.cornerMarkers.forEach(marker => {
            const pos = positions[marker.cornerPos];
            marker.setLatLng(pos);
        });
    }

    /**
     * Update panel with current bounds
     */
    updatePanel() {
        if (!this.rectangle) return;

        const bounds = this.rectangle.getBounds();

        document.getElementById('crop-west').textContent = bounds.getWest().toFixed(4);
        document.getElementById('crop-south').textContent = bounds.getSouth().toFixed(4);
        document.getElementById('crop-east').textContent = bounds.getEast().toFixed(4);
        document.getElementById('crop-north').textContent = bounds.getNorth().toFixed(4);

        const lonSpan = bounds.getEast() - bounds.getWest();
        const latSpan = bounds.getNorth() - bounds.getSouth();

        document.getElementById('crop-lon-span').textContent = lonSpan.toFixed(4);
        document.getElementById('crop-lat-span').textContent = latSpan.toFixed(4);
    }

    /**
     * Copy bounds to clipboard
     */
    copyBounds() {
        if (!this.rectangle) return;

        const bounds = this.rectangle.getBounds();
        const boundsArray = [
            bounds.getWest().toFixed(4),
            bounds.getSouth().toFixed(4),
            bounds.getEast().toFixed(4),
            bounds.getNorth().toFixed(4)
        ];

        const text = `'bounds': [${boundsArray.join(', ')}],`;

        navigator.clipboard.writeText(text).then(() => {
            const msg = document.getElementById('crop-copy-msg');
            msg.style.display = 'block';
            setTimeout(() => msg.style.display = 'none', 2000);
        });
    }

    /**
     * Reset bounds to initial position
     */
    resetBounds() {
        if (this.rectangle) {
            this.map.removeLayer(this.rectangle);
            this.rectangle = null;
        }
        if (this.cornerMarkers) {
            this.cornerMarkers.forEach(m => this.map.removeLayer(m));
            this.cornerMarkers = null;
        }

        this.createRectangle();
        this.updatePanel();
    }

    /**
     * Get current bounds
     */
    getBounds() {
        if (!this.rectangle) return null;

        const bounds = this.rectangle.getBounds();
        return [
            bounds.getWest(),
            bounds.getSouth(),
            bounds.getEast(),
            bounds.getNorth()
        ];
    }
}

// Export for use in other modules
window.CropTarget = CropTarget;
