#!/usr/bin/env python3
"""
Screenshot automation for HTML visualizations.
Uses Playwright to capture high-quality screenshots of generated maps.

Requires a local HTTP server to avoid CORS issues with file:// URLs.
"""

import os
import json
import threading
import http.server
import socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright


class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses request logging."""
    def log_message(self, format, *args):
        pass  # Suppress log output


def start_server(directory, port=8000):
    """Start a local HTTP server serving the given directory."""
    os.chdir(directory)
    handler = QuietHTTPHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def capture_screenshot(url, output_path, width=1200, height=800, full_page=False, wait_ms=3000):
    """
    Capture a screenshot of a URL (file:// or http://).

    Args:
        url: URL to screenshot (can be file:// path)
        output_path: Where to save the screenshot
        width: Browser viewport width
        height: Browser viewport height
        full_page: If True, capture the entire page (not just viewport)
        wait_ms: Milliseconds to wait after networkidle for map tiles
    """
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)

        # Create a new page with specified viewport
        page = browser.new_page(viewport={'width': width, 'height': height})

        # Navigate to the URL
        print(f"📸 Loading {url}...")
        page.goto(url)

        # Wait for page to be fully loaded (important for maps!)
        page.wait_for_load_state('networkidle')

        # Wait for Leaflet maps to finish loading tiles and GeoJSON
        page.wait_for_timeout(wait_ms)

        # Capture screenshot (with page's background color)
        print(f"💾 Saving screenshot to {output_path}")
        page.screenshot(path=output_path, full_page=full_page)

        browser.close()
        print(f"✅ Screenshot saved!")


def get_config_names(configs_dir):
    """Get all config names from the configs directory."""
    configs = []
    for config_file in sorted(configs_dir.glob('*.json')):
        config_name = config_file.stem  # filename without extension
        configs.append(config_name)
    return configs


def screenshot_viewer_configs(docs_dir, base_url, screenshots_dir, configs=None, hide_ui=True):
    """
    Screenshot all viewer configurations.

    Args:
        docs_dir: Path to docs directory (for config discovery)
        base_url: HTTP base URL for the server
        screenshots_dir: Path to save screenshots
        configs: Optional list of config names. If None, auto-discover all.
        hide_ui: If True, hide info box and JSON display for cleaner screenshots.
    """
    configs_dir = docs_dir / 'viewer' / 'configs'

    # Get config names
    if configs is None:
        configs = get_config_names(configs_dir)

    print(f"📋 Found {len(configs)} configurations to screenshot")
    print(f"   UI overlays: {'hidden' if hide_ui else 'visible'}\n")

    # Create viewer screenshots subdirectory
    viewer_screenshots_dir = screenshots_dir / 'viewer'
    viewer_screenshots_dir.mkdir(exist_ok=True)

    success_count = 0
    fail_count = 0

    for i, config_name in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] {config_name}")

        # Build HTTP URL with config parameter (and hideUI if requested)
        hide_param = '&hideUI=true' if hide_ui else ''
        viewer_url = f'{base_url}/viewer/map-viewer.html?config={config_name}{hide_param}'
        output_path = viewer_screenshots_dir / f'{config_name}.png'

        try:
            capture_screenshot(
                url=viewer_url,
                output_path=str(output_path),
                width=1200,
                height=800,
                full_page=False,  # Just viewport for maps
                wait_ms=4000  # 4 seconds for GeoJSON loading
            )
            success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            fail_count += 1

        print()

    return success_count, fail_count


def screenshot_index(base_url, screenshots_dir):
    """Screenshot the main index page."""
    output_path = screenshots_dir / 'index.png'

    try:
        capture_screenshot(
            url=f'{base_url}/index.html',
            output_path=str(output_path),
            width=1200,
            height=900,
            full_page=True,  # Full page for index
            wait_ms=2000
        )
        return True
    except Exception as e:
        print(f"❌ Error capturing index: {e}")
        return False


def main():
    """Main function to capture screenshots of all visualizations."""
    import argparse

    parser = argparse.ArgumentParser(description='Capture screenshots of map visualizations')
    parser.add_argument('--index-only', action='store_true', help='Only screenshot the index page')
    parser.add_argument('--viewers-only', action='store_true', help='Only screenshot viewer configs')
    parser.add_argument('--config', type=str, help='Screenshot a specific config name')
    parser.add_argument('--port', type=int, default=8765, help='Port for local HTTP server')
    parser.add_argument('--show-ui', action='store_true', help='Show UI overlays (info box, JSON display). Default hides them.')
    args = parser.parse_args()

    # Setup paths
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / 'docs'
    screenshots_dir = project_root / 'screenshots'

    # Create screenshots directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True)
    print(f"📁 Screenshots will be saved to: {screenshots_dir}\n")

    # Start local HTTP server to serve docs directory (avoids CORS issues)
    print(f"🌐 Starting local server on port {args.port}...")
    server = start_server(str(docs_dir), args.port)
    base_url = f"http://localhost:{args.port}"
    print(f"   Serving {docs_dir} at {base_url}\n")

    try:
        # Screenshot index page
        if not args.viewers_only:
            print("=" * 50)
            print("📄 INDEX PAGE")
            print("=" * 50)
            screenshot_index(base_url, screenshots_dir)
            print()

        # Screenshot viewer configs
        if not args.index_only:
            print("=" * 50)
            print("🗺️  VIEWER CONFIGURATIONS")
            print("=" * 50)

            if args.config:
                # Single config mode
                configs = [args.config]
            else:
                configs = None  # Auto-discover all

            hide_ui = not args.show_ui
            success, fail = screenshot_viewer_configs(docs_dir, base_url, screenshots_dir, configs, hide_ui=hide_ui)
            print(f"📊 Results: {success} succeeded, {fail} failed")

    finally:
        # Shutdown server
        print("\n🛑 Shutting down server...")
        server.shutdown()

    print("\n🎉 Screenshot capture complete!")
    print(f"📂 Find your screenshots in: {screenshots_dir}")


if __name__ == '__main__':
    main()
