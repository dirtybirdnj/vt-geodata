# Unified Map Viewer - Testing Progress

## Status: Phase 2 Testing In Progress

Last Updated: November 24, 2025

---

## Configs Created (4 / 39)

### ✅ Completed & Ready for Testing

1. **vermont_demo.json** ✓
   - Type: Simple boundary
   - Features: Static styling, tooltips
   - Test URL: `https://dirtybirdnj.github.io/vt-geodata/viewer/map-viewer.html?config=vermont_demo`
   - Status: Created in Phase 2, needs testing

2. **vermont_counties.json** ✓
   - Type: Simple polygons
   - Features: Static styling, tooltips
   - Test URL: `https://dirtybirdnj.github.io/vt-geodata/viewer/map-viewer.html?config=vermont_counties`
   - Status: Just created, needs testing

3. **ma_boundary.json** ✓
   - Type: Simple boundary (different state)
   - Features: Static styling, validates pattern works for other states
   - Test URL: `https://dirtybirdnj.github.io/vt-geodata/viewer/map-viewer.html?config=ma_boundary`
   - Status: Just created, needs testing

4. **vt_towns.json** ✓
   - Type: Complex with 256 features
   - Features: **ColorMap styling** (14 county colors), tooltips, stats display
   - Test URL: `https://dirtybirdnj.github.io/vt-geodata/viewer/map-viewer.html?config=vt_towns`
   - Status: Just created, **tests colorMap functionality**

---

## Testing Checklist

### Basic Functionality (Config 1-4)

For each config above, verify:

- [ ] **vermont_demo**
  - [ ] Page loads without console errors
  - [ ] Map displays with correct center/zoom
  - [ ] Vermont boundary renders in light green
  - [ ] Info box displays correctly in top-left
  - [ ] Tooltip shows state name on hover
  - [ ] Back button works

- [ ] **vermont_counties**
  - [ ] 14 counties render
  - [ ] Counties are colored green
  - [ ] Info box shows "256 Vermont towns colored by county"
  - [ ] Tooltip shows county name
  - [ ] Styling consistent with original

- [ ] **ma_boundary**
  - [ ] Massachusetts boundary renders in red/pink tones
  - [ ] Map centered on Massachusetts
  - [ ] Info box uses red color scheme
  - [ ] Pattern works for non-Vermont states

- [ ] **vt_towns** (CRITICAL - Tests ColorMap)
  - [ ] All 256 towns load
  - [ ] Towns colored by county (14 different colors)
  - [ ] Each county has distinct color:
    - Addison: #66bb6a (green)
    - Bennington: #42a5f5 (blue)
    - Chittenden: #ef5350 (red)
    - Etc. (14 total)
  - [ ] Tooltip shows town name, county, area
  - [ ] Stats display shows "Total Towns: 256"
  - [ ] No performance issues with 256 features

### Visual Comparison

- [ ] Side-by-side test: `vermont_demo.html` vs `viewer/?config=vermont_demo`
  - [ ] Colors match
  - [ ] Info box content matches
  - [ ] Map position/zoom matches

- [ ] Side-by-side test: `vermont_counties.html` vs `viewer/?config=vermont_counties`
  - [ ] Visual appearance identical

- [ ] Side-by-side test: `vt_towns.html` vs `viewer/?config=vt_towns`
  - [ ] County colors match exactly
  - [ ] Border styling matches

### Technical Validation

- [ ] Browser Console (Chrome DevTools)
  - [ ] No JavaScript errors
  - [ ] No 404 errors for resources
  - [ ] Config loads successfully
  - [ ] GeoJSON loads successfully
  - [ ] All modules initialize

- [ ] Performance
  - [ ] Maps load in < 2 seconds
  - [ ] No lag when panning/zooming
  - [ ] vt_towns (256 features) performs acceptably

### Browser Compatibility

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

---

## Known Issues

### None reported yet

(Will be filled in as testing progresses)

---

## Next Configs to Create (Priority Order)

After validating the 4 configs above work correctly:

### Simple Maps (Priority 1 - Next 5)
5. **nh_boundary.json** - New Hampshire boundary
6. **ny_boundary.json** - New York boundary
7. **vermont_counties_colored.json** - Counties with distinct colors each
8. **vt_towns_vector.json** - Vector-only mode test (no base tiles)

### Water Features (Priority 2 - Next 3)
9. **vt_champlain_tiger_hydroids.json** - VT Champlain water
10. **ny_champlain_tiger_hydroids.json** - NY Champlain water
11. **champlain_tiger_hydroids_combined.json** - Combined VT+NY water (2 layers)

### Interactive Maps (Priority 3 - Critical Test)
12. **vt_towns_with_water_cutouts.json** - **Interactive with click-to-select**
    - Tests: Click handlers, JSON display, selection state
    - This is CRITICAL - validates interactive features work

---

## Success Criteria for Phase 2

Before creating remaining 27 configs:

✅ **Must Complete:**
1. All 4 current configs load without errors
2. ColorMap functionality works (vt_towns)
3. Visual comparison matches original maps
4. No browser console errors
5. Performance acceptable

⏳ **Then:**
6. Create 1 interactive config (vt_towns_with_water_cutouts)
7. Test click-to-select, JSON display
8. If all works: Proceed with remaining configs systematically

---

## Testing Commands

### View Config on GitHub Pages
```
https://dirtybirdnj.github.io/vt-geodata/viewer/map-viewer.html?config=[name]
```

### View Original HTML
```
https://dirtybirdnj.github.io/vt-geodata/[name].html
```

### Local Testing (if needed)
```bash
cd docs/viewer
python3 -m http.server 8000
# Visit: http://localhost:8000/map-viewer.html?config=vermont_demo
```

---

## Rollback Plan

If critical issues found:
1. Old HTML maps still fully functional
2. Can revert viewer commits: `git revert [commit]`
3. Can deploy hybrid: some maps on viewer, some on old HTML
4. No risk to production - parallel systems

---

## Notes

- All configs use relative paths: `../json/filename.json`
- ColorMap requires `type: "colorMap"` + `property` + `colorMap` object
- Stats in info box: use `"stats": [{ "label": "...", "value": "..." }]`
- Vector-only maps: set `"tiles": null` in map config

---

**Current Focus:** Validate these 4 configs work correctly before proceeding with more configs.

**Next Session:** Test URLs above, check browser console, document any issues found.
