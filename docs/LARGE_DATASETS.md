# Large Dataset Exclusion Policy

## Overview

This project focuses on **modular, reusable geodata chunks** rather than massive all-in-one datasets. Large census water files (11-53MB) are excluded from the unified map viewer to maintain performance and focus on practical use cases.

## Excluded Datasets

### Why These Are Excluded

These datasets contain comprehensive census water features for entire regions. While complete, they are:
- ⚠️ **Too large** for web performance (11-53MB each)
- 📦 **Monolithic** - difficult to use specific parts
- 🔄 **Better replaced** by modular subsets (like HYDROID cutouts)

### Excluded Maps

| Map | File Size | Why Excluded | Alternative |
|-----|-----------|--------------|-------------|
| **vt_census_water_all** | ~11MB | Complete VT census water | Use `vt_champlain_tiger_hydroids` for Lake Champlain |
| **vt_census_water_all_vector** | ~11MB | Vector version | Same as above |
| **ny_census_water_all** | ~53MB | Complete NY census water | Use `ny_champlain_tiger_hydroids` for Lake Champlain |
| **ny_census_water_all_vector** | ~53MB | Vector version | Same as above |
| **census_water_champlain** | ~15MB | Combined census water | Use `champlain_tiger_hydroids_combined` |
| **census_water_champlain_vector** | ~15MB | Vector version | Same as above |
| **vt_opendata_water** | ~8MB | VT Open Geodata water | Use `lake_champlain_water` |
| **vt_opendata_water_vector** | ~8MB | Vector version | Same as above |
| **data_comparison_vector** | Variable | Comparison mashup | Covered by other mashup maps |
| **champlain_categorized** | ~12MB | Categorized water | Use `champlain_ny_vt` |
| **vermont_simplify** | N/A | Interactive tool | Not a map viewer config |

## Modular Alternatives

### Instead of Large Census Files, Use:

**Lake Champlain Water Features:**
- ✅ `vt_champlain_tiger_hydroids` (45 features, ~1.6MB)
- ✅ `ny_champlain_tiger_hydroids` (12 features, ~150KB)
- ✅ `champlain_tiger_hydroids_combined` (57 features, combined)
- ✅ `lake_champlain_water` (VT lake main body)
- ✅ `ny_lake_champlain_water` (NY lake portion)

**Town Boundaries with Water Cutouts:**
- ✅ `vt_towns_with_water_cutouts` (256 towns with geometric water removal)
- ✅ `vt_grand_isle_water_cutouts` (Champlain Islands with cutouts)

**Mashup Visualizations:**
- ✅ `towns_over_hydroids` (towns + TIGER water)
- ✅ `towns_over_champlain` (towns + lake water)
- ✅ `champlain_ny_vt` (combined VT/NY waters)

## Screenshots

Screenshots of excluded large datasets are available in `/docs/screenshots/` for reference without requiring the full data files.

### How to Add Screenshots

```bash
# Take screenshot of map
# Save as PNG: docs/screenshots/{map_name}.png

# Example:
docs/screenshots/vt_census_water_all.png
docs/screenshots/ny_census_water_all.png
```

## Design Philosophy

### ✅ Prefer: Modular, Combined Datasets
- **Small files** that load quickly
- **Focused datasets** for specific regions (Lake Champlain, specific counties)
- **Combined views** that layer multiple sources
- **Interactive features** (click-to-select, JSON export)

### ❌ Avoid: Monolithic Complete Datasets
- All water features for entire state
- Unfiltered census downloads
- Datasets with thousands of tiny features
- Files over 5-10MB without specific use case

## Future Approach

When processing new geodata:

1. **Extract meaningful subsets** (e.g., by region, water body, county)
2. **Create geometric operations** (e.g., water cutouts from boundaries)
3. **Build mashup visualizations** that combine subsets
4. **Test file size** - keep under 5MB per file when possible
5. **Document alternatives** if excluding large source files

## Accessing Original Data

If you need the complete census water datasets:

1. **Generate from source:** Use scripts in `src/` to download from Census TIGER
2. **Local use only:** Keep large files local, don't commit to repo
3. **Extract what you need:** Process to create focused subsets

## Questions?

The goal is **practical, usable geodata** for mapping and analysis, not archive completeness. If you need specific water features from the excluded datasets, create a focused extraction rather than including the entire file.
