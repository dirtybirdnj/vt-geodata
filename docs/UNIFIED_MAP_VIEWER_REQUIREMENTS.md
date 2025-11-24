# Unified Map Viewer Requirements

**Generated:** 2025-11-23
**Purpose:** Design requirements for a modular, unified map viewer to replace 39 individual HTML files with a single configurable interface.

---

## Executive Summary

Phase 1 standardization of 39 HTML map files revealed consistent patterns and edge cases that inform the design of a unified map viewer. This document catalogs those findings and provides architectural requirements.

**Key Findings:**
- 36 files successfully standardized with back buttons moved into info boxes
- 5 files have click-to-select interactivity that must be preserved
- 22 files include JSON display functionality
- 9 unique color schemes used across maps
- 11 different info box widths (ranging 300-540px)

---

## 1. Core Architecture Requirements

### 1.1 URL-Based Configuration

The unified viewer should load different maps via URL parameters:

```
map-viewer.html?config=towns_over_champlain
map-viewer.html?config=vt_towns_with_water_cutouts
map-viewer.html?config=champlain_categorized
```

### 1.2 Configuration Files

Each map configuration should be a JSON file defining:
- **Data sources** (GeoJSON files to load)
- **Layer styling** (colors, weights, opacity)
- **Interactivity** (click handlers, tooltips)
- **UI elements** (info box content, color scheme)
- **Special features** (JSON display, custom buttons)

Example structure:
```json
{
  "id": "towns_over_champlain",
  "title": "🔬 Third Order: Towns Over Champlain Waters",
  "description": "Mashup visualization to identify data gaps",
  "center": [44.3, -73.2],
  "zoom": 8,
  "colorScheme": "#ff6b6b",
  "infoBoxWidth": "520px",
  "layers": [...],
  "features": {
    "clickToSelect": true,
    "jsonDisplay": true,
    "customButtons": []
  }
}
```

---

## 2. Feature Requirements by Category

### 2.1 Interactive Maps (5 files)

**Files requiring click-to-select:**
1. `champlain_categorized.html` - Category reassignment
2. `towns_over_champlain.html` - Town selection
3. `vermont_simplify.html` - Feature selection
4. `vt_towns_vector.html` - Town selection with Clear button
5. `vt_towns_with_water_cutouts.html` - Town selection with Clear button

**Requirements:**
- Click handler registration for specified layers
- Selection state tracking (multiple or single select)
- Visual feedback on selected features (highlight, border)
- Clear selection functionality
- Export selected features to JSON

**Implementation Pattern:**
```javascript
// From towns_over_champlain.html line ~232
layer.on('click', function(e) {
    const feature = e.target.feature;
    // Track selection
    // Update JSON display
    // Update visual styling
});
```

### 2.2 JSON Display Feature (22 files)

**Purpose:** Display selected feature properties in JSON format

**Position Variants:**
- Bottom-left: `position: fixed; bottom: 10px; left: 10px;` (1 file)
- Bottom-right: `position: fixed; bottom: 20px; right: 20px;` (2 files)
- Top-left (absolute): `position: absolute; top: 60px; left: 10px;` (1 file)
- Many files: No dedicated JSON display div (use browser console)

**Standard Pattern:**
```html
<div class="json-display">
    <h4>Selected Features</h4>
    <pre id="json-output">{}</pre>
</div>
```

**Configuration Option:**
```json
"jsonDisplay": {
    "enabled": true,
    "position": "bottom-left",  // or "bottom-right", "top-left"
    "maxHeight": "40vh"
}
```

### 2.3 Custom Buttons (3 files)

**champlain_categorized.html:**
- Buttons: "Big Lake", "River", "Pond"
- Function: Reassign water feature categories
- Tracking: Changes stored in JSON for export

**vt_towns_vector.html & vt_towns_with_water_cutouts.html:**
- Button: "Clear All"
- Function: Deselect all selected features
- Reset JSON display

