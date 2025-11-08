#!/usr/bin/env python3
"""
Screenshot automation for HTML visualizations.
Uses Playwright to capture high-quality screenshots of generated maps.
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def capture_screenshot(html_path, output_path, width=1200, height=800, full_page=True):
    """
    Capture a screenshot of an HTML file.

    Args:
        html_path: Path to the HTML file to screenshot
        output_path: Where to save the screenshot
        width: Browser viewport width
        height: Browser viewport height
        full_page: If True, capture the entire page (not just viewport)
    """
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)

        # Create a new page with specified viewport
        page = browser.new_page(viewport={'width': width, 'height': height})

        # Navigate to the HTML file
        file_url = f'file://{os.path.abspath(html_path)}'
        print(f"📸 Loading {html_path}...")
        page.goto(file_url)

        # Wait for page to be fully loaded (important for maps!)
        page.wait_for_load_state('networkidle')

        # For Folium/Leaflet maps, wait a bit longer for tiles to load
        page.wait_for_timeout(2000)  # 2 seconds

        # Capture screenshot (with page's background color)
        print(f"💾 Saving screenshot to {output_path}")
        page.screenshot(path=output_path, full_page=full_page)

        browser.close()
        print(f"✅ Screenshot saved!")


def main():
    """Main function to capture screenshots of all visualizations."""

    # Setup paths
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / 'docs'
    screenshots_dir = project_root / 'screenshots'

    # Create screenshots directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True)
    print(f"📁 Screenshots will be saved to: {screenshots_dir}\n")

    # List of HTML files to screenshot
    html_files = [
        'index.html',
        # 'vt_opendata_water.html',
        # 'census_water_champlain.html',
        # 'vermont_counties.html',
        # 'vermont_demo.html',
        # Add more files here as needed
    ]

    # Capture screenshots
    for html_file in html_files:
        html_path = docs_dir / html_file

        if not html_path.exists():
            print(f"⚠️  Skipping {html_file} - file not found")
            continue

        # Generate output filename (replace .html with .png)
        output_filename = html_file.replace('.html', '.png')
        output_path = screenshots_dir / output_filename

        try:
            capture_screenshot(
                html_path=str(html_path),
                output_path=str(output_path),
                width=1200,
                height=800,
                full_page=True  # Capture entire page
            )
        except Exception as e:
            print(f"❌ Error capturing {html_file}: {e}")

        print()  # Empty line for readability

    print("🎉 All screenshots captured!")
    print(f"\n📂 Find your screenshots in: {screenshots_dir}")


if __name__ == '__main__':
    main()
