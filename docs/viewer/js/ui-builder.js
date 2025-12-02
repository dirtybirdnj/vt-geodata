/**
 * UI Builder
 * Build info box, buttons, and other UI elements
 */

class UIBuilder {
    constructor(config, interactionManager) {
        this.config = config;
        this.interactionManager = interactionManager;
        this.versionInfo = null;

        // Store global reference for hover updates from other modules
        window.uiBuilderInstance = this;
    }

    /**
     * Load version info - try GitHub API first for live commit, fallback to version.json
     */
    async loadVersionInfo() {
        // Try GitHub API for latest commit (works on GitHub Pages)
        try {
            const response = await fetch('https://api.github.com/repos/dirtybirdnj/vt-geodata/commits/main', {
                headers: { 'Accept': 'application/vnd.github.v3+json' }
            });
            if (response.ok) {
                const data = await response.json();
                this.versionInfo = {
                    commitId: data.sha.substring(0, 7),
                    timestamp: data.commit.committer.date.substring(0, 10)
                };
                return;
            }
        } catch (e) {
            console.log('GitHub API not available, using version.json');
        }

        // Fallback to version.json
        try {
            const response = await fetch('version.json');
            if (response.ok) {
                this.versionInfo = await response.json();
            }
        } catch (e) {
            console.log('Version info not available');
        }
    }

    /**
     * Build all UI elements
     * @param {Object} options - Options for UI building
     * @param {boolean} options.hideInfoBox - Hide the info box (for screenshots)
     * @param {boolean} options.hideJsonDisplay - Hide the JSON display panel
     */
    async buildUI(options = {}) {
        this.options = options;

        // Load version info before building UI
        await this.loadVersionInfo();

        if (!options.hideInfoBox) {
            this.buildInfoBox();
        }
        this.buildCustomButtons();
    }

    /**
     * Build info box with title, description, and legend
     */
    buildInfoBox() {
        const uiConfig = this.config.ui;
        const infoBoxConfig = uiConfig.infoBox;

        if (!infoBoxConfig) return;

        const colorScheme = uiConfig.colorScheme;
        const width = infoBoxConfig.width || '450px';

        // Create info box container
        const infoBox = document.createElement('div');
        infoBox.className = 'info-box';
        infoBox.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            width: ${width};
            background-color: white;
            border: 2px solid ${colorScheme};
            border-radius: 8px;
            z-index: 9999;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;

        // Build header row with back link and commit ID
        const headerRow = document.createElement('div');
        headerRow.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        `;

        // Build back link
        const backLink = document.createElement('a');
        backLink.href = '../index.html';
        backLink.style.cssText = `
            text-decoration: none;
            color: ${colorScheme};
            font-weight: 600;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        `;
        backLink.innerHTML = `<span>←</span><span>Back to Index</span>`;

        // Build commit ID badge
        const commitBadge = document.createElement('span');
        commitBadge.id = 'commit-badge';
        commitBadge.style.cssText = `
            font-family: monospace;
            font-size: 10px;
            color: #666;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        `;
        commitBadge.textContent = this.versionInfo?.commitId || 'dev';

        headerRow.appendChild(backLink);
        headerRow.appendChild(commitBadge);

        // Build title
        const title = document.createElement('h4');
        title.style.cssText = `margin: 0 0 10px 0; color: ${colorScheme};`;
        title.textContent = this.config.title || 'Map Viewer';

        // Build description/subtitle
        const description = document.createElement('p');
        description.style.cssText = 'margin: 5px 0; font-size: 12px; color: #666;';

        let descContent = infoBoxConfig.content?.subtitle || this.config.description || '';

        // Add highlights if present
        if (infoBoxConfig.content?.highlights) {
            descContent += '<br>' + infoBoxConfig.content.highlights.join('<br>');
        }

        description.innerHTML = descContent;

        // Assemble info box
        infoBox.appendChild(headerRow);
        infoBox.appendChild(title);
        infoBox.appendChild(description);

        // Add legend if present
        if (infoBoxConfig.content?.legend) {
            const legend = this.buildLegend(infoBoxConfig.content.legend);
            infoBox.appendChild(legend);
        }

        // Add metadata display if present
        if (infoBoxConfig.content?.metadata) {
            const metadata = this.buildMetadata(infoBoxConfig.content.metadata);
            infoBox.appendChild(metadata);
        }

        // Add footer if present
        if (infoBoxConfig.content?.footer) {
            const footer = document.createElement('p');
            footer.style.cssText = 'margin: 10px 0 0 0; font-size: 10px; color: #999; font-style: italic;';
            footer.textContent = infoBoxConfig.content.footer;
            infoBox.appendChild(footer);
        }

        // Add hover info panel (fixed size)
        this.buildHoverPanel(infoBox, colorScheme);

        document.body.appendChild(infoBox);
    }

    /**
     * Build fixed-size hover info panel
     */
    buildHoverPanel(container, colorScheme) {
        const hoverPanel = document.createElement('div');
        hoverPanel.id = 'hover-info-panel';
        hoverPanel.style.cssText = `
            margin-top: 12px;
            padding: 10px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            min-height: 60px;
            height: 60px;
            overflow: hidden;
        `;

        const header = document.createElement('div');
        header.style.cssText = `
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        `;
        header.textContent = 'Feature Info';

        const content = document.createElement('div');
        content.id = 'hover-info-content';
        content.style.cssText = `
            font-size: 12px;
            color: #333;
            line-height: 1.4;
        `;
        content.innerHTML = '<span style="color: #999; font-style: italic;">Hover over a feature</span>';

        hoverPanel.appendChild(header);
        hoverPanel.appendChild(content);
        container.appendChild(hoverPanel);

        // Store reference for updates
        this.hoverContent = content;
    }