**Configuration Option:**
```json
"customButtons": [
    {
        "label": "Clear All",
        "action": "clearSelection",
        "position": "bottom-right"
    },
    {
        "label": "Export JSON",
        "action": "exportJSON",
        "position": "bottom-right"
    }
]
```

---

## 3. Color Scheme Analysis

### 3.1 Identified Color Schemes (9 unique)

| Color | Hex | Usage | Examples |
|-------|-----|-------|----------|
| Black | `#000` | Vector maps (17 files) | All `*_vector.html` files |
| Blue (Material) | `#1e88e5`, `#1976d2` | Water features (7 files) | Census water, Champlain |
| Indigo | `#5c6bc0` | Mashup/combined maps (5 files) | HYDROIDs, categorized |
| Green | `#2c5f2d`, `#27ae60` | Towns/boundaries (5 files) | VT towns, counties |
| Red | `#ff6b6b`, `#d32f2f` | Special emphasis (2 files) | Grand Isle, NY data |
| Sky Blue | `#4a90e2` | OpenData (1 file) | VT OpenData water |

**Pattern:**
- Vector-only maps: Always black (`#000`)
- Water-focused maps: Blue shades (`#1976d2`, `#1e88e5`, `#4a90e2`)
- Town/boundary maps: Green shades (`#2c5f2d`, `#27ae60`)
- Multi-source mashups: Indigo (`#5c6bc0`)
- Highlighting/contrast: Red shades (`#ff6b6b`, `#d32f2f`)

### 3.2 Configuration Approach

Define color schemes in a palette system:

```json
"colorSchemes": {
    "vectorBlack": "#000",
    "waterBlue": "#1976d2",
    "townGreen": "#2c5f2d",
    "mashupIndigo": "#5c6bc0",
    "emphasizeRed": "#ff6b6b"
}
```

Map configs reference scheme by name:
```json
{
    "colorScheme": "waterBlue"
}
```

---

## 4. Info Box Width Variations

### 4.1 Width Distribution

| Width (px) | Count | Usage Pattern |
|------------|-------|---------------|
| 300-350 | 4 | Simple boundary maps |
| 400-450 | 18 | Standard data displays |
| 480-500 | 10 | Complex mashups |
| 520-540 | 2 | Rich content with legends |

**Recommendation:** Standardize to 3 size classes:
- **Small:** 350px (simple maps, minimal info)
- **Medium:** 450px (standard, default)
- **Large:** 520px (complex legends, multiple layers)

---

## 5. Layer Configuration Requirements

### 5.1 Layer Types Observed

1. **Base Tiles**
   - OpenStreetMap (most maps)
   - None/vector-only (all `*_vector.html` files)

2. **GeoJSON Layers**
   - Single layer (simple maps)
   - Multiple layers with z-ordering (mashup maps)

3. **Layer Styles**
   - Static styling (same style for all features)
   - Dynamic styling (function based on properties)

### 5.2 Layer Configuration Schema

```json
"layers": [
    {
        "id": "water_features",
        "source": "json/champlain_tiger_hydroids_combined.json",
        "type": "geojson",
        "zIndex": 1,
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
        },
        "tooltip": {
            "fields": ["FULLNAME", "state", "HYDROID", "area_sqkm"],
            "aliases": ["Name:", "State:", "Hydro ID:", "Area (sq km):"]
        },
        "interactive": false
    },
    {
        "id": "vt_towns",
        "source": "json/vt_towns_with_water_cutouts.json",
        "type": "geojson",
        "zIndex": 2,
        "style": {
            "type": "function",
            "property": "county_name",
            "colorMap": "countyColors",
            "borderColor": "#000000",
            "weight": 1.5,
            "fillOpacity": 0.6
        },
        "tooltip": {
            "fields": ["NAME", "county_name", "water_cutout_applied"],
            "aliases": ["Town:", "County:", "Water Cutout:"]
        },
        "interactive": true,
        "clickable": true
    }
]
```

