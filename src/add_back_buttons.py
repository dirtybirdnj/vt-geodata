#!/usr/bin/env python3
"""
Add back buttons to all vector HTML pages.
"""

import re

# Files to update
files = [
    'docs/census_water_champlain_vector.html',
    'docs/data_comparison_vector.html',
    'docs/vermont_counties_vector.html',
    'docs/vermont_demo_vector.html',
    'docs/vt_opendata_water_vector.html',
    'docs/ny_boundary_vector.html',
    'docs/nh_boundary_vector.html',
    'docs/ma_boundary_vector.html'
]

# CSS for back button
back_button_css = """
    <style>
        .back-button {
            position: fixed;
            top: 10px;
            right: 10px;
            background: white;
            padding: 10px 15px;
            border-radius: 5px;
            border: 2px solid #000;
            z-index: 9999;
            text-decoration: none;
            color: #000;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: background-color 0.2s;
        }
        .back-button:hover {
            background-color: #f5f5f5;
        }
    </style>
"""

# HTML for back button
back_button_html = """    <a href="index.html" class="back-button">
        <span>←</span>
        <span>Back to Index</span>
    </a>
"""

for filepath in files:
    print(f"Processing {filepath}...")

    with open(filepath, 'r') as f:
        content = f.read()

    # Check if back button already exists
    if 'back-button' in content:
        print(f"  ✓ Already has back button, skipping")
        continue

    # Add CSS before </head>
    content = content.replace('</head>', f'{back_button_css}\n</head>')

    # Add HTML after <body> and background style
    # Find the pattern: <body>\n    <style>body { background-color: white; }
    pattern = r'(<body>\s*<style>body \{ background-color: white; \}[^<]*</style>)'
    replacement = r'\1\n' + back_button_html
    content = re.sub(pattern, replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"  ✓ Added back button")

print("\n✅ All vector pages updated!")
