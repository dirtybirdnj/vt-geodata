/**
 * Grouped Layer Control
 * Custom layer control with collapsible groups and show/hide all functionality
 */

class GroupedLayerControl {
    constructor(map, layerHandler, config) {
        this.map = map;
        this.layerHandler = layerHandler;
        this.config = config;
        this.container = null;
        this.groups = new Map();

        // Define layer groups
        this.layerGroups = {
            'Regions': {
                collapsed: false,
                layers: ['quebec_mrc', 'ny_counties', 'nh_counties', 'ma_counties', 'me_counties']
            },
            'Towns & Municipalities': {
                collapsed: true,
                layers: ['quebec_municipalities', 'ny_towns', 'nh_towns', 'ma_towns', 'me_towns', 'vt_towns',
                         'chittenden_towns_hydro', 'washington_towns_hydro']
            },
            'Major Water Bodies': {
                collapsed: false,
                layers: ['lake_champlain', 'lake_memphremagog', 'richelieu_corridor', 'missisquoi_quebec']
            },
            'Lakes & Rivers': {
                collapsed: true,
                layers: ['quebec_lakes', 'quebec_rivers', 'ny_lakes', 'ny_rivers', 'nh_lakes', 'nh_rivers',
                         'chittenden_rivers', 'chittenden_lakes', 'washington_rivers', 'washington_lakes',
                         'vt_rivers', 'vt_lakes']
            },
            'Highways & Roads': {
                collapsed: false,
                layers: ['vt_state_routes', 'vt_us_highways', 'vt_interstates', 'quebec_highways',
                         'regional_state_routes', 'regional_us_highways', 'regional_interstates',
                         'ny_interstates', 'ny_us_highways', 'ny_state_routes',
                         'nh_interstates', 'nh_us_highways', 'nh_state_routes']
            }
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
        return this;
    }

    /**
     * Build the HTML for the layer control
     */
    buildHTML() {
        const layers = this.layerHandler.getAllLayers();

        let html = `
            <div class="glc-header">
                <span class="glc-title">Layers</span>
                <div class="glc-header-buttons">
                    <button class="glc-btn glc-show-all" title="Show All">👁</button>
                    <button class="glc-btn glc-hide-all" title="Hide All">👁‍🗨</button>
                    <button class="glc-btn glc-toggle-panel" title="Collapse">−</button>
                </div>
            </div>
            <div class="glc-body">
        `;

        // Track which layers have been added to groups
        const groupedLayers = new Set();

        // Build groups
        for (const [groupName, groupConfig] of Object.entries(this.layerGroups)) {
            const groupLayers = groupConfig.layers.filter(id => layers.has(id));

            if (groupLayers.length === 0) continue;

            groupLayers.forEach(id => groupedLayers.add(id));

            const collapsedClass = groupConfig.collapsed ? 'collapsed' : '';
            const chevron = groupConfig.collapsed ? '▶' : '▼';

            html += `
                <div class="glc-group ${collapsedClass}" data-group="${groupName}">
                    <div class="glc-group-header">
                        <span class="glc-chevron">${chevron}</span>
                        <span class="glc-group-name">${groupName}</span>
                        <span class="glc-group-count">(${groupLayers.length})</span>
                        <div class="glc-group-buttons">
                            <button class="glc-btn-sm glc-group-show" title="Show Group">+</button>
                            <button class="glc-btn-sm glc-group-hide" title="Hide Group">−</button>
                        </div>
                    </div>
                    <div class="glc-group-layers">
            `;

            for (const layerId of groupLayers) {
                const layerInfo = layers.get(layerId);
                const name = layerInfo.config.name || layerId;
                const checked = this.map.hasLayer(layerInfo.layer) ? 'checked' : '';

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

        // Add ungrouped layers to "Other" group
        const ungroupedLayers = [];
        layers.forEach((layerInfo, id) => {
            if (!groupedLayers.has(id)) {
                ungroupedLayers.push(id);
            }
        });

        if (ungroupedLayers.length > 0) {
            html += `
                <div class="glc-group" data-group="Other">
                    <div class="glc-group-header">
                        <span class="glc-chevron">▼</span>
                        <span class="glc-group-name">Other</span>
                        <span class="glc-group-count">(${ungroupedLayers.length})</span>
                        <div class="glc-group-buttons">
                            <button class="glc-btn-sm glc-group-show" title="Show Group">+</button>
                            <button class="glc-btn-sm glc-group-hide" title="Hide Group">−</button>
                        </div>
                    </div>
                    <div class="glc-group-layers">
            `;

            for (const layerId of ungroupedLayers) {
                const layerInfo = layers.get(layerId);
                const name = layerInfo.config.name || layerId;
                const checked = this.map.hasLayer(layerInfo.layer) ? 'checked' : '';

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
                chevron.textContent = group.classList.contains('collapsed') ? '▶' : '▼';
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

        // Toggle panel button
        this.container.querySelector('.glc-toggle-panel').addEventListener('click', (e) => {
            const body = this.container.querySelector('.glc-body');
            body.classList.toggle('hidden');
            e.target.textContent = body.classList.contains('hidden') ? '+' : '−';
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
