"""
Link parsing module for Cognitive Weaver
Extracts Obsidian links and their context from markdown files
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class LinkData:
    """Data structure for extracted links with context
    
    Attributes:
        source_note (str): Name of the source note where the link is found
        target_note (str): Name of the target note being linked to
        context_text (str): Text context surrounding the link
        line_number (int): Line number where the link appears in the source file
        original_line (str): The complete line containing the link
        relation_link (str): Relation type inferred by AI (e.g., "简单提及", "支撑观点")
    """
    source_note: str
    target_note: str
    context_text: str
    line_number: int
    original_line: str
    relation_link: str = None  # Added for storing AI inference results

class LinkParser:
    """Parses Obsidian links from markdown files and extracts context"""
    
    def __init__(self, config):
        """
        Initialize the link parser with configuration.
        
        Args:
            config: Configuration object containing parsing settings
        """
        self.config = config
        # Regex to find Obsidian wiki links: [[target_note]] or [[target_note|display_text]]
        self.link_pattern = re.compile(r'\[\[(.*?)\]\]')
        # Regex to check if a line already has a relation link to avoid reprocessing
        self.relation_pattern = re.compile(r'\[\[(支撑观点|反驳观点|举例说明|定义概念|属于分类|包含部分|引出主题|简单提及)\]\]')
    
    def parse_file(self, file_path: Path, skip_relation_links: bool = True) -> List[LinkData]:
        """
        Parse a markdown file and extract all Obsidian links with context.
        
        Args:
            file_path (Path): Path to the markdown file to parse
            skip_relation_links (bool): If True, skip lines that already have relation links
                                       to avoid infinite processing. If False, include all lines.
        
        Returns:
            List[LinkData]: A list of LinkData objects containing link information and context
        """
        if not file_path.exists():
            return []
        
        links = []
        source_note = file_path.stem  # Get the note name without extension
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip lines that already have relation links if specified
                if skip_relation_links and self.relation_pattern.search(line):
                    continue
                
                # Find all links in this line
                link_matches = self.link_pattern.finditer(line)
                for match in link_matches:
                    full_link = match.group(1)
                    # Handle links with display text: [[target|display]]
                    if '|' in full_link:
                        target_note = full_link.split('|')[0].strip()
                    else:
                        target_note = full_link.strip()
                    
                    # Skip empty or malformed links
                    if not target_note:
                        continue
                    
                    # Extract context around the link
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
        Extract context around a link within the text.
        
        Args:
            lines (List[str]): List of all lines from the file
            line_num (int): Line number where the link is found (1-based index)
            start_pos (int): Starting position of the link within the line
            end_pos (int): Ending position of the link within the line
            
        Returns:
            str: A string containing the link and surrounding context text
        """
        context_window = self.config.file_monitoring.context_window_size
        current_line = lines[line_num - 1]
        
        # Extract context from the current line
        line_start = max(0, start_pos - context_window // 2)
        line_end = min(len(current_line), end_pos + context_window // 2)
        context = current_line[line_start:line_end]
        
        # Add previous line if available
        if line_num > 1:
            prev_line = lines[line_num - 2]
            prev_context = prev_line[-context_window // 4:] if len(prev_line) > context_window // 4 else prev_line
            context = prev_context + " " + context
        
        # Add next line if available
        if line_num < len(lines):
            next_line = lines[line_num]
            next_context = next_line[:context_window // 4] if len(next_line) > context_window // 4 else next_line
            context = context + " " + next_context
        
        # Clean up the context text
        context = re.sub(r'\s+', ' ', context).strip()
        return context
    
    def has_relation_links(self, line: str) -> bool:
        """Check if a line already contains relation links"""
        return bool(self.relation_pattern.search(line))
