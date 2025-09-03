#!/usr/bin/env python3
"""
Test script to verify AI similarity detection for the '人格' keyword
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cognitive_weaver.keyword_extractor import KeywordExtractor, KeywordData
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
        
        # Create KeywordData objects for the '人格' keyword from both files
        kd1 = KeywordData(
            keyword='人格',
            context='调节心中对人格有决定性影响的父母关系 重构',
            file_path=Path('tests/精神分析/调节心中对人格有决定性影响的父母关系（治疗）.md'),
            line_number=1,
            original_line='调节心中对人格有决定性影响的父母关系 重构'
        )
        
        kd2 = KeywordData(
            keyword='人格', 
            context='防御是人格的边界',
            file_path=Path('tests/精神分析/防御是人格的边界.md'),
            line_number=1,
            original_line='防御是人格的边界'
        )
        
        keywords = [kd1, kd2]
        print(f"Testing AI similarity with keywords: {[kd.keyword for kd in keywords]}")
        
        # Test AI similarity detection
        similar_groups = await keyword_extractor.find_similar_keywords(keywords)
        
        print(f"Found {len(similar_groups)} similar keyword groups")
        for base_keyword, group in similar_groups.items():
            print(f"Group '{base_keyword}': {len(group)} occurrences")
            for kd in group:
                print(f"  - File: {kd.file_path.name}, Keyword: '{kd.keyword}'")
        
        # If similar, test the rewriter functionality
        if similar_groups:
            print("\nTesting link creation...")
            # For simplicity, just check if the keyword would be wrapped
            for base_keyword, group in similar_groups.items():
                if base_keyword == '人格':
                    print(f"Keyword '人格' would be wrapped as [[人格]] in both files")
                    break
        
        print("AI similarity test completed.")
        
    except Exception as e:
        print(f"Error during AI similarity test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
