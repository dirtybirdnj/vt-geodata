# Screenshots Directory

This directory contains bitmap screenshots of large datasets that are excluded from the unified map viewer due to file size constraints.

## Purpose

Screenshots allow users to:
- See what's in the large census water datasets
- Understand coverage and feature density
- Make informed decisions about which modular alternatives to use
- Preview data without loading massive files

## Adding Screenshots

When you have a large dataset (>5MB) that you're excluding:

1. Open the original HTML map in a browser
2. Take a full-screen screenshot showing:
   - Overall coverage area
   - Feature density
   - Color scheme
   - Info box with statistics
3. Save as PNG: `{map_name}.png`
4. Compress if needed (aim for <500KB per screenshot)

## Screenshots Needed

### High Priority
- [ ] `vt_census_water_all.png` - Vermont all census water (11MB dataset)
- [ ] `ny_census_water_all.png` - New York all census water (53MB dataset)
- [ ] `census_water_champlain.png` - Combined Champlain census water (15MB)

### Medium Priority
- [ ] `vt_opendata_water.png` - VT Open Geodata water (8MB)
- [ ] `champlain_categorized.png` - Categorized water features (12MB)

## File Naming Convention

Use the same name as the HTML file without extension:
- `docs/vt_census_water_all.html` → `screenshots/vt_census_water_all.png`

## Compression

Use PNG compression to keep files reasonable:
```bash
# Using imagemagick
convert original.png -quality 85 -resize 1920x1080 compressed.png

# Using pngquant
pngquant --quality=80-90 original.png
```

## Referencing in Documentation

Link to screenshots in markdown:
```markdown
![VT Census Water All](screenshots/vt_census_water_all.png)
*Complete Vermont census water features - 11MB dataset*
```
