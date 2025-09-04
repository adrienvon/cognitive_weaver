"""
Cognitive Weaver 的链接解析模块
从 Markdown 文件中提取 Obsidian 链接及其上下文

Link parsing module for Cognitive Weaver
Extracts Obsidian links and their context from markdown files
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class LinkData:
    """提取链接及其上下文的数据结构
    
    Attributes:
        source_note (str): 发现链接的源笔记名称
        target_note (str): 被链接到的目标笔记名称
        context_text (str): 链接周围的文本上下文
        line_number (int): 链接在源文件中出现的行号
        original_line (str): 包含链接的完整行
        relation_link (str): AI推断的关系类型（例如，"简单提及"，"支撑观点"）
    """
    source_note: str
    target_note: str
    context_text: str
    line_number: int
    original_line: str
    relation_link: str = None  # 用于存储 AI 推理结果

class LinkParser:
    """解析 Markdown 文件中的 Obsidian 链接并提取上下文
    
    Parses Obsidian links from markdown files and extracts context
    """
    
    def __init__(self, config):
        """
        使用配置初始化链接解析器。
        
        Initialize the link parser with configuration.
        
        Args:
            config: 包含解析设置的配置对象
            config: Configuration object containing parsing settings
        """
        self.config = config
        # 用于查找 Obsidian wiki 链接的正则表达式：[[target_note]] 或 [[target_note|display_text]]
        self.link_pattern = re.compile(r'\[\[(.*?)\]\]')
        # 用于检查行是否已包含关系链接以避免重复处理的正则表达式
        self.relation_pattern = re.compile(r'\[\[(支撑观点|反驳观点|举例说明|定义概念|属于分类|包含部分|引出主题|简单提及)\]\]')
    
    def parse_file(self, file_path: Path, skip_relation_links: bool = True) -> List[LinkData]:
        """
        解析 Markdown 文件并提取所有带有上下文的 Obsidian 链接。
        
        Parse a markdown file and extract all Obsidian links with context.
        
        Args:
            file_path (Path): 要解析的 Markdown 文件路径
            skip_relation_links (bool): 如果为 True，跳过已包含关系链接的行以避免无限处理。
                                       如果为 False，包含所有行。
        
        Returns:
            List[LinkData]: 包含链接信息和上下文的 LinkData 对象列表
        """
        if not file_path.exists():
            return []
        
        links = []
        source_note = file_path.stem  # 获取不带扩展名的笔记名称
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # 如果指定，跳过已包含关系链接的行
                if skip_relation_links and self.relation_pattern.search(line):
                    continue
                
                # 查找此行中的所有链接
                link_matches = self.link_pattern.finditer(line)
                for match in link_matches:
                    full_link = match.group(1)
                    # 处理带有显示文本的链接：[[target|display]]
                    if '|' in full_link:
                        target_note = full_link.split('|')[0].strip()
                    else:
                        target_note = full_link.strip()
                    
                    # 跳过空或格式错误的链接
                    if not target_note:
                        continue
                    
                    # 提取链接周围的上下文
                    context_text = self.extract_context(lines, line_num, match.start(), match.end())
                    
                    link_data = LinkData(
                        source_note=source_note,
                        target_note=target_note,
                        context_text=context_text,
                        line_number=line_num,
                        original_line=line.strip()
                    )
                    links.append(link_data)
        
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
        
        return links
    
    def extract_context(self, lines: List[str], line_num: int, start_pos: int, end_pos: int) -> str:
        """
        提取文本中链接周围的上下文。
        
        Extract context around a link within the text.
        
        Args:
            lines (List[str]): 文件中所有行的列表
            line_num (int): 发现链接的行号（基于1的索引）
            start_pos (int): 链接在行内的起始位置
            end_pos (int): 链接在行内的结束位置
            
        Returns:
            str: 包含链接和周围上下文文本的字符串
        """
        context_window = self.config.file_monitoring.context_window_size
        current_line = lines[line_num - 1]
        
        # 从当前行提取上下文
        line_start = max(0, start_pos - context_window // 2)
        line_end = min(len(current_line), end_pos + context_window // 2)
        context = current_line[line_start:line_end]
        
        # 如果可用，添加上一行
        if line_num > 1:
            prev_line = lines[line_num - 2]
            prev_context = prev_line[-context_window // 4:] if len(prev_line) > context_window // 4 else prev_line
            context = prev_context + " " + context
        
        # 如果可用，添加下一行
        if line_num < len(lines):
            next_line = lines[line_num]
            next_context = next_line[:context_window // 4] if len(next_line) > context_window // 4 else next_line
            context = context + " " + next_context
        
        # 清理上下文文本
        context = re.sub(r'\s+', ' ', context).strip()
        return context
    
    def has_relation_links(self, line: str) -> bool:
        """检查行是否已包含关系链接
        Check if a line already contains relation links
        """
        return bool(self.relation_pattern.search(line))
