#!/usr/bin/env python3
"""
Test script for the complete Cognitive Weaver pipeline
Tests: Link parsing -> AI inference -> File rewriting
"""

import asyncio
from pathlib import Path
from cognitive_weaver.config import load_config
from cognitive_weaver.parser import LinkParser
from cognitive_weaver.ai_inference import AIInferenceEngine
from cognitive_weaver.rewriter import FileRewriter

async def test_pipeline():
    """Test the complete pipeline on a test file"""
    print("=== Cognitive Weaver Pipeline Test ===\n")
    
    # Load configuration
    config = load_config("config.yaml")
    
    # Test file path
    test_file = Path("test_vault/无意识.md")
    
    if not test_file.exists():
        print(f"Error: Test file {test_file} does not exist.")
        return
    
    print(f"Testing on file: {test_file}")
    print(f"File content before processing:")
    print("-" * 50)
    with open(test_file, 'r', encoding='utf-8') as f:
        print(f.read())
    print("-" * 50)
    print()
    
    # Step 1: Parse links from the file
    print("1. Parsing links...")
    parser = LinkParser(config)
    links = parser.parse_file(test_file)
    
    if not links:
        print("No links found in the file.")
        return
    
    print(f"Found {len(links)} links:")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link.source_note} -> {link.target_note}")
        print(f"     Context: {link.context_text[:50]}...")
        print(f"     Line: {link.line_number}")
    print()
    
    # Step 2: AI Inference for each link
    print("2. AI Inference for relationship extraction...")
    ai_engine = AIInferenceEngine(config)
    
    for i, link in enumerate(links, 1):
        print(f"  Processing link {i}: {link.source_note} -> {link.target_note}")
        
        # Call AI to infer relationship
        relation_link = await ai_engine.infer_relation(link)
        
        if relation_link:
            print(f"     AI Result: {relation_link}")
            link.relation_link = relation_link  # Store the result
        else:
            print(f"     AI inference failed for this link.")
            link.relation_link = None
    
    print()
    
    # Step 3: File rewriting with relation links
    print("3. File rewriting with relation links...")
    rewriter = FileRewriter(config)
    
    successful_updates = 0
    for i, link in enumerate(links, 1):
        if link.relation_link:
            print(f"  Adding {link.relation_link} to line {link.line_number}...")
            success = await rewriter.add_relation_to_file(test_file, link, link.relation_link)
            if success:
                successful_updates += 1
                print(f"     ✓ Successfully added relation link")
            else:
                print(f"     ✗ Failed to add relation link")
        else:
            print(f"  Skipping link {i} (no relation link available)")
    
    print(f"\nSuccessfully updated {successful_updates} out of {len(links)} links.")
    
    # Show final file content
    print(f"\nFile content after processing:")
    print("-" * 50)
    with open(test_file, 'r', encoding='utf-8') as f:
        print(f.read())
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
