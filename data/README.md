# Data Directory

This directory contains raw source data files used for generating map visualizations.

## Structure

- `excel/` - Excel files with lat/lng coordinates and location data

## Processing

Excel files in this directory can be converted to GeoJSON format using Python scripts in the `src/` directory, then visualized using the unified map viewer in `docs/viewer/`.

## Workflow

1. Add Excel files to `data/excel/`
2. Run processing script to convert to GeoJSON
3. Save GeoJSON output to `docs/json/`
4. Create viewer config in `docs/viewer/configs/`
5. View at: `docs/viewer/map-viewer.html?config=your_config_name`
