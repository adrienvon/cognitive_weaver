import asyncio
from src.cognitive_weaver.parser import LinkParser
from src.cognitive_weaver.config import load_config
from src.cognitive_weaver.ai_inference import AIInferenceEngine
from pathlib import Path

async def test_full_pipeline():
    # 加载配置
    config = load_config('config.yaml')
    print(f"Loaded config with AI provider: {config.ai_model.provider}")
    
    # 初始化组件
    parser = LinkParser(config)
    ai_engine = AIInferenceEngine(config)
    
    # 测试文件
    file_path = Path('tests/精神分析/人活着的四个驱动.md')
    print(f"\nTesting file: {file_path}")
    
    if not file_path.exists():
        print("File does not exist!")
        return
    
    # 解析链接（不跳过关系链接，以便看到所有链接）
    links = parser.parse_file(file_path, skip_relation_links=False)
    print(f"Found {len(links)} links:")
    
    for i, link in enumerate(links, 1):
        print(f"\n--- Link {i} ---")
        print(f"Source: {link.source_note}")
        print(f"Target: {link.target_note}")
        print(f"Context: {link.context_text}")
        print(f"Original line: {link.original_line}")
        
        # 只对内容链接进行AI推理（跳过关系链接）
        if link.target_note not in config.relations.predefined_relations:
            print("Running AI inference...")
            try:
                relation = await ai_engine.infer_relation(link)
                print(f"AI inferred relation: {relation}")
            except Exception as e:
                print(f"AI inference failed: {e}")
        else:
            print(f"Skipping AI inference for relation link: {link.target_note}")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