    /**
     * Update hover panel with feature info
     */
    updateHoverPanel(feature, layerConfig) {
        const content = document.getElementById('hover-info-content');
        if (!content) return;

        if (!feature) {
            content.innerHTML = '<span style="color: #999; font-style: italic;">Hover over a feature</span>';
            return;
        }

        // Build content from tooltip config
        const tooltipConfig = layerConfig?.tooltip;
        let html = '';

        if (tooltipConfig) {
            const fields = tooltipConfig.fields || [];
            const aliases = tooltipConfig.aliases || fields;

            fields.forEach((field, index) => {
                const value = feature.properties[field];
                const alias = aliases[index] || field;

                if (value !== undefined && value !== null) {
                    html += `<div><strong>${alias}</strong> ${value}</div>`;
                }
            });
        } else {
            // Fallback: show NAME if available
            const name = feature.properties.NAME || feature.properties.name || '';
            if (name) {
                html = `<strong>${name}</strong>`;
            }
        }

        // Add layer source info
        if (layerConfig) {
            const layerId = layerConfig.id;
            const layerName = layerConfig.name || layerId;
            const sourceFile = layerConfig.source || '';

            html += `<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; font-size: 10px; color: #666;">`;
            html += `<div><strong>Layer:</strong> ${layerName}</div>`;
            html += `<div><strong>Source:</strong> <code style="font-size: 9px; background: #f0f0f0; padding: 1px 3px; border-radius: 2px;">${sourceFile}</code></div>`;

            // Build shareable link
            const featureId = feature.properties.id || feature.properties.GEOID || feature.properties.NAME || feature.properties.name;
            if (featureId) {
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('layer', layerId);
                currentUrl.searchParams.set('feature', featureId);
                const shareUrl = currentUrl.toString();

                html += `<div style="margin-top: 6px;">`;
                html += `<a href="${shareUrl}" target="_blank" style="color: #1976d2; text-decoration: none; font-size: 10px;" title="Open in new tab">`;
                html += `🔗 Share this feature</a>`;
                html += `</div>`;
            }

            html += `</div>`;
        }

        content.innerHTML = html || '<span style="color: #999;">No data</span>';
    }

    /**
     * Build legend
     */
    buildLegend(legendItems) {
        const container = document.createElement('div');
        container.style.cssText = 'margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;';

        const header = document.createElement('div');
        header.style.cssText = 'font-size: 11px; font-weight: bold; margin-bottom: 5px;';
        header.textContent = 'Data Layers:';
        container.appendChild(header);

        legendItems.forEach(item => {
            const row = document.createElement('div');
            row.style.cssText = 'display: flex; align-items: center; margin: 3px 0;';

            const swatch = document.createElement('div');
            swatch.style.cssText = `
                width: 15px;
                height: 15px;
                background: ${item.color};
                border: ${item.border || '1px solid ' + item.color};
                margin-right: 8px;
            `;

            const label = document.createElement('span');
            label.style.cssText = 'font-size: 11px;';
            label.textContent = item.label;

            row.appendChild(swatch);
            row.appendChild(label);
            container.appendChild(row);
        });

        return container;
    }

    /**
     * Build metadata display
     */
    buildMetadata(metadata) {
        const container = document.createElement('div');
        container.style.cssText = `
            margin-top: 10px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 11px;
        `;

        let html = '';
        for (const [key, value] of Object.entries(metadata)) {
            html += `<b>${key}:</b> ${value}<br>`;
        }

        container.innerHTML = html;
        return container;
    }

    /**
     * Build custom buttons
     */
    buildCustomButtons() {
        const buttons = this.config.features.customButtons || [];

        buttons.forEach(buttonConfig => {
            this.buildButton(buttonConfig);
        });
    }

    /**
     * Build a single button
     */
    buildButton(buttonConfig) {
        const button = document.createElement('button');
        button.textContent = buttonConfig.label;
        button.className = 'custom-button';

        // Position button
        const position = buttonConfig.position || 'bottom-right';
        this.positionElement(button, position);

        // Style button
        button.style.cssText += `
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            border: 2px solid #5c6bc0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 9998;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
        `;

        // Add click handler
        button.addEventListener('click', () => {
            this.handleButtonAction(buttonConfig.action);
        });

        document.body.appendChild(button);
    }

    /**
     * Position an element based on position string
     */
    positionElement(element, position) {
        const positions = {
            'top-left': 'position: fixed; top: 10px; left: 10px;',
            'top-right': 'position: fixed; top: 10px; right: 10px;',
            'bottom-left': 'position: fixed; bottom: 10px; left: 10px;',
            'bottom-right': 'position: fixed; bottom: 20px; right: 20px;',
            'json-display': 'margin-top: 10px;' // Inside JSON display
        };

        element.style.cssText = positions[position] || positions['bottom-right'];
    }

    /**
     * Handle button actions
     */
    handleButtonAction(action) {
        switch (action) {
            case 'clearSelection':
                if (this.interactionManager) {
                    this.interactionManager.clearAllSelections();
                }
                break;

            case 'exportJSON':
                this.exportJSON();
                break;

            default:
                console.warn('Unknown button action:', action);
        }
    }

    /**
     * Export selected features as JSON
     */
    exportJSON() {
        if (!this.interactionManager) return;

        const features = this.interactionManager.getSelectedFeatures();
        const json = JSON.stringify(features, null, 2);

        // Create download
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.config.id}_selection.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Export for use in other modules
window.UIBuilder = UIBuilder;
