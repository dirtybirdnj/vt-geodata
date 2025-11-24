# Testing & Validation Plan for Unified Map Viewer

**Purpose:** Ensure zero functionality loss during migration from 39 individual HTML files to unified map-viewer.html system

**Created:** 2025-11-23
**Status:** Phase 1 Complete, Ready for Phase 2 Testing

---

## Overview

This document outlines the testing strategy to ensure that the unified map viewer preserves all functionality from the existing 39 HTML files. The goal is to prevent regression bugs and ensure a smooth migration with comprehensive validation.

---

## Testing Philosophy

**"Don't throw anything away"** - Every feature, interaction, and visual element in the current system must be verified in the new system before cutover.

**Testing Phases:**
1. **Baseline Documentation** - Catalog all current functionality (DONE in Phase 1)
2. **Parallel Development** - Build unified viewer while keeping old system intact
3. **Feature Parity Testing** - Validate each feature works identically
4. **Visual Regression Testing** - Ensure maps look correct
5. **User Acceptance Testing** - Manual verification of all maps
6. **Performance Testing** - Ensure new system is performant
7. **Cutover with Rollback Plan** - Safe migration strategy

---

## 1. Baseline Documentation (✓ COMPLETE)

### Current State Captured

✓ **Edge Cases Report** (`docs/edge_cases_report.json`)
- 5 interactive maps identified
- 22 maps with JSON displays
- 3 maps with custom buttons
- Color schemes cataloged
- Width variations documented

✓ **Requirements Document** (`docs/UNIFIED_MAP_VIEWER_REQUIREMENTS.md`)
- Full technical specifications
- Configuration schema examples
- Layer patterns documented
- Special features cataloged

✓ **Standardized UI** (Phase 1)
- All maps have consistent top-left layout
- Back buttons integrated into info boxes
- Positions standardized to `top: 10px; left: 10px`

---

## 2. Testing Categories

### 2.1 Functional Testing

#### A. Interactive Features (5 maps - CRITICAL)

**Maps to Test:**
1. `champlain_categorized.html` - Category reassignment
2. `towns_over_champlain.html` - Town selection
3. `vermont_simplify.html` - Feature selection
4. `vt_towns_vector.html` - Town selection with Clear button
5. `vt_towns_with_water_cutouts.html` - Town selection with Clear button

**Test Cases:**

| Test ID | Feature | Old System Behavior | New System Expected | Status |
|---------|---------|---------------------|---------------------|--------|
| INT-01 | Click feature to select | Feature highlights, adds to selection | Same | ⏳ |
| INT-02 | Multi-select support | Can select multiple features | Same | ⏳ |
| INT-03 | Selection highlighting | Selected features have bold border | Same | ⏳ |
| INT-04 | JSON display updates | Selection shows in JSON panel | Same | ⏳ |
| INT-05 | Clear All button | Deselects all, clears JSON | Same | ⏳ |
| INT-06 | Category reassignment (categorized map) | Buttons appear, can reassign | Same | ⏳ |
| INT-07 | Change tracking | Modified features tracked separately | Same | ⏳ |

**Acceptance Criteria:**
- ✓ All click handlers register correctly
- ✓ Selection state persists across interactions
- ✓ Visual feedback matches old system
- ✓ JSON output format identical
- ✓ Clear button resets state completely
- ✓ Category buttons function identically

#### B. JSON Display (22 maps)

**Test Cases:**

| Test ID | Feature | Validation |
|---------|---------|------------|
| JSON-01 | Display appears in correct position | bottom-left, bottom-right, or top-left as configured |
| JSON-02 | JSON formatting | Pretty-printed, valid JSON syntax |
| JSON-03 | Feature properties included | All properties from GeoJSON preserved |
| JSON-04 | Updates on selection | Real-time update when clicking features |
| JSON-05 | Scroll behavior | Scrollable when content exceeds max-height |
| JSON-06 | Copy functionality | Can select and copy JSON text |