---

## 6. Special Edge Cases

### 6.1 County Color Mapping

Used by: `towns_over_champlain.html`, `towns_over_hydroids.html`, `vt_towns.html`, `vt_towns_with_water_cutouts.html`

**Standard County Colors:**
```javascript
{
    'Addison': '#66bb6a',
    'Bennington': '#42a5f5',
    'Caledonia': '#ab47bc',
    'Chittenden': '#ef5350',
    'Essex': '#ffa726',
    'Franklin': '#26c6da',
    'Grand Isle': '#7e57c2',
    'Lamoille': '#ec407a',
    'Orange': '#5c6bc0',
    'Orleans': '#9ccc65',
    'Rutland': '#29b6f6',
    'Washington': '#ff7043',
    'Windham': '#26a69a',
    'Windsor': '#ffd54f'
}
```

**Configuration:**
```json
"colorMaps": {
    "countyColors": {
        "Addison": "#66bb6a",
        "Bennington": "#42a5f5",
        ...
    }
}
```

### 6.2 Maps Without Info Box

**File:** `vermont_simplify.html`

This map has click interactivity and JSON display but no info box. The unified viewer should gracefully handle this case with minimal default UI.

### 6.3 Category Reassignment (champlain_categorized.html)

Unique functionality:
- Click feature to open category buttons
- Reassign water feature type
- Track changes in JSON
- Export modified categories

**Requirements:**
- Support for dynamic button generation
- Change tracking system
- Export functionality
- Persistence (optional: localStorage)

---

## 7. Metadata Requirements

### 7.1 Data Source Attribution

Many maps include metadata about feature counts and areas:

```json
"metadata": {
    "total_towns": 256,
    "towns_with_cutouts": 36,
    "total_features": 57,
    "total_area_sqkm": 1101
}
```

Should be:
1. Read from GeoJSON metadata field
2. Calculated dynamically from loaded data
3. Displayed in info box

### 7.2 Transformation Order Notes

Some maps include notes like:
- "First-Order Transformation: Direct from TIGER/Line data"
- "Second-Order Transformation: Combined VT + NY sources"
- "Third-Order Transformation: Mashup visualization for analysis"

**Configuration:**
```json
"transformationOrder": "third",
"notes": "Mashup visualization for analysis"
```

---

## 8. Technical Architecture Recommendations

### 8.1 File Structure

```
docs/
├── map-viewer.html          # Unified viewer
├── js/
│   ├── map-core.js         # Core map initialization
│   ├── layer-handler.js    # Layer loading and styling
│   ├── interaction.js      # Click handlers, selection
│   ├── ui-builder.js       # Info box, buttons, JSON display
│   └── config-loader.js    # Load and parse config files
├── css/
│   └── map-viewer.css      # Standardized styles
├── configs/
│   ├── towns_over_champlain.json
│   ├── vt_towns.json
│   ├── champlain_categorized.json
│   └── ... (39 config files)
└── json/
    └── ... (existing GeoJSON data files)
```

### 8.2 JavaScript Modules

**map-core.js:**
- Initialize Leaflet map
- Load base tiles or vector-only mode
- Set center and zoom from config

**layer-handler.js:**
- Load GeoJSON from URLs
- Apply styling (static or function-based)
- Handle z-ordering
- Add tooltips

**interaction.js:**
- Register click handlers
- Track selections
- Update JSON display
- Handle custom button actions

**ui-builder.js:**
- Build info box from config
- Position and style elements
- Create back link
- Add metadata displays
- Build custom buttons

**config-loader.js:**
- Parse URL parameters
- Load JSON config
- Validate schema
- Provide defaults for missing fields

### 8.3 Backward Compatibility

**Option 1: Redirect**
Keep existing HTML filenames as redirects:
```html
<!-- towns_over_champlain.html -->
<meta http-equiv="refresh" content="0; url=map-viewer.html?config=towns_over_champlain">
```

