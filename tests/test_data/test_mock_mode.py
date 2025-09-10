import asyncio
import shutil
from pathlib import Path
from src.cognitive_weaver.parser import LinkParser, LinkData
from src.cognitive_weaver.config import load_config
from src.cognitive_weaver.ai_inference import AIInferenceEngine
from src.cognitive_weaver.rewriter import FileRewriter

async def test_mock_mode():
    print("=== Cognitive Weaver 模拟模式测试 ===\n")
    
    # 创建测试文件
    test_file = Path('test_mock_file.md')
    
    try:
        # 创建测试文件内容
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('这是一个测试文件，包含对[[攻击性]]的引用。\n')
            f.write('另外还提到了[[防御机制]]的概念。\n')
        
        print(f"1. 创建测试文件: {test_file}")
        
        # 加载配置
        config = load_config('config.yaml')
        
        # 初始化组件
        parser = LinkParser(config)
        ai_engine = AIInferenceEngine(config)
        rewriter = FileRewriter(config)
        
        # 强制设置AI客户端为None以使用模拟模式
        ai_engine.client = None
        
        print("2. 初始化所有组件完成（强制使用模拟模式）")
        
        # 解析链接
        print("\n3. 解析文件中的链接...")
        links = parser.parse_file(test_file, skip_relation_links=True)
        print(f"   发现 {len(links)} 个需要处理的链接:")
        
        for i, link in enumerate(links, 1):
            print(f"\n   {i}. 源笔记: {link.source_note}")
            print(f"      目标笔记: {link.target_note}")
            print(f"      上下文: {link.context_text}")
            print(f"      行号: {link.line_number}")
            
            # 跳过关系链接
            if link.target_note in config.relations.predefined_relations:
                print(f"      -> 跳过关系链接: {link.target_note}")
                continue
            
            # AI推理关系（模拟模式）
            print(f"      -> 正在进行AI推理（模拟模式）...")
            try:
                relation = await ai_engine.infer_relation(link)
                print(f"      -> AI推理结果: {relation}")
                
                if relation:
                    # 添加关系到文件
                    print(f"      -> 正在添加关系到文件...")
                    success = await rewriter.add_relation_to_file(test_file, link, relation)
                    if success:
                        print(f"      -> ✓ 成功添加关系链接")
                    else:
                        print(f"      -> ✗ 添加关系链接失败")
                else:
                    print(f"      -> ⚠ AI推理未返回有效关系")
                    
            except Exception as e:
                print(f"      -> ✗ AI推理出错: {e}")
        
        # 显示最终结果
        print("\n4. 处理完成，查看最终文件内容:")
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("   " + "="*60)
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip():
                print(f"   {i}: {line}")
        print("   " + "="*60)
        
        # 验证备份文件
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        if backup_file.exists():
            print(f"\n5. ✓ 备份文件已创建: {backup_file}")
            # 显示备份文件内容
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            print("   备份文件内容:")
            for i, line in enumerate(backup_content.split('\n'), 1):
                if line.strip():
                    print(f"   {i}: {line}")
        else:
            print(f"\n5. ⚠ 未找到备份文件")
        
        print("\n=== 模拟模式测试完成 ===")
        print("✓ 完整的处理流程测试成功（模拟模式）")
        
    except Exception as e:
        print(f"✗ 模拟模式测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
            print(f"\n清理: 删除测试文件 {test_file}")
        
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        if backup_file.exists():
            backup_file.unlink()
            print(f"清理: 删除备份文件 {backup_file}")

if __name__ == "__main__":
    asyncio.run(test_mock_mode())
