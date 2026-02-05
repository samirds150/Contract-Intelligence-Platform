#!/usr/bin/env python
"""Convert FUNCTIONS_REFERENCE.md to HTML"""
from pathlib import Path
import sys

# Add docs directory to path to use md_to_html module
sys.path.insert(0, str(Path(__file__).parent))
from md_to_html import md_to_html

if __name__ == '__main__':
    script_dir = Path(__file__).parent
    md_file = script_dir / 'FUNCTIONS_REFERENCE.md'
    html_file = script_dir / 'FUNCTIONS_REFERENCE.html'
    
    md_to_html(str(md_file), str(html_file))