**Option 2: Dual System**
Maintain both old and new systems during transition:
- Old files in `docs/*.html`
- New system in `docs/viewer/map-viewer.html`
- Update index.html links gradually

---

## 9. Configuration Schema (Full Example)

```json
{
    "id": "towns_over_champlain",
    "version": "1.0",
    "title": "🔬 Third Order: Towns Over Champlain Waters",
    "description": "Mashup visualization to identify data gaps",

    "map": {
        "center": [44.3, -73.2],
        "zoom": 8,
        "tiles": "OpenStreetMap",
        "attributionControl": true
    },

    "ui": {
        "colorScheme": "emphasizeRed",
        "infoBox": {
            "width": "520px",
            "content": {
                "subtitle": "VT Towns overlaid on Lake Champlain water features",
                "highlights": [
                    "★ Grand Isle County (Champlain Islands) shown in RED",
                    "Notice: Island land areas appear small relative to surrounding water"
                ],
                "legend": [
                    {
                        "color": "#0d47a1",
                        "label": "VT - Lake Champlain Main Body"
                    },
                    {
                        "color": "#5c6bc0",
                        "label": "NY - Lake Champlain"
                    },
                    {
                        "color": "#ff6b6b",
                        "border": "3px solid #c92a2a",
                        "label": "Grand Isle County (Champlain Islands)"
                    },
                    {
                        "color": "#66bb6a",
                        "border": "2px solid #2c5f2d",
                        "label": "Other VT Towns"
                    }
                ],
                "footer": "Third Order Transformation: Combining processed data sources"
            }
        }
    },

    "layers": [
        {
            "id": "champlain_water",
            "name": "Lake Champlain Waters",
            "source": "json/census_water_champlain.json",
            "zIndex": 1,
            "style": {
                "type": "function",
                "property": "state",
                "rules": {
                    "VT": {
                        "fillColor": "#0d47a1",
                        "color": "#01579b",
                        "weight": 2,
                        "fillOpacity": 0.6
                    },
                    "NY": {
                        "fillColor": "#5c6bc0",
                        "color": "#3949ab",
                        "weight": 2,
                        "fillOpacity": 0.5
                    }
                }
            },
            "tooltip": {
                "fields": ["FULLNAME", "state", "AWATER"],
                "aliases": ["Name:", "State:", "Area (sq m):"]
            }
        },
        {
            "id": "vt_towns",
            "name": "Vermont Towns",
            "source": "json/vt_towns.json",
            "zIndex": 2,
            "style": {
                "type": "function",
                "property": "county_name",
                "colorMap": "countyColors",
                "borderColor": "#2c5f2d",
                "weight": 2,
                "fillOpacity": 0.7,
                "specialRules": {
                    "property": "county_name",
                    "value": "Grand Isle",
                    "style": {
                        "fillColor": "#ff6b6b",
                        "color": "#c92a2a",
                        "weight": 3
                    }
                }
            },
            "tooltip": {
                "fields": ["NAME", "county_name", "ALAND"],
                "aliases": ["Town:", "County:", "Land Area (sq m):"]
            }
        }
    ],

    "features": {
        "clickToSelect": {
            "enabled": true,
            "multiSelect": true,
            "layers": ["vt_towns"],
            "highlightStyle": {
                "weight": 4,
                "color": "#000",
                "fillOpacity": 0.9
            }
        },
        "jsonDisplay": {
            "enabled": true,
            "position": "bottom-left",
            "maxHeight": "40vh"
        },
        "customButtons": [
            {
                "label": "Clear All",
                "action": "clearSelection",
                "position": "json-display"
            }
        ],
        "layerControl": {
            "enabled": true,
            "position": "topright",
            "collapsed": false
        }
    },

    "colorMaps": {
        "countyColors": {
            "Addison": "#66bb6a",
            "Bennington": "#42a5f5",
            "Caledonia": "#ab47bc",
            "Chittenden": "#ef5350",
            "Essex": "#ffa726",
            "Franklin": "#26c6da",
            "Grand Isle": "#7e57c2",
            "Lamoille": "#ec407a",
            "Orange": "#5c6bc0",
            "Orleans": "#9ccc65",
            "Rutland": "#29b6f6",
            "Washington": "#ff7043",
            "Windham": "#26a69a",
            "Windsor": "#ffd54f"
        }
    },

    "metadata": {
        "transformationOrder": "third",
        "dataSources": [
            "US Census TIGER/Line 2022 - AREAWATER",
            "VT Towns with manual processing"
        ],
        "created": "2025-11-23",
        "tags": ["mashup", "champlain", "towns", "islands"]
    }
}
```

