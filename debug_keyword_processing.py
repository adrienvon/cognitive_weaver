#!/usr/bin/env python3
"""
Debug script for keyword processing functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cognitive_weaver.monitor import VaultMonitor
from cognitive_weaver.config import load_config

async def main():
    try:
        print("Loading configuration...")
        config = load_config('config.yaml')
        print(f"Config loaded: {config.ai_model.provider}")
        
        print("Initializing monitor...")
        monitor = VaultMonitor(Path('tests/精神分析'), config)
        
        print("Processing keywords for folder: tests/精神分析")
        folder_path = Path('tests/精神分析')
        
        # Check if folder exists and list files
        if not folder_path.exists():
            print(f"Error: Folder {folder_path} does not exist.")
            return
        
        md_files = list(folder_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files: {[f.name for f in md_files]}")
        
        # Process keywords
        await monitor.process_keywords_for_folder(folder_path)
        
        print("Keyword processing completed!")
        
    except Exception as e:
        print(f"Error during keyword processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
