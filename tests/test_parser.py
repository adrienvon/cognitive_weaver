#!/usr/bin/env python3
"""
Test script for Cognitive Weaver parser functionality
"""

from pathlib import Path
from cognitive_weaver.parser import LinkParser
from cognitive_weaver.config import load_config

def test_parser():
    """Test the link parser functionality"""
    try:
        # Load configuration
        config = load_config('config.yaml')
        
        # Initialize parser
        parser = LinkParser(config)
        
        # Parse the test file - convert to Path object
        file_path = Path('test_vault/无意识.md')
        links = parser.parse_file(file_path)
        
        print(f"Found {len(links)} links in the file:")
        for i, link in enumerate(links, 1):
            print(f"\nLink {i}:")
            print(f"  Source: {link.source_note}")
            print(f"  Target: {link.target_note}")
            print(f"  Context: {link.context_text}")
            print(f"  Line: {link.line_number}")
            
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_parser()
