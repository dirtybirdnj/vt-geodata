# Unified Map Viewer

A modular, configuration-driven map viewer system that replaces individual HTML files with a single viewer + JSON configuration files.

## Quick Start

### Viewing a Map

Open the map viewer with a configuration parameter:

```
map-viewer.html?config=vermont_demo
```

### Available Maps

- `vermont_demo` - Simple Vermont boundary (test configuration)
- More configurations coming soon...

## Architecture

### Directory Structure

```
viewer/
├── map-viewer.html       # Main HTML file
├── css/
│   └── map-viewer.css   # Styles
├── js/
│   ├── config-loader.js # Load and validate configurations
│   ├── map-core.js      # Initialize Leaflet map
│   ├── layer-handler.js # Load and style GeoJSON layers
│   ├── interaction.js   # Click handlers and selections
│   └── ui-builder.js    # Build info box and UI elements
└── configs/
    └── *.json           # Map configurations
```

### How It Works

1. **URL Parameter** - Map viewer reads `?config=name` from URL
2. **Load Config** - Fetches `configs/name.json` configuration file
3. **Initialize Map** - Creates Leaflet map with specified center/zoom
4. **Load Layers** - Fetches and styles GeoJSON layers
5. **Setup Interactions** - Registers click handlers if enabled
6. **Build UI** - Creates info box, buttons, JSON display

## Creating a New Map

### Step 1: Create Configuration File

Create `configs/my_map.json`:

```json
{
  "id": "my_map",
  "title": "My Map Title",
  "description": "Map description",

  "map": {
    "center": [44.0, -72.7],
    "zoom": 8,
    "tiles": "OpenStreetMap"
  },

  "ui": {
    "colorScheme": "#5c6bc0",
    "infoBox": {
      "width": "450px",
      "content": {
        "subtitle": "Description text",
        "footer": "Source information"
      }
    }
  },

  "layers": [
    {
      "id": "my_layer",
      "name": "My Layer",
      "source": "json/my_data.json",
      "zIndex": 1,
      "style": {
        "type": "static",
        "fillColor": "#3388ff",
        "color": "#0066cc",
        "weight": 2,
        "fillOpacity": 0.5
      },
      "tooltip": {
        "fields": ["NAME"],
        "aliases": ["Name:"]
      }
    }
  ],

  "features": {
    "clickToSelect": {
      "enabled": false
    },
    "jsonDisplay": {
      "enabled": false
    }
  }
}
```

### Step 2: Add GeoJSON Data

Place your GeoJSON file in `../json/my_data.json`

### Step 3: Open Map

Navigate to:
```
map-viewer.html?config=my_map
```

## Configuration Reference

### Map Options

```json
"map": {
  "center": [lat, lon],           // Map center coordinates
  "zoom": 8,                       // Initial zoom level
  "tiles": "OpenStreetMap",        // Base tiles ("OpenStreetMap", "CartoDB", or null for vector-only)
  "attributionControl": true       // Show attribution
}
```

### UI Options

```json
"ui": {
  "colorScheme": "#5c6bc0",        // Theme color (hex or named scheme)
  "infoBox": {
    "width": "450px",              // Info box width
    "content": {
      "subtitle": "...",           // Description text
      "highlights": ["...", "..."], // Highlighted text (optional)
      "legend": [...],             // Legend items (optional)
      "metadata": {...},           // Metadata key-value pairs (optional)
      "footer": "..."              // Footer text (optional)
    }
  }
}
```

### Named Color Schemes

- `vectorBlack` - #000
- `waterBlue` - #1976d2
- `townGreen` - #2c5f2d
- `mashupIndigo` - #5c6bc0
- `emphasizeRed` - #ff6b6b

### Layer Options

```json
"layers": [
  {
    "id": "unique_id",             // Unique layer identifier
    "name": "Display Name",        // Name in layer control
    "source": "json/file.json",    // Path to GeoJSON file
    "zIndex": 1,                   // Layer z-order (lower = bottom)
    "style": {...},                // Style configuration (see below)
    "tooltip": {...},              // Tooltip configuration (optional)
    "interactive": true            // Enable click handlers (default: false)
  }
]
```

