#!/usr/bin/env python3
"""
Test script to verify keyword extraction from the two target files.
"""

import sys
sys.path.insert(0, 'src')

from cognitive_weaver.keyword_extractor import KeywordExtractor
from cognitive_weaver.ai_inference import AIInferenceEngine
from cognitive_weaver.config import load_config

def main():
    # Load configuration
    config = load_config('../config.yaml')
    ai_engine = AIInferenceEngine(config)
    extractor = KeywordExtractor(config, ai_engine)
    
    # Test keyword extraction on the first file
    file1 = '../tests/精神分析/调节心中对人格有决定性影响的父母关系（治疗）.md'
    keywords1 = extractor.extract_keywords_from_file(file1)
    print(f'Keywords from first file: {[k.keyword for k in keywords1]}')
    
    # Test keyword extraction on the second file  
    file2 = '../tests/精神分析/防御是人格的边界.md'
    keywords2 = extractor.extract_keywords_from_file(file2)
    print(f'Keywords from second file: {[k.keyword for k in keywords2]}')
    
    # Check if '人格' is extracted
    personality_keywords1 = [k for k in keywords1 if k.keyword == '人格']
    personality_keywords2 = [k for k in keywords2 if k.keyword == '人格']
    print(f'人格 found in first file: {len(personality_keywords1) > 0}')
    print(f'人格 found in second file: {len(personality_keywords2) > 0}')
    
    if personality_keywords1 and personality_keywords2:
        print("人格 keyword found in both files!")
        print(f"First file context: {personality_keywords1[0].context}")
        print(f"Second file context: {personality_keywords2[0].context}")
        # Note: AI similarity detection is async and requires proper async handling
        # For now, we'll just confirm the keywords are extracted

if __name__ == "__main__":
    main()
