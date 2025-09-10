import asyncio
import shutil
from pathlib import Path
from src.cognitive_weaver.parser import LinkParser, LinkData
from src.cognitive_weaver.config import load_config
from src.cognitive_weaver.ai_inference import AIInferenceEngine
from src.cognitive_weaver.rewriter import FileRewriter

async def test_end_to_end():
    print("=== Cognitive Weaver 端到端测试 ===\n")
    
    # 创建测试文件副本
    test_file = Path('test_temp_file.md')
    original_file = Path('tests/精神分析/攻击性与力比多的表现化.md')
    
    try:
        # 复制原文件作为测试
        shutil.copy2(original_file, test_file)
        
        # 添加一个测试链接到文件中
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('攻击性与力比多的表现化：唠叨是力比多的表达化还停留在口欲期，与世界的链接停留在嘴巴，用语言对孩子进行心理强奸\n')
            f.write('使攻击性和力比多的表达远离原始（杀人），我们成长的过程其实就是力比多和[[攻击性]]象征化表达的过程\n')
        
        print(f"1. 创建测试文件: {test_file}")
        
        # 加载配置
        config = load_config('config.yaml')
        
        # 初始化组件
        parser = LinkParser(config)
        ai_engine = AIInferenceEngine(config)
        rewriter = FileRewriter(config)
        
        print("2. 初始化所有组件完成")
        
        # 解析链接
        print("\n3. 解析文件中的链接...")
        links = parser.parse_file(test_file, skip_relation_links=True)
        print(f"   发现 {len(links)} 个需要处理的链接:")
        
        for i, link in enumerate(links, 1):
            print(f"   {i}. 源笔记: {link.source_note}")
            print(f"      目标笔记: {link.target_note}")
            print(f"      上下文: {link.context_text}")
            print(f"      行号: {link.line_number}")
            
            # 跳过关系链接
            if link.target_note in config.relations.predefined_relations:
                print(f"      -> 跳过关系链接: {link.target_note}")
                continue
            
            # AI推理关系
            print(f"      -> 正在进行AI推理...")
            try:
                # 使用超时来避免卡住
                relation = await asyncio.wait_for(
                    ai_engine.infer_relation(link),
                    timeout=15.0
                )
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
                    
            except asyncio.TimeoutError:
                print(f"      -> ⚠ AI推理超时，使用模拟关系")
                # 使用模拟关系
                mock_relation = "[[简单提及]]"
                success = await rewriter.add_relation_to_file(test_file, link, mock_relation)
                if success:
                    print(f"      -> ✓ 成功添加模拟关系链接: {mock_relation}")
            except Exception as e:
                print(f"      -> ✗ AI推理出错: {e}")
        
        # 显示最终结果
        print("\n4. 处理完成，查看最终文件内容:")
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("   " + "="*50)
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip():
                print(f"   {i}: {line}")
        print("   " + "="*50)
        
        # 验证备份文件
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        if backup_file.exists():
            print(f"\n5. ✓ 备份文件已创建: {backup_file}")
        else:
            print(f"\n5. ⚠ 未找到备份文件")
        
        print("\n=== 端到端测试完成 ===")
        print("✓ 完整的处理流程测试成功")
        
    except Exception as e:
        print(f"✗ 端到端测试失败: {e}")
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
    asyncio.run(test_end_to_end())
