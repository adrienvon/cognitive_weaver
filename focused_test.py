#!/usr/bin/env python3
"""
Focused test for the two specific files mentioned in the task
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cognitive_weaver.keyword_extractor import KeywordExtractor
from cognitive_weaver.ai_inference import AIInferenceEngine
from cognitive_weaver.config import load_config

async def main():
    try:
        print("Loading configuration...")
        config = load_config('config.yaml')
        print(f"Config loaded: {config.ai_model.provider}")
        
        print("Initializing AI engine...")
        ai_engine = AIInferenceEngine(config)
        
        print("Initializing keyword extractor...")
        keyword_extractor = KeywordExtractor(config, ai_engine)
        
        # Focus on the two specific files mentioned in the task
        file1 = Path('tests/精神分析/调节心中对人格有决定性影响的父母关系（治疗）.md')
        file2 = Path('tests/精神分析/防御是人格的边界.md')
        
        print(f"Extracting keywords from {file1.name}")
        keywords1 = keyword_extractor.extract_keywords_from_file(file1)
        print(f"Found {len(keywords1)} keywords in {file1.name}")
        for kd in keywords1:
            print(f"  - '{kd.keyword}' in context: {kd.context}")
        
        print(f"Extracting keywords from {file2.name}")
        keywords2 = keyword_extractor.extract_keywords_from_file(file2)
        print(f"Found {len(keywords2)} keywords in {file2.name}")
        for kd in keywords2:
            print(f"  - '{kd.keyword}' in context: {kd.context}")
        
        # Combine keywords from both files
        all_keywords = keywords1 + keywords2
        print(f"Total keywords from both files: {len(all_keywords)}")
        
        # Test AI similarity detection with just these keywords
        print("Testing AI similarity detection...")
        similar_groups = await keyword_extractor.find_similar_keywords(all_keywords)
        
        print(f"Found {len(similar_groups)} similar keyword groups")
        for base_keyword, group in similar_groups.items():
            print(f"Group '{base_keyword}': {len(group)} occurrences")
            for kd in group:
                print(f"  - File: {kd.file_path.name}, Keyword: '{kd.keyword}'")
        
        print("Focused test completed.")
        
    except Exception as e:
        print(f"Error during focused test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
