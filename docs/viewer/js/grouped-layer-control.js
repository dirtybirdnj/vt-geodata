/**
 * Grouped Layer Control
 * Custom layer control with collapsible groups and show/hide all functionality
 * Groups are determined by the 'group' property in each layer config
 */

class GroupedLayerControl {
    constructor(map, layerHandler, config) {
        this.map = map;
        this.layerHandler = layerHandler;
        this.config = config;
        this.container = null;

        // Default group settings (collapsed state, default visibility)
        this.groupDefaults = {
            'Regional Background': { collapsed: true, defaultOn: false },
            'Major Water Bodies': { collapsed: false, defaultOn: true },
            'Town Boundaries': { collapsed: false, defaultOn: true },
            'Regional Hydro': { collapsed: true, defaultOn: false },
            'Regional Highways': { collapsed: true, defaultOn: false },
            'Boundaries': { collapsed: false, defaultOn: true },
            'Other': { collapsed: false, defaultOn: true }
        };
    }

    /**
     * Create and add the control to the map
     */
    addTo(map) {
        this.container = document.createElement('div');
        this.container.className = 'grouped-layer-control';
        this.container.innerHTML = this.buildHTML();

        // Add to map container (outside Leaflet's control system for better styling)
        const mapContainer = document.getElementById('map');
        mapContainer.appendChild(this.container);

        this.attachEventListeners();
        this.applyDefaultVisibility();
        return this;
    }

    /**
     * Build groups from layer configs
     */
    buildGroups() {
        const layers = this.layerHandler.getAllLayers();
        const groups = new Map();

        layers.forEach((layerInfo, layerId) => {
            const groupName = layerInfo.config.group || 'Other';
            if (!groups.has(groupName)) {
                groups.set(groupName, []);
            }
            groups.get(groupName).push(layerId);
        });

        return groups;
    }

    /**
     * Build the HTML for the layer control
     */
    buildHTML() {
        const layers = this.layerHandler.getAllLayers();
        const groups = this.buildGroups();

        let html = `
            <div class="glc-header">
                <span class="glc-title">Layers</span>
                <div class="glc-header-buttons">
                    <button class="glc-btn glc-show-all" title="Show All">+</button>
                    <button class="glc-btn glc-hide-all" title="Hide All">-</button>
                </div>
            </div>
            <div class="glc-body">
        `;

        // Build each group
        for (const [groupName, layerIds] of groups) {
            if (layerIds.length === 0) continue;

            const groupSettings = this.groupDefaults[groupName] || { collapsed: false, defaultOn: true };
            const collapsedClass = groupSettings.collapsed ? 'collapsed' : '';
            const chevron = groupSettings.collapsed ? '&#9654;' : '&#9660;';

            html += `
                <div class="glc-group ${collapsedClass}" data-group="${groupName}">
                    <div class="glc-group-header">
                        <span class="glc-chevron">${chevron}</span>
                        <span class="glc-group-name">${groupName}</span>
                        <span class="glc-group-count">(${layerIds.length})</span>
                        <div class="glc-group-buttons">
                            <button class="glc-btn-sm glc-group-show" title="Show Group">+</button>
                            <button class="glc-btn-sm glc-group-hide" title="Hide Group">-</button>
                        </div>
                    </div>
                    <div class="glc-group-layers">
            `;

            for (const layerId of layerIds) {
                const layerInfo = layers.get(layerId);
                const name = layerInfo.config.name || layerId;
                // Check if layer should be on by default
                const shouldBeOn = groupSettings.defaultOn;
                const checked = shouldBeOn ? 'checked' : '';

                html += `
                    <label class="glc-layer">
                        <input type="checkbox" data-layer="${layerId}" ${checked}>
                        <span class="glc-layer-name">${name}</span>
                    </label>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    /**
     * Apply default visibility based on group settings
     */
    applyDefaultVisibility() {
        const groups = this.buildGroups();

        for (const [groupName, layerIds] of groups) {
            const groupSettings = this.groupDefaults[groupName] || { collapsed: false, defaultOn: true };

            for (const layerId of layerIds) {
                const layerInfo = this.layerHandler.getLayer(layerId);
                if (!layerInfo) continue;

                if (groupSettings.defaultOn) {
                    if (!this.map.hasLayer(layerInfo.layer)) {
                        layerInfo.layer.addTo(this.map);
                    }
                } else {
                    if (this.map.hasLayer(layerInfo.layer)) {
                        this.map.removeLayer(layerInfo.layer);
                    }
                }
            }
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Individual layer toggles
        this.container.querySelectorAll('input[data-layer]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const layerId = e.target.dataset.layer;
                this.toggleLayer(layerId, e.target.checked);
            });
        });

        // Group header click (collapse/expand)
        this.container.querySelectorAll('.glc-group-header').forEach(header => {
            header.addEventListener('click', (e) => {
                // Don't toggle if clicking buttons
                if (e.target.closest('.glc-group-buttons')) return;

                const group = header.closest('.glc-group');
                group.classList.toggle('collapsed');
                const chevron = header.querySelector('.glc-chevron');
                chevron.innerHTML = group.classList.contains('collapsed') ? '&#9654;' : '&#9660;';
            });
        });

        // Group show/hide buttons
        this.container.querySelectorAll('.glc-group-show').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const group = btn.closest('.glc-group');
                this.setGroupVisibility(group, true);
            });
        });

        this.container.querySelectorAll('.glc-group-hide').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const group = btn.closest('.glc-group');
                this.setGroupVisibility(group, false);
            });
        });

        // Show all button
        this.container.querySelector('.glc-show-all').addEventListener('click', () => {
            this.setAllVisibility(true);
        });

        // Hide all button
        this.container.querySelector('.glc-hide-all').addEventListener('click', () => {
            this.setAllVisibility(false);
        });
    }

    /**
     * Toggle a single layer
     */
    toggleLayer(layerId, visible) {
        const layerInfo = this.layerHandler.getLayer(layerId);
        if (!layerInfo) return;

        if (visible) {
            if (!this.map.hasLayer(layerInfo.layer)) {
                layerInfo.layer.addTo(this.map);
            }
        } else {
            if (this.map.hasLayer(layerInfo.layer)) {
                this.map.removeLayer(layerInfo.layer);
            }
        }
    }

    /**
     * Set visibility for all layers in a group
     */
    setGroupVisibility(groupElement, visible) {
        groupElement.querySelectorAll('input[data-layer]').forEach(checkbox => {
            checkbox.checked = visible;
            this.toggleLayer(checkbox.dataset.layer, visible);
        });
    }

    /**
     * Set visibility for all layers
     */
    setAllVisibility(visible) {
        this.container.querySelectorAll('input[data-layer]').forEach(checkbox => {
            checkbox.checked = visible;
            this.toggleLayer(checkbox.dataset.layer, visible);
        });
    }
}

// Export
window.GroupedLayerControl = GroupedLayerControl;
