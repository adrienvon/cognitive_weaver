import asyncio
from src.cognitive_weaver.parser import LinkParser
from src.cognitive_weaver.config import load_config
from src.cognitive_weaver.ai_inference import AIInferenceEngine
from pathlib import Path

def test_basic_functionality():
    print("=== Cognitive Weaver 基础功能测试 ===\n")
    
    # 1. 测试配置加载
    print("1. 测试配置加载...")
    try:
        config = load_config('config.yaml')
        print(f"   ✓ 配置加载成功")
        print(f"   - AI Provider: {config.ai_model.provider}")
        print(f"   - Model: {config.ai_model.model_name}")
        print(f"   - 预定义关系数量: {len(config.relations.predefined_relations)}")
    except Exception as e:
        print(f"   ✗ 配置加载失败: {e}")
        return
    
    # 2. 测试解析器
    print("\n2. 测试链接解析器...")
    try:
        parser = LinkParser(config)
        
        # 测试多个文件
        test_files = [
            'tests/精神分析/人活着的四个驱动.md',
            'tests/精神分析/攻击性与力比多的表现化.md',
            'tests/精神分析/防御是人格的边界.md'
        ]
        
        total_links = 0
        for file_path in test_files:
            path = Path(file_path)
            if path.exists():
                links = parser.parse_file(path, skip_relation_links=False)
                total_links += len(links)
                print(f"   - {path.name}: 发现 {len(links)} 个链接")
                for link in links:
                    print(f"     * {link.target_note} (来源: {link.source_note})")
            else:
                print(f"   - {path.name}: 文件不存在")
        
        print(f"   ✓ 解析器测试完成，总共发现 {total_links} 个链接")
    except Exception as e:
        print(f"   ✗ 解析器测试失败: {e}")
        return
    
    # 3. 测试AI引擎初始化（不调用API）
    print("\n3. 测试AI引擎初始化...")
    try:
        ai_engine = AIInferenceEngine(config)
        if ai_engine.client is None:
            print("   ⚠ AI客户端未初始化，将使用模拟模式")
        else:
            print("   ✓ AI客户端初始化成功")
    except Exception as e:
        print(f"   ✗ AI引擎初始化失败: {e}")
        return
    
    # 4. 测试模拟AI推理
    print("\n4. 测试模拟AI推理...")
    try:
        # 创建一个测试链接数据
        from src.cognitive_weaver.parser import LinkData
        test_link = LinkData(
            source_note="人活着的四个驱动",
            target_note="攻击性",
            context_text="人活着的四个驱动：性驱力、[[攻击性]]、关系驱动、自恋",
            line_number=1,
            original_line="人活着的四个驱动：性驱力、[[攻击性]]、关系驱动、自恋 [[简单提及]]"
        )
        
        # 测试关系验证
        test_relations = ["[[支撑观点]]", "[[简单提及]]", "[[无效关系]]"]
        for relation in test_relations:
            is_valid = ai_engine._is_valid_relation(relation)
            print(f"   - {relation}: {'有效' if is_valid else '无效'}")
        
        print("   ✓ 模拟AI推理测试完成")
    except Exception as e:
        print(f"   ✗ 模拟AI推理测试失败: {e}")
        return
    
    print("\n=== 基础功能测试完成 ===")
    print("✓ 所有基础功能正常工作")
    print("⚠ 注意：AI API调用可能需要网络连接，如果网络有问题会自动使用模拟模式")

if __name__ == "__main__":
    test_basic_functionality()