**Spot Check Maps:**
- `towns_over_champlain.html` (bottom-left)
- `vt_towns_with_water_cutouts.html` (bottom-right)
- `champlain_categorized.html` (top-left absolute)

#### C. Custom Buttons (3 maps)

**Test Cases:**

| Test ID | Map | Button | Action | Expected Result |
|---------|-----|--------|--------|-----------------|
| BTN-01 | champlain_categorized.html | Big Lake | Reassign category | Feature category changes to "Big Lake" |
| BTN-02 | champlain_categorized.html | River | Reassign category | Feature category changes to "River" |
| BTN-03 | champlain_categorized.html | Pond | Reassign category | Feature category changes to "Pond" |
| BTN-04 | vt_towns_vector.html | Clear All | Clear selection | All selections cleared, JSON reset |
| BTN-05 | vt_towns_with_water_cutouts.html | Clear All | Clear selection | All selections cleared, JSON reset |

### 2.2 Visual Regression Testing

**Tool Options:**
- Manual screenshot comparison (simple, effective)
- Percy.io or similar (automated visual diffs)
- Browser DevTools screenshot comparison

**Maps to Visually Validate (Sample - 10 maps):**

| Priority | Map | Reason |
|----------|-----|--------|
| HIGH | towns_over_champlain.html | Complex legend, Grand Isle red highlight |
| HIGH | champlain_categorized.html | Category buttons, info box styling |
| HIGH | vt_towns_with_water_cutouts.html | County colors, water cutouts |
| MEDIUM | champlain_tiger_hydroids_combined.html | Two-layer mashup |
| MEDIUM | vt_champlain_tiger.html | Blue water styling |
| MEDIUM | ny_champlain_tiger.html | NY red water styling |
| MEDIUM | vermont_counties_vector.html | Vector-only rendering |
| LOW | ma_boundary.html | Simple boundary display |
| LOW | vermont_demo.html | Basic state outline |
| LOW | data_comparison_vector.html | Comparison view |

**Visual Checklist per Map:**
- [ ] Info box position (top: 10px, left: 10px)
- [ ] Info box width matches original
- [ ] Back to Index link styled correctly (color matches theme)
- [ ] Border color matches theme
- [ ] Title text correct
- [ ] Description text correct
- [ ] Legend items (if present) match
- [ ] Footer text present
- [ ] Layer colors match
- [ ] Layer borders match
- [ ] Tooltip styling consistent
- [ ] JSON display (if present) positioned correctly
- [ ] Custom buttons (if present) styled correctly

### 2.3 Data Integrity Testing

**Verify that all GeoJSON data loads correctly:**

**Test Cases:**

| Test ID | Validation | Method |
|---------|------------|--------|
| DATA-01 | All GeoJSON files load | Check network tab, no 404s |
| DATA-02 | Feature counts match | Compare feature count in old vs new |
| DATA-03 | Properties preserved | Spot-check property values |
| DATA-04 | Geometries render correctly | Visual comparison of shapes |
| DATA-05 | Metadata displays | Verify counts (e.g., "256 towns") |
| DATA-06 | Tooltips show correct data | Hover over features, verify fields |

**Sample Data Validation (5 maps):**

| Map | Expected Feature Count | Properties to Verify |
|-----|------------------------|----------------------|
| vt_towns.html | 256 towns | NAME, county_name, ALAND |
| champlain_tiger_hydroids_combined.html | 57 water features | FULLNAME, state, HYDROID, area_sqkm |
| vt_towns_with_water_cutouts.html | 256 towns (36 with cutouts) | water_cutout_applied, new_land_area_sqkm |
| census_water_champlain.html | Census water features | FULLNAME, AWATER |
| vermont_counties.html | 14 counties | COUNTYFP, NAME |

### 2.4 Layer Styling Testing

**Verify styling functions work correctly:**

**Test Cases:**