### Style Types

**Static Style:**
```json
"style": {
  "type": "static",
  "fillColor": "#3388ff",
  "color": "#0066cc",
  "weight": 2,
  "fillOpacity": 0.5
}
```

**Property-Based Style (Rules):**
```json
"style": {
  "type": "function",
  "property": "state",
  "rules": {
    "VT": {
      "fillColor": "#1976d2",
      "color": "#0d47a1",
      "weight": 1,
      "fillOpacity": 0.5
    },
    "NY": {
      "fillColor": "#d32f2f",
      "color": "#b71c1c",
      "weight": 1,
      "fillOpacity": 0.5
    }
  }
}
```

**Property-Based Style (Color Map):**
```json
"style": {
  "type": "function",
  "property": "county_name",
  "colorMap": "countyColors",
  "borderColor": "#000",
  "weight": 2,
  "fillOpacity": 0.6
}
```

With corresponding color map:
```json
"colorMaps": {
  "countyColors": {
    "Addison": "#66bb6a",
    "Bennington": "#42a5f5",
    ...
  }
}
```

### Interactive Features

**Click to Select:**
```json
"features": {
  "clickToSelect": {
    "enabled": true,
    "multiSelect": true,              // Allow multiple selections
    "layers": ["layer_id"],           // Which layers are clickable
    "highlightStyle": {
      "weight": 4,
      "color": "#000",
      "fillOpacity": 0.9
    }
  }
}
```

**JSON Display:**
```json
"jsonDisplay": {
  "enabled": true,
  "position": "bottom-left",          // "bottom-left", "bottom-right", "top-left"
  "maxHeight": "40vh"
}
```

**Custom Buttons:**
```json
"customButtons": [
  {
    "label": "Clear All",
    "action": "clearSelection",        // "clearSelection" or "exportJSON"
    "position": "bottom-right"
  }
]
```

## Testing

Before deploying a new map configuration:

1. **Validate JSON** - Use a JSON validator to check syntax
2. **Check GeoJSON** - Verify data file exists and loads
3. **Test interactivity** - If enabled, verify click handlers work
4. **Visual check** - Compare with old map (if migrating)
5. **Browser test** - Test in Chrome, Firefox, Safari

## Migration from Old System

When migrating an existing map:

1. Create config file based on old HTML
2. Test side-by-side with old map
3. Verify all features work identically
4. Update index.html link
5. Keep old HTML file until validated

See `../TESTING_VALIDATION_PLAN.md` for detailed testing procedures.

## Troubleshooting

### Map doesn't load

- Check browser console for errors
- Verify config file exists and is valid JSON
- Check GeoJSON file paths are correct

### Layers not appearing

- Verify GeoJSON files exist
- Check file paths (should be relative to `viewer/` directory)
- Check network tab for 404 errors

### Click handlers not working

- Verify `clickToSelect.enabled` is true
- Check `layers` array includes correct layer IDs
- Look for JavaScript errors in console

### Styling issues

- Verify style type matches configuration
- Check property names in style.property match GeoJSON properties
- For color maps, ensure colorMaps object exists

## Examples

See `configs/vermont_demo.json` for a simple example.

More examples will be added as maps are migrated from the old system.

## Development

### Adding New Features

1. Create/modify JavaScript modules in `js/`
2. Update configuration schema in this README
3. Test with existing configurations
4. Update `UNIFIED_MAP_VIEWER_REQUIREMENTS.md`

### Module Responsibilities

- **config-loader.js** - Load, validate, and enhance configurations
- **map-core.js** - Initialize Leaflet map and base tiles
- **layer-handler.js** - Load GeoJSON, apply styles, manage layers
- **interaction.js** - Handle clicks, selections, JSON display
- **ui-builder.js** - Build info box, buttons, UI elements

---

**Version:** 1.0
**Status:** Initial build - testing phase
**Last Updated:** 2025-11-23
