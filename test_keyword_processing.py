#!/usr/bin/env python3
"""
Test script for keyword processing functionality
"""
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cognitive_weaver.monitor import VaultMonitor
from cognitive_weaver.config import load_config
from pathlib import Path

async def main():
    try:
        print("Loading configuration...")
        config = load_config('config.yaml')
        
        print("Initializing monitor...")
        monitor = VaultMonitor('tests/精神分析', config)
        
        print("Processing keywords for folder: tests/精神分析")
        folder_path = Path('tests/精神分析')
        await monitor.process_keywords_for_folder(folder_path)
        
        print("Keyword processing completed!")
        
    except Exception as e:
        print(f"Error during keyword processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