| Test ID | Styling Type | Example Map | Validation |
|---------|--------------|-------------|------------|
| STYLE-01 | Static styling | vermont_demo.html | All features same color |
| STYLE-02 | Property-based coloring | vt_towns.html | Counties have different colors |
| STYLE-03 | Conditional styling | towns_over_champlain.html | Grand Isle County is red |
| STYLE-04 | State-based styling | champlain_ny_vt.html | VT blue, NY red |
| STYLE-05 | Border weight variation | vt_towns_with_water_cutouts.html | Cutout towns have thicker borders |
| STYLE-06 | Opacity settings | All maps | Verify fillOpacity values |

**County Color Validation:**

Verify standard county color map on these maps:
- `vt_towns.html`
- `towns_over_champlain.html`
- `towns_over_hydroids.html`
- `vt_towns_with_water_cutouts.html`

Expected colors:
```
Addison: #66bb6a (green)
Bennington: #42a5f5 (blue)
Caledonia: #ab47bc (purple)
Chittenden: #ef5350 (red)
Essex: #ffa726 (orange)
Franklin: #26c6da (cyan)
Grand Isle: #7e57c2 (violet) OR #ff6b6b (red - special case in towns_over_champlain)
...
```

### 2.5 Performance Testing

**Metrics to Track:**

| Metric | Current (Old System) | Target (New System) | Acceptable Range |
|--------|---------------------|---------------------|------------------|
| Initial page load | Baseline per map | Same or better | ±10% |
| GeoJSON load time | Baseline per map | Same or better | ±20% |
| Feature click response | <100ms | <100ms | Must be instant |
| JSON display update | <50ms | <50ms | Must be instant |
| Map pan/zoom smoothness | 60fps | 60fps | No jank |

**Large File Tests (Important!):**

GitHub warned about these large files:
- `ny_census_water_all.html` (53.03 MB)
- `ny_census_water_all_vector.html` (54.25 MB)

**Test:**
- Load time acceptable
- Browser doesn't freeze/crash
- Can interact smoothly after load
- Consider data optimization or lazy loading

### 2.6 Browser Compatibility Testing

**Browsers to Test:**

| Browser | Version | Priority | Tested? |
|---------|---------|----------|---------|
| Chrome | Latest | HIGH | ⏳ |
| Firefox | Latest | HIGH | ⏳ |
| Safari | Latest | HIGH | ⏳ |
| Edge | Latest | MEDIUM | ⏳ |
| Mobile Safari (iOS) | Latest | MEDIUM | ⏳ |
| Mobile Chrome (Android) | Latest | LOW | ⏳ |

**Features to Verify:**
- Leaflet map renders
- Click handlers work
- JSON display appears
- CSS flexbox/grid layouts
- Arrow character (←) displays correctly

### 2.7 URL and Navigation Testing

**Test Cases:**

| Test ID | Scenario | Expected Behavior |
|---------|----------|-------------------|
| NAV-01 | Direct URL to map | Loads correct configuration |
| NAV-02 | Invalid config parameter | Shows error message, suggests valid configs |
| NAV-03 | Missing config parameter | Shows default/index of available maps |
| NAV-04 | Back to Index link | Returns to index.html |
| NAV-05 | Browser back button | Returns to previous page |
| NAV-06 | Bookmark/share URL | Loads same map configuration |
| NAV-07 | Refresh page | Reloads map, preserves state (if implemented) |

---

## 3. Testing Workflow

### Phase 2A: Initial Development (In Progress)

**During Development:**
1. Build one module at a time (core, layers, interaction, UI)
2. Unit test each module in isolation
3. Use 2-3 simple maps for initial integration testing
4. Verify functionality before adding complexity

**Recommended Test Maps for Development:**
- **Simple:** `vermont_demo.html` (basic boundary, no interactivity)
- **Medium:** `vt_towns.html` (county colors, tooltips, no click)
- **Complex:** `towns_over_champlain.html` (multi-layer, click, JSON, legend)

