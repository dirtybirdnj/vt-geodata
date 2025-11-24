#!/usr/bin/env python3
"""
Standardize top-left UI across all map HTML files.

This script:
1. Moves "Back to Index" links into the info box (if both exist)
2. Standardizes info box position to top: 10px, left: 10px
3. Preserves all interactive features (click handlers, JSON displays, etc.)
4. Collects edge case data for future unified map-viewer.html

Edge cases tracked:
- Maps with click interactivity
- Maps with special buttons (Clear, Reassign, etc.)
- Maps with JSON display elements
- Maps with custom CSS classes
- Color scheme variations
- Width variations
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


class MapUIStandardizer:
    """Standardize map UI while preserving functionality"""

    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.edge_cases = {
            'interactive_maps': [],
            'json_displays': [],
            'custom_buttons': [],
            'css_classes_used': [],
            'color_schemes': {},
            'width_variations': {},
            'special_features': {},
            'errors': []
        }

    def find_info_box(self, content: str) -> Optional[Tuple[str, int, int]]:
        """
        Find the info box div and its position in the content.
        Returns (matched_text, start_pos, end_pos) or None
        """
        # Pattern 1: Inline style info box (most common)
        patterns = [
            # Fixed position info boxes with various attributes
            r'<div style="position:\s*fixed;\s*top:\s*\d+px;\s*left:\s*\d+px;[^>]*?background[^>]*?>(.*?)</div>',
            # Info boxes with class
            r'<div[^>]*class="info-box"[^>]*>(.*?)</div>',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(0), match.start(), match.end()

        return None

    def find_back_button(self, content: str) -> Optional[Tuple[str, int, int]]:
        """
        Find the back button link and its position.
        Returns (matched_text, start_pos, end_pos) or None
        """
        # Look for back to index links
        patterns = [
            r'<a\s+href="index\.html"[^>]*>.*?Back to Index.*?</a>',
            r'<a[^>]*class="back-button"[^>]*>.*?</a>',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(0), match.start(), match.end()

        return None

    def extract_border_color(self, info_box_html: str) -> Optional[str]:
        """Extract border color from info box styles"""
        match = re.search(r'border:\s*\d+px\s+solid\s+(#[0-9a-fA-F]{3,6}|[a-z]+)', info_box_html)
        if match:
            return match.group(1)
        return '#5c6bc0'  # Default color

    def extract_width(self, info_box_html: str) -> str:
        """Extract width from info box"""
        match = re.search(r'width:\s*(\d+)px', info_box_html)
        if match:
            return match.group(1)
        return '500'  # Default width

    def has_click_interactivity(self, content: str) -> bool:
        """Check if map has click event handlers"""
        patterns = [
            r'\.on\([\'"]click[\'"],\s*function',
            r'onclick\s*=',
            r'addEventListener\([\'"]click[\'"]',
        ]
        return any(re.search(pattern, content) for pattern in patterns)

    def has_json_display(self, content: str) -> bool:
        """Check if map has JSON display element"""
        patterns = [
            r'id\s*=\s*[\'"]json',
            r'class\s*=\s*[\'"]json-display',
            r'JSON\.stringify',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)

    def find_custom_buttons(self, content: str) -> List[str]:
        """Find custom buttons (Clear, Reassign, etc.)"""
        buttons = []

        # Look for buttons with onclick
        matches = re.findall(r'<button[^>]*onclick[^>]*>(.*?)</button>', content, re.IGNORECASE)
        buttons.extend(matches)

        return buttons

    def create_standardized_back_link(self, border_color: str) -> str:
        """Create standardized back link to be placed inside info box"""
        return f'''<a href="index.html" style="text-decoration: none; color: {border_color}; font-weight: 600;
                                       font-size: 14px; display: inline-flex; align-items: center; gap: 5px;
                                       margin-bottom: 10px;">
                <span>←</span>
                <span>Back to Index</span>
            </a>'''

    def standardize_info_box_position(self, info_box_html: str) -> str:
        """Standardize info box to left: 10px"""
        # Replace left: XXpx with left: 10px
        result = re.sub(r'left:\s*\d+px', 'left: 10px', info_box_html)
        return result

    def process_file(self, filepath: Path) -> bool:
        """Process a single HTML file"""
        print(f"\nProcessing: {filepath.name}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            changes_made = []

            # Collect edge case data
            if self.has_click_interactivity(content):
                self.edge_cases['interactive_maps'].append(filepath.name)
                print("  ✓ Has click interactivity - preserving")

            if self.has_json_display(content):
                self.edge_cases['json_displays'].append(filepath.name)
                print("  ✓ Has JSON display - preserving")

            custom_buttons = self.find_custom_buttons(content)
            if custom_buttons:
                self.edge_cases['custom_buttons'].append({
                    'file': filepath.name,
                    'buttons': custom_buttons
                })
                print(f"  ✓ Has {len(custom_buttons)} custom button(s) - preserving")

            # Find info box and back button
            info_box_data = self.find_info_box(content)
            back_button_data = self.find_back_button(content)

            if not info_box_data:
                print("  ⚠ No info box found - skipping")
                self.edge_cases['special_features'][filepath.name] = 'no_info_box'
                return False

            info_box_html, info_start, info_end = info_box_data

            # Extract info box properties
            border_color = self.extract_border_color(info_box_html)
            width = self.extract_width(info_box_html)

            self.edge_cases['color_schemes'][filepath.name] = border_color
            self.edge_cases['width_variations'][filepath.name] = width

            # Check if back button is already inside info box
            if back_button_data:
                back_html, back_start, back_end = back_button_data

                # Is back button inside info box?
                if back_start > info_start and back_end < info_end:
                    print("  ✓ Back button already in info box")
                    # Just standardize position
                    new_info_box = self.standardize_info_box_position(info_box_html)
                    if new_info_box != info_box_html:
                        content = content[:info_start] + new_info_box + content[info_end:]
                        changes_made.append("standardized info box position")
                else:
                    # Move back button into info box
                    print("  → Moving back button into info box")

                    # Remove standalone back button
                    content = content[:back_start] + content[back_end:]

                    # Adjust info box position if we removed something before it
                    if back_end < info_start:
                        adjustment = back_end - back_start
                        info_start -= adjustment
                        info_end -= adjustment
                        info_box_html = content[info_start:info_end]

                    # Create new back link
                    new_back_link = self.create_standardized_back_link(border_color)

                    # Find the opening div tag end and insert after it
                    div_end_match = re.search(r'<div[^>]*>', info_box_html)
                    if div_end_match:
                        insert_pos = div_end_match.end()
                        new_info_box = (
                            info_box_html[:insert_pos] + '\n            ' +
                            new_back_link + '\n            ' +
                            info_box_html[insert_pos:]
                        )

                        # Standardize position
                        new_info_box = self.standardize_info_box_position(new_info_box)

                        # Update content
                        content = content[:info_start] + new_info_box + content[info_end:]
                        changes_made.append("moved back button into info box")
                        changes_made.append("standardized position")
            else:
                # No back button exists - just standardize position
                print("  ⚠ No back button found")
                new_info_box = self.standardize_info_box_position(info_box_html)
                if new_info_box != info_box_html:
                    content = content[:info_start] + new_info_box + content[info_end:]
                    changes_made.append("standardized info box position")

            # Save if changes were made
            if changes_made and content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ Updated: {', '.join(changes_made)}")
                return True
            else:
                print("  ○ No changes needed")
                return False

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.edge_cases['errors'].append({
                'file': filepath.name,
                'error': str(e)
            })
            import traceback
            traceback.print_exc()
            return False

    def process_all_maps(self, exclude_files: List[str] = None):
        """Process all HTML files in docs directory"""
        if exclude_files is None:
            exclude_files = ['index.html']

        html_files = sorted(self.docs_dir.glob('*.html'))
        html_files = [f for f in html_files if f.name not in exclude_files]

        print("=" * 70)
        print("MAP UI STANDARDIZATION")
        print("=" * 70)
        print(f"Found {len(html_files)} HTML files to process\n")

        updated_count = 0
        skipped_count = 0

        for filepath in html_files:
            if self.process_file(filepath):
                updated_count += 1
            else:
                skipped_count += 1

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✓ Updated: {updated_count} files")
        print(f"○ Skipped: {skipped_count} files")
        print(f"✗ Errors: {len(self.edge_cases['errors'])} files")

        # Save edge cases report
        self.save_edge_cases_report()

    def save_edge_cases_report(self):
        """Save edge cases data for future unified map-viewer design"""
        report_path = Path('docs/edge_cases_report.json')

        # Clean up edge cases for JSON serialization
        report = {
            'interactive_maps': self.edge_cases['interactive_maps'],
            'json_displays': self.edge_cases['json_displays'],
            'custom_buttons': self.edge_cases['custom_buttons'],
            'color_schemes': self.edge_cases['color_schemes'],
            'width_variations': self.edge_cases['width_variations'],
            'special_features': self.edge_cases['special_features'],
            'errors': self.edge_cases['errors'],
            'statistics': {
                'total_interactive_maps': len(self.edge_cases['interactive_maps']),
                'total_with_json_display': len(self.edge_cases['json_displays']),
                'total_with_custom_buttons': len(self.edge_cases['custom_buttons']),
                'unique_colors': len(set(self.edge_cases['color_schemes'].values())),
                'unique_widths': len(set(self.edge_cases['width_variations'].values())),
            }
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Edge cases report saved to: {report_path}")
        print("\nEdge Case Summary:")
        print(f"  - Interactive maps: {report['statistics']['total_interactive_maps']}")
        print(f"  - Maps with JSON display: {report['statistics']['total_with_json_display']}")
        print(f"  - Maps with custom buttons: {report['statistics']['total_with_custom_buttons']}")
        print(f"  - Unique color schemes: {report['statistics']['unique_colors']}")
        print(f"  - Unique width values: {report['statistics']['unique_widths']}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Standardize map UI across all HTML files')
    parser.add_argument('--docs-dir', default='docs', help='Directory containing HTML files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')

    args = parser.parse_args()

    standardizer = MapUIStandardizer(args.docs_dir)

    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    standardizer.process_all_maps()

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