---

## 10. Migration Plan

### Phase 1: Core Infrastructure ✓ COMPLETE
- [x] Standardize existing HTML files
- [x] Document edge cases
- [x] Define requirements

### Phase 2: Build Unified Viewer (NEXT)
- [ ] Create map-viewer.html skeleton
- [ ] Build JavaScript modules (core, layers, interaction, UI)
- [ ] Create CSS for standardized components
- [ ] Implement config loader

### Phase 3: Configuration Migration
- [ ] Generate JSON configs for all 39 maps
- [ ] Validate configs against schema
- [ ] Test each config in unified viewer

### Phase 4: Testing & Refinement
- [ ] Verify all interactive features work
- [ ] Test JSON display functionality
- [ ] Validate color schemes and styling
- [ ] Cross-browser testing

### Phase 5: Deployment
- [ ] Update index.html to link to new viewer
- [ ] Add redirects from old HTML files
- [ ] Deploy to production
- [ ] Archive old HTML files

---

## 11. Success Criteria

A successful unified map viewer implementation will:

1. **Replace 39 HTML files** with 1 viewer + 39 lightweight JSON configs
2. **Preserve all interactivity** (click-to-select, category reassignment, etc.)
3. **Maintain visual consistency** (colors, layouts, info boxes)
4. **Support extensibility** (easy to add new maps via config)
5. **Reduce maintenance burden** (single codebase for bug fixes)
6. **Enable rapid development** (new maps = new config file only)

---

## Appendix A: Files Processed

### Successfully Standardized (36 files)
- census_water_champlain.html
- census_water_champlain_vector.html
- champlain_categorized.html
- champlain_ny_vt.html
- champlain_ny_vt_vector.html
- champlain_tiger_hydroids_combined.html
- champlain_tiger_hydroids_combined_vector.html
- data_comparison_vector.html
- ma_boundary.html
- ma_boundary_vector.html
- nh_boundary.html
- nh_boundary_vector.html
- ny_boundary.html
- ny_boundary_vector.html
- ny_census_water_all.html
- ny_census_water_all_vector.html
- ny_champlain_tiger.html
- ny_champlain_tiger_vector.html
- towns_over_champlain.html
- towns_over_champlain_vector.html
- towns_over_hydroids.html
- towns_over_hydroids_vector.html
- vermont_counties.html
- vermont_counties_vector.html
- vermont_demo.html
- vermont_demo_vector.html
- vermont_with_islands.html
- vt_census_water_all.html
- vt_census_water_all_vector.html
- vt_champlain_tiger.html
- vt_champlain_tiger_vector.html
- vt_opendata_water.html
- vt_opendata_water_vector.html
- vt_towns.html
- vt_towns_vector.html
- vt_towns_with_water_cutouts.html
- vt_towns_with_water_cutouts_vector.html

### Skipped (3 files)
- counties_colored.html (no changes needed)
- towns_over_hydroids.html (already standardized)
- vermont_simplify.html (no info box found)

---

**Document Status:** Complete
**Next Action:** Begin Phase 2 implementation of unified map viewer