### Phase 2B: Parallel System Testing

**Strategy:** Keep both old and new systems running side-by-side

**Directory Structure During Testing:**
```
docs/
├── index.html                    # Links to old system
├── index_new.html                # Links to new viewer
├── *.html                        # Old individual maps (keep intact)
├── viewer/
│   ├── map-viewer.html          # New unified viewer
│   ├── js/
│   ├── css/
│   └── configs/
└── json/                         # Shared data files
```

**Testing Process:**
1. Deploy both systems to test server
2. Test new viewer with each config
3. Compare side-by-side with old map
4. Document any discrepancies
5. Fix issues in new viewer
6. Re-test until parity achieved

### Phase 2C: Systematic Validation (Before Cutover)

**Checklist Approach - All 39 Maps:**

Create a testing spreadsheet with columns:
- Map Name
- Config File Created
- Visual Regression Pass
- Functional Test Pass
- Data Integrity Pass
- Performance Acceptable
- Issues Found
- Issues Resolved
- Ready for Cutover

**Testing Order (Suggested):**

1. **Week 1:** Simple maps (no interactivity)
   - Boundary maps (6 files)
   - County/demo maps (4 files)

2. **Week 2:** Medium complexity (tooltips, styling)
   - Water feature maps (10 files)
   - Town maps (6 files)

3. **Week 3:** Complex maps (multi-layer, legends)
   - Champlain mashups (6 files)
   - Combined/comparison maps (4 files)

4. **Week 4:** Interactive maps (CRITICAL)
   - All 5 interactive maps
   - Intensive testing of click handlers
   - Validate JSON displays
   - Test custom buttons

5. **Week 5:** Final validation
   - Re-test any fixed issues
   - Full browser compatibility sweep
   - Performance validation
   - User acceptance testing

---

## 4. Issue Tracking Template

**For each issue found:**

```markdown
### Issue #XXX: [Short Description]

**Map:** `map_name.html`
**Severity:** Critical / High / Medium / Low
**Category:** Functional / Visual / Data / Performance

**Current Behavior (Old System):**
[What happens in the old system]

**Expected Behavior (New System):**
[What should happen]

**Actual Behavior (New System):**
[What actually happens]

**Steps to Reproduce:**
1. Load map-viewer.html?config=map_name
2. Click on [feature]
3. Observe [behavior]

**Screenshots:**
- Old system: [screenshot]
- New system: [screenshot]

**Fix Required:**
[Description of what needs to be fixed]

**Status:** Open / In Progress / Testing / Closed
**Fixed In:** [commit hash or PR number]
```

---

## 5. Rollback Plan

**If critical issues are discovered during/after cutover:**

### Immediate Rollback (< 5 minutes)

**Option 1: Git Revert**
```bash
# Revert to last known good commit
git revert [commit-hash]
git push origin main
```

**Option 2: Branch Switch**
```bash
# Keep old system on a branch
git checkout old-system-backup
git push origin main --force
```

**Option 3: Manual Restore**
- Restore old `index.html` linking to individual maps
- Keep individual map HTML files intact during testing phase
- No data loss - old files never deleted until validation complete

### Gradual Rollback (Partial Cutover)

If some maps work but others don't:

```html
<!-- index.html hybrid approach -->
<h2>Maps (New Viewer)</h2>
<ul>
  <li><a href="viewer/map-viewer.html?config=vt_towns">VT Towns</a> ✓</li>
  <li><a href="viewer/map-viewer.html?config=vermont_demo">Demo</a> ✓</li>
</ul>

<h2>Maps (Legacy - Under Migration)</h2>
<ul>
  <li><a href="champlain_categorized.html">Champlain Categorized</a> ⚠️</li>
  <li><a href="towns_over_champlain.html">Towns Over Champlain</a> ⚠️</li>
</ul>
```

---

