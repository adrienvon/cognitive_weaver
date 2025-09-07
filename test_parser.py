from src.cognitive_weaver.parser import LinkParser
from src.cognitive_weaver.config import load_config
from pathlib import Path

config = load_config('config.yaml')
parser = LinkParser(config)

# 测试解析器
file_path = Path('tests/精神分析/人活着的四个驱动.md')
print(f"Testing file: {file_path}")
print(f"File exists: {file_path.exists()}")

if file_path.exists():
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"File content: {repr(content)}")
    
    links = parser.parse_file(file_path, skip_relation_links=False)
    print(f'Found {len(links)} links:')
    for link in links:
        print(f'  - Source: {link.source_note}')
        print(f'    Target: {link.target_note}')
        print(f'    Context: {link.context_text}')
        print(f'    Line: {link.original_line}')
        print()
