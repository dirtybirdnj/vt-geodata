/**
 * UI Builder
 * Build info box, buttons, and other UI elements
 */

class UIBuilder {
    constructor(config, interactionManager) {
        this.config = config;
        this.interactionManager = interactionManager;
    }

    /**
     * Build all UI elements
     */
    buildUI() {
        this.buildInfoBox();
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
            margin-bottom: 10px;
        `;
        backLink.innerHTML = `<span>←</span><span>Back to Index</span>`;

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
        infoBox.appendChild(backLink);
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

        document.body.appendChild(infoBox);
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