## 6. Success Criteria for Cutover

**All criteria must be met before replacing old system:**

### Functional Requirements
- [ ] All 39 config files created and validated
- [ ] All 5 interactive maps work identically to old system
- [ ] All 22 JSON displays function correctly
- [ ] All 3 custom button implementations work
- [ ] Layer styling matches old system (spot-checked on 10+ maps)
- [ ] Tooltips display correct data on all maps
- [ ] Back to Index navigation works on all maps

### Visual Requirements
- [ ] Info boxes positioned correctly (top-left, consistent)
- [ ] Color schemes match originals (9 schemes validated)
- [ ] Legends render correctly (where applicable)
- [ ] County colors correct (4 maps validated)
- [ ] No visual regressions found in spot-check sample

### Data Integrity Requirements
- [ ] All GeoJSON files load successfully
- [ ] Feature counts match old system
- [ ] Properties preserved in tooltips and JSON displays
- [ ] Metadata displays correctly (feature counts, areas)

### Performance Requirements
- [ ] Page load times acceptable (within ±10% of old system)
- [ ] No browser freezing/crashing on large files
- [ ] Interaction responsiveness <100ms
- [ ] Map pan/zoom smooth (60fps)

### Compatibility Requirements
- [ ] Works in Chrome (latest)
- [ ] Works in Firefox (latest)
- [ ] Works in Safari (latest)
- [ ] Works on mobile Safari (tested on iPhone)

### Documentation Requirements
- [ ] README updated with new architecture
- [ ] Config schema documented
- [ ] Adding new maps documented
- [ ] Troubleshooting guide created

### Safety Requirements
- [ ] Old system files backed up
- [ ] Rollback plan tested
- [ ] Git tag created for last old-system commit
- [ ] Can restore old system in <5 minutes if needed

---

## 7. Post-Cutover Monitoring

**Week 1 After Cutover:**
- [ ] Monitor for user-reported issues
- [ ] Check browser console for JavaScript errors
- [ ] Verify analytics (page views, bounce rates)
- [ ] Test all interactive maps daily

**Week 2-4 After Cutover:**
- [ ] Spot-check random maps weekly
- [ ] Address any reported bugs
- [ ] Optimize performance if needed
- [ ] Collect user feedback

