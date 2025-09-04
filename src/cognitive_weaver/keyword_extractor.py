"""
Keyword extraction module for Cognitive Weaver
Handles extraction of potential keywords from markdown files
and AI-based similarity detection for linking

关键词提取模块 - 处理从Markdown文件中提取潜在关键词和基于AI的相似性检测以进行链接
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from .ai_inference import AIInferenceEngine

@dataclass
class KeywordData:
    """Data structure for extracted keywords with context"""
    keyword: str
    file_path: Path
    context: str
    line_number: int
    original_line: str

class KeywordExtractor:
    """Extracts potential keywords from markdown files and handles AI-based linking"""
    
    def __init__(self, config, ai_engine: AIInferenceEngine):
        self.config = config
        self.ai_engine = ai_engine
        # Common words to exclude from keyword extraction
        self.stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "都", "而", "及", "与", "等", 
                          "这", "那", "你", "他", "她", "它", "我们", "他们", "你们", "这个", "那个", "这些", "那些"}
        # Minimum length for keywords
        self.min_keyword_length = 2
    
    def extract_keywords_from_file(self, file_path: Path) -> List[KeywordData]:
        """
        Extract potential keywords from a markdown file.
        
        Args:
            file_path (Path): The path to the markdown file to extract keywords from.
        
        Returns:
            List[KeywordData]: A list of KeywordData objects containing extracted keywords with context.
        """
        if not file_path.exists():
            return []
        
        keywords = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip lines that already have Obsidian links to avoid processing them as keywords
                if re.search(r'\[\[.*?\]\]', line):
                    continue
                
                # Extract potential keywords from the line
                line_keywords = self._extract_keywords_from_text(line.strip())
                
                for keyword in line_keywords:
                    # Get context around the keyword
                    context = self._extract_keyword_context(lines, line_num, line, keyword)
                    
                    keyword_data = KeywordData(
                        keyword=keyword,
                        file_path=file_path,
                        context=context,
                        line_number=line_num,
                        original_line=line.strip()
                    )
                    keywords.append(keyword_data)
        
        except Exception as e:
            print(f"Error extracting keywords from file {file_path}: {e}")
        
        return keywords
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extract potential keywords from text using improved heuristics for Chinese.
        Focuses on meaningful words and reduces noise from fragments.
        
        Args:
            text (str): The text to extract keywords from.
        
        Returns:
            List[str]: A list of extracted keywords.
        """
        # Remove punctuation and split into words
        words = re.findall(r'[\u4e00-\u9fff\w]+', text)
        
        # Improved Chinese keyword extraction:
        # 1. Prefer complete words (2-4 characters) that are likely meaningful
        # 2. Avoid excessive fragmentation by using a smarter approach
        keywords = []
        for word in words:
            # For Chinese text, extract meaningful segments
            if all('\u4e00' <= char <= '\u9fff' for char in word):
                # Chinese word - use intelligent segmentation
                if len(word) <= 4:
                    # Short Chinese words are likely meaningful
                    keywords.append(word)
                else:
                    # For longer Chinese phrases, extract likely compounds
                    # Use a sliding window but with better filtering
                    segments = set()
                    # Prefer 2-3 character segments that are common
                    for i in range(len(word) - 1):
                        for length in [2, 3]:  # Focus on 2-3 character words
                            if i + length <= len(word):
                                segment = word[i:i+length]
                                # Only add segments that don't start/end with stop characters
                                if (segment not in self.stop_words and
                                    not any(seg in self.stop_words for seg in [segment[0], segment[-1]])):
                                    segments.add(segment)
                    keywords.extend(list(segments))
            else:
                # Non-Chinese words (English, etc.)
                if len(word) >= self.min_keyword_length and word not in self.stop_words:
                    keywords.append(word)
        
        # Additional filtering
        filtered_keywords = []
        for word in keywords:
            if (len(word) >= self.min_keyword_length and 
                word not in self.stop_words and
                not word.isdigit() and
                not any(sw in word for sw in self.stop_words) and  # Avoid words containing stop words
                word not in filtered_keywords):  # Avoid duplicates
                filtered_keywords.append(word)
        
        return filtered_keywords
    
    def _extract_keyword_context(self, lines: List[str], line_num: int, line: str, keyword: str) -> str:
        """
        Extract context around a keyword within the text.
        
        Args:
            lines (List[str]): All lines from the file.
            line_num (int): The line number where the keyword appears.
            line (str): The specific line containing the keyword.
            keyword (str): The keyword to extract context for.
        
        Returns:
            str: The context text around the keyword.
        """
        context_window = self.config.file_monitoring.context_window_size
        
        # Find the position of the keyword in the line
        keyword_pos = line.find(keyword)
        if keyword_pos == -1:
            return line.strip()  # Fallback to the whole line
        
        # Extract context from the current line
        line_start = max(0, keyword_pos - context_window // 2)
        line_end = min(len(line), keyword_pos + len(keyword) + context_window // 2)
        context = line[line_start:line_end]
        
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
    
    async def find_similar_keywords(self, keyword_data_list: List[KeywordData]) -> Dict[str, List[KeywordData]]:
        """
        Use AI to find similar keywords that should be linked together.
        
        Args:
            keyword_data_list (List[KeywordData]): List of KeywordData objects to analyze for similarity.
        
        Returns:
            Dict[str, List[KeywordData]]: A dictionary mapping normalized keywords to lists of similar KeywordData objects.
        """
        # Group keywords by their base form for initial clustering
        keyword_groups = {}
        for kd in keyword_data_list:
            # Simple normalization: convert to lowercase for initial grouping
            normalized = kd.keyword.lower()
            if normalized not in keyword_groups:
                keyword_groups[normalized] = []
            keyword_groups[normalized].append(kd)
        
        # Use AI to verify and refine similarity
        final_groups = {}
        for base_keyword, group in keyword_groups.items():
            if len(group) > 1:
                # Only process groups with multiple occurrences
                verified_group = await self._ai_verify_similarity(group)
                if verified_group:
                    final_groups[base_keyword] = verified_group
        
        return final_groups
    
    async def _ai_verify_similarity(self, keyword_group: List[KeywordData]) -> List[KeywordData]:
        """
        Use AI to verify if keywords in a group refer to the same concept
        with improved semantic understanding for psychology concepts.
        
        Args:
            keyword_group (List[KeywordData]): A group of KeywordData objects to verify for similarity.
        
        Returns:
            List[KeywordData]: The verified group of similar keywords, or an empty list if not similar.
        """
        if len(keyword_group) < 2:
            return keyword_group
        
        # Prepare detailed context for AI analysis
        contexts = []
        for kd in keyword_group:
            contexts.append(f"关键词: '{kd.keyword}', 上下文: '{kd.context}', 文件: {kd.file_path.name}")
        
        prompt = f"""
        你是一位心理学知识图谱专家，擅长识别中文心理学概念之间的语义相似性。

        请分析以下关键词是否指向同一个心理学概念或实体。考虑：
        1. 语义相似性（同义词、近义词、相关概念）
        2. 上下文中的使用方式
        3. 心理学领域的专业含义

        关键词组分析：
        {chr(10).join(contexts)}

        如果这些关键词确实指向同一个心理学概念，回复"是"，否则回复"否"。

        注意：即使关键词的字面形式不同，如果它们在心理学语境中表示相同的核心概念，也应该被认为是相同的。
        """
        
        try:
            response = await self.ai_engine._call_ai_model(prompt)
            # More robust checking for affirmative responses
            affirmative_responses = {"是", "是的", "相同", "一样", "同一个概念", "相同概念"}
            response_lower = response.strip().lower()
            
            if any(affirmative in response_lower for affirmative in affirmative_responses):
                return keyword_group
            else:
                return []
        except Exception as e:
            print(f"AI similarity verification error: {e}")
            return []  # Don't assume similarity on AI failure
