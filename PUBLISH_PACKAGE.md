# Ortelius Package Publishing Plan

## Package Name: `ortelius`

Named after Abraham Ortelius (1527-1598), creator of the first modern atlas.

## Core Modules

```
ortelius/
├── geometry.py    # cut_features, identify_islands, merge_features, simplify
├── geojson.py     # load, save, filter, transform
├── colors.py      # HSL utilities, per-feature coloring, palettes
├── svg.py         # generate_svg, geometry_to_path, layer styling
└── cli.py         # Command-line interface
```

## Key Features to Document

1. **Water cutouts** - Cut lake/river shapes from town boundaries
2. **Island detection** - Identify islands from MultiPolygon town data
3. **SVG generation** - Print-ready SVGs with simplification levels
4. **Per-feature coloring** - Consistent hash-based color assignment
5. **Layer composition** - Z-ordered layer rendering with styles

## Publishing Steps

1. Rename `geodata_tools/` to `ortelius/`
2. Create `pyproject.toml` with dependencies (shapely, etc.)
3. Add CLI entry points (`ortelius svg`, `ortelius cutout`, etc.)
4. Write docstrings and type hints
5. Add tests for core functions
6. Publish to PyPI: `pip install ortelius`

## CLI Ideas

```bash
ortelius svg --config vermont_12x18.json --output map.svg --quality fine
ortelius cutout --water lake.json --land towns.json --output towns_cut.json
ortelius islands --water lake.json --towns towns.json --output islands.json
```

## Dependencies

- shapely
- (optional) cairosvg for PNG export

## Deferred - Resume After Plotter Export