**After 1 Month Stable:**
- [ ] Archive old HTML files (don't delete, just move to `/archive`)
- [ ] Update documentation
- [ ] Consider additional features for unified viewer

---

## 8. Test Automation Opportunities

### Automated Tests to Consider

**JavaScript Unit Tests (Jest/Mocha):**
```javascript
describe('Config Loader', () => {
  test('loads valid config from URL', () => {
    // Test config loading
  });

  test('handles missing config parameter', () => {
    // Test error handling
  });
});

describe('Layer Styling', () => {
  test('applies county colors correctly', () => {
    // Test color map function
  });

  test('handles conditional styling', () => {
    // Test special cases like Grand Isle
  });
});

describe('Selection Manager', () => {
  test('tracks multiple selections', () => {
    // Test multi-select
  });

  test('clears all selections', () => {
    // Test clear button
  });
});
```

**Integration Tests (Playwright/Cypress):**
```javascript
test('Click to select town', async ({ page }) => {
  await page.goto('/viewer/map-viewer.html?config=vt_towns');

  // Wait for map to load
  await page.waitForSelector('.leaflet-container');

  // Click a feature
  await page.click('[data-town="Burlington"]');

  // Verify JSON display updates
  const jsonDisplay = await page.textContent('#json-output');
  expect(jsonDisplay).toContain('Burlington');
});
```

**Visual Regression (Percy/BackstopJS):**
```javascript
// Capture screenshots of all maps
const configs = ['vt_towns', 'towns_over_champlain', ...];

configs.forEach(config => {
  test(`Visual: ${config}`, async ({ page }) => {
    await page.goto(`/viewer/map-viewer.html?config=${config}`);
    await page.waitForLoadState('networkidle');
    await percySnapshot(page, config);
  });
});
```

---

## 9. Documentation for Testers

### Quick Test Guide for Non-Technical Users

**Testing a Single Map:**

1. Open the old map: `https://[your-domain]/docs/vt_towns.html`
2. Take a screenshot
3. Note any interactive features (can you click things?)
4. Open the new map: `https://[your-domain]/docs/viewer/map-viewer.html?config=vt_towns`
5. Take a screenshot
6. Compare:
   - Does it look the same?
   - Do the colors match?
   - Can you click the same things?
   - Does the info box have all the same text?
7. Report any differences

**What to Look For:**
- ✓ Info box in top-left corner
- ✓ "Back to Index" link inside info box
- ✓ Title matches
- ✓ Colors match
- ✓ Legend (if present) matches
- ✓ Can click features (if old map could)
- ✓ JSON display appears (if old map had it)
- ✓ Buttons work (if old map had them)

---

## 10. Final Checklist Before "Lighting the Candle"

**Pre-Flight Checklist:**

### Code Readiness
- [ ] All JavaScript modules written and tested
- [ ] All 39 config files created
- [ ] CSS styles finalized
- [ ] No console errors in browser DevTools
- [ ] No network errors (404s) when loading maps
- [ ] Code committed to git with descriptive messages

### Testing Complete
- [ ] 39/39 maps visually validated
- [ ] 5/5 interactive maps functionally tested
- [ ] Data integrity verified on sample maps
- [ ] Performance acceptable on large files
- [ ] Browser compatibility confirmed
- [ ] Mobile testing completed (if required)

### Documentation Ready
- [ ] README.md updated
- [ ] Config schema documented
- [ ] Adding new maps guide written
- [ ] Known issues documented (if any)
- [ ] Migration notes written

### Safety Measures
- [ ] Old system backed up
- [ ] Git tag created: `git tag old-system-backup`
- [ ] Rollback procedure tested
- [ ] Can restore old system in <5 minutes
- [ ] Team notified of cutover plan
- [ ] Off-hours cutover scheduled (if production)

### User Communication
- [ ] Users notified of upcoming changes
- [ ] Feedback channel established (email/form)
- [ ] Quick start guide available
- [ ] Known differences documented

---

## Appendix A: Test Data Sets

### Minimal Test Set (Quick Validation)
- `vermont_demo.html` - Simple boundary
- `vt_towns.html` - County colors
- `towns_over_champlain.html` - Interactive with legend

### Representative Sample (Comprehensive)
- 2 boundary maps (VT, MA)
- 2 county/region maps (VT counties, colored)
- 3 water feature maps (VT, NY, combined)
- 2 TIGER HYDROIDs maps (VT, combined)
- 3 towns maps (VT, with cutouts, vector)
- 2 mashup maps (towns over Champlain, towns over HYDROIDs)
- 1 categorization map (champlain_categorized)
- 2 vector-only maps (any *_vector.html)

### Full Regression (All 39 Maps)
- See complete list in UNIFIED_MAP_VIEWER_REQUIREMENTS.md Appendix A

---

## Appendix B: Regression Testing Spreadsheet Template

**Create a Google Sheet or CSV with these columns:**

| Map Name | Config Exists | Visual OK | Functional OK | Data OK | Perf OK | Browser OK | Issues | Resolved | Ready |
|----------|---------------|-----------|---------------|---------|---------|------------|--------|----------|-------|
| vermont_demo.html | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None | N/A | ✓ |
| vt_towns.html | ✓ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | | | |
| ... | | | | | | | | | |

**Legend:**
- ✓ = Pass
- ✗ = Fail
- ⏳ = Not yet tested
- ⚠️ = Minor issue, not blocking

---

**Document Status:** Complete
**Next Steps:** Begin Phase 2 development with testing-first approach
**Cutover Target:** TBD based on testing completion
