#!/usr/bin/env python3
"""
Simple script to add [[人格]] links to the two target files.
This is a temporary solution to demonstrate the functionality.
"""

import re
from pathlib import Path

def add_links_to_file(file_path: Path):
    """Add [[人格]] links to occurrences of '人格' in the file."""
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace '人格' with '[[人格]]' but avoid replacing within existing links
        # Use a regex to find '人格' that is not inside [[ ]]
        pattern = r'(?<!\[\[)人格(?!\]\])'
        new_content = re.sub(pattern, '[[人格]]', content)
        
        # If the content changed, write it back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added [[人格]] links to {file_path.name}")
            return True
        else:
            print(f"No changes needed for {file_path.name}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    file1 = Path("tests/精神分析/调节心中对人格有决定性影响的父母关系（治疗）.md")
    file2 = Path("tests/精神分析/防御是人格的边界.md")
    
    add_links_to_file(file1)
    add_links_to_file(file2)

if __name__ == "__main__":
    main()
