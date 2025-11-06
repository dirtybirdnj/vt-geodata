# Quick Start Guide for Python Beginners

Welcome to Python! This guide will get you up and running with the VT GeoData project.

## Step 1: Check Python Installation

macOS usually comes with Python. Let's verify:

```bash
python3 --version
```

You should see something like `Python 3.x.x`. If not, install Python from [python.org](https://www.python.org/downloads/).

## Step 2: Set Up Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects.

```bash
# Create virtual environment (only do this once)
python3 -m venv venv

# Activate it (do this every time you work on the project)
source venv/bin/activate

# You'll see (venv) appear in your terminal prompt
```

To deactivate later: just type `deactivate`

## Step 3: Install Dependencies

```bash
# Make sure you're in the vt-geodata directory and venv is activated
pip install -r requirements.txt
```

This will download all the GIS libraries we need. It might take a few minutes.

## Step 4: Download Your First Dataset

```bash
python src/download.py
```

This will:
- Automatically download Census TIGER shapefiles
- Show you instructions for manual downloads from Vermont Open Geodata Portal

## Step 5: Explore Your Data

After downloading at least one dataset:

```bash
python src/explore.py
```

This creates:
- `output/overview_map.html` - Interactive map you can open in your browser
- `output/comparison.png` - Side-by-side comparison of datasets

## Common Commands

```bash
# Activate virtual environment (do this first, always!)
source venv/bin/activate

# List what datasets you've downloaded
python src/download.py --list

# Explore datasets without creating maps (faster)
python src/explore.py --no-maps

# Process datasets (coming soon)
python src/process.py

# Export to SVG (coming soon)
python src/export.py
```

## Troubleshooting

### "command not found: python3"
- Install Python from python.org or use Homebrew: `brew install python3`

### "No module named 'geopandas'"
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Then run: `pip install -r requirements.txt`

### ImportError or dependency issues
- Try upgrading pip: `pip install --upgrade pip`
- Then reinstall: `pip install -r requirements.txt`

## Python Basics You'll Need

Python uses **indentation** instead of curly braces:

```python
# This is a comment
if condition:
    do_something()  # 4 spaces indent
    do_another_thing()
```

**Variables**: No type declarations needed
```python
name = "Vermont"
count = 42
is_ready = True
```

**Lists** (like arrays):
```python
shapefiles = ['boundary.shp', 'water.shp']
```

**Dictionaries** (like objects):
```python
data = {
    'name': 'Lake Champlain',
    'type': 'water_body'
}
```

## Next Steps

1. Download datasets: `python src/download.py`
2. Explore them: `python src/explore.py`
3. Check the interactive map in `output/overview_map.html`
4. Ready to process? Let's build the processing pipeline!

## Need Help?

- Python is beginner-friendly and error messages are usually helpful
- We'll figure it out together step by step
- Most errors are typos or forgetting to activate the virtual environment
