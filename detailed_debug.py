#!/usr/bin/env python3
"""
Detailed debug script for keyword processing functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cognitive_weaver.monitor import VaultMonitor
from cognitive_weaver.config import load_config
from cognitive_weaver.keyword_extractor import KeywordExtractor
from cognitive_weaver.ai_inference import AIInferenceEngine

async def main():
    try:
        print("Loading configuration...")
        config = load_config('config.yaml')
        print(f"Config loaded: {config.ai_model.provider}")
        
        print("Initializing AI engine...")
        ai_engine = AIInferenceEngine(config)
        
        print("Initializing keyword extractor...")
        keyword_extractor = KeywordExtractor(config, ai_engine)
        
        folder_path = Path('tests/精神分析')
        print(f"Processing folder: {folder_path}")
        
        # Check if folder exists and list files
        if not folder_path.exists():
            print(f"Error: Folder {folder_path} does not exist.")
            return
        
        md_files = list(folder_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")
        
        # Extract keywords from all files
        all_keywords = []
        for file_path in md_files:
            print(f"Extracting keywords from {file_path.name}")
            keywords = keyword_extractor.extract_keywords_from_file(file_path)
            print(f"Found {len(keywords)} keywords in {file_path.name}")
            all_keywords.extend(keywords)
        
        print(f"Total keywords found: {len(all_keywords)}")
        
        if not all_keywords:
            print("No keywords found. Exiting.")
            return
        
        # Use AI to find similar keywords
        print("Finding similar keywords with AI...")
        similar_keyword_groups = await keyword_extractor.find_similar_keywords(all_keywords)
        
        print(f"Found {len(similar_keyword_groups)} groups of similar keywords")
        
        for base_keyword, group in similar_keyword_groups.items():
            print(f"Group for '{base_keyword}': {len(group)} occurrences")
            for kd in group:
                print(f"  - File: {kd.file_path.name}, Context: {kd.context}")
        
        print("Debug completed.")
        
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
