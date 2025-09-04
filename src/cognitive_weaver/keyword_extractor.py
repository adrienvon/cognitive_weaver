"""
Cognitive Weaver 关键词提取模块
处理从Markdown文件中提取潜在关键词和基于AI的相似性检测以进行链接

Keyword extraction module for Cognitive Weaver
Handles extraction of potential keywords from markdown files
and AI-based similarity detection for linking
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from .ai_inference import AIInferenceEngine

@dataclass
class KeywordData:
    """包含上下文的提取关键词的数据结构
    Data structure for extracted keywords with context
    """
    keyword: str
    file_path: Path
    context: str
    line_number: int
    original_line: str

class KeywordExtractor:
    """从Markdown文件中提取潜在关键词并处理基于AI的链接
    Extracts potential keywords from Markdown files and handles AI-based linking
    """
    
    def __init__(self, config, ai_engine: AIInferenceEngine):
        self.config = config
        self.ai_engine = ai_engine
        # 关键词提取中要排除的常见词
        self.stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "都", "而", "及", "与", "等", 
                          "这", "那", "你", "他", "她", "它", "我们", "他们", "你们", "这个", "那个", "这些", "那些"}
        # 关键词的最小长度
        self.min_keyword_length = 2
    
    def extract_keywords_from_file(self, file_path: Path) -> List[KeywordData]:
        """
        从Markdown文件中提取潜在关键词。
        
        参数:
            file_path (Path): 要提取关键词的Markdown文件的路径。
        
        返回:
            List[KeywordData]: 包含带上下文的提取关键词的KeywordData对象列表。
        """
        if not file_path.exists():
            return []
        
        keywords = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # 跳过已包含Obsidian链接的行，避免将其作为关键词处理
                if re.search(r'\[\[.*?\]\]', line):
                    continue
                
                # 从行中提取潜在关键词
                line_keywords = self._extract_keywords_from_text(line.strip())
                
                for keyword in line_keywords:
                    # 获取关键词周围的上下文
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
        使用改进的中文启发式方法从文本中提取潜在关键词。
        专注于有意义的词语并减少片段的噪音。
        
        参数:
            text (str): 要从中提取关键词的文本。
        
        返回:
            List[str]: 提取的关键词列表。
        """
        # 移除标点符号并分割成单词
        words = re.findall(r'[\u4e00-\u9fff\w]+', text)
        
        # 改进的中文关键词提取：
        # 1. 偏好可能具有意义的完整词语（2-4个字符）
        # 2. 使用更智能的方法避免过度碎片化
        keywords = []
        for word in words:
            # 对于中文文本，提取有意义的片段
            if all('\u4e00' <= char <= '\u9fff' for char in word):
                # 中文词语 - 使用智能分割
                if len(word) <= 4:
                    # 短中文词语很可能具有意义
                    keywords.append(word)
                else:
                    # 对于较长的中文短语，提取可能的复合词
                    # 使用滑动窗口但具有更好的过滤
                    segments = set()
                    # 偏好常见的2-3字符片段
                    for i in range(len(word) - 1):
                        for length in [2, 3]:  # 专注于2-3字符的词语
                            if i + length <= len(word):
                                segment = word[i:i+length]
                                # 只添加不开始/结束于停用字符的片段
                                if (segment not in self.stop_words and
                                    not any(seg in self.stop_words for seg in [segment[0], segment[-1]])):
                                    segments.add(segment)
                    keywords.extend(list(segments))
            else:
                # 非中文词语（英文等）
                if len(word) >= self.min_keyword_length and word not in self.stop_words:
                    keywords.append(word)
        
        # 额外过滤
        filtered_keywords = []
        for word in keywords:
            if (len(word) >= self.min_keyword_length and 
                word not in self.stop_words and
                not word.isdigit() and
                not any(sw in word for sw in self.stop_words) and  # 避免包含停用词的词语
                word not in filtered_keywords):  # 避免重复
                filtered_keywords.append(word)
        
        return filtered_keywords
    
    def _extract_keyword_context(self, lines: List[str], line_num: int, line: str, keyword: str) -> str:
        """
        提取文本中关键词周围的上下文。
        
        参数:
            lines (List[str]): 文件中的所有行。
            line_num (int): 关键词出现的行号。
            line (str): 包含关键词的特定行。
            keyword (str): 要提取上下文的关键词。
        
        返回:
            str: 关键词周围的上下文文本。
        """
        context_window = self.config.file_monitoring.context_window_size
        
        # 查找关键词在行中的位置
        keyword_pos = line.find(keyword)
        if keyword_pos == -1:
            return line.strip()  # 回退到整行
        
        # 从当前行提取上下文
        line_start = max(0, keyword_pos - context_window // 2)
        line_end = min(len(line), keyword_pos + len(keyword) + context_window // 2)
        context = line[line_start:line_end]
        
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
    
    async def find_similar_keywords(self, keyword_data_list: List[KeywordData]) -> Dict[str, List[KeywordData]]:
        """
        使用AI查找应该链接在一起的相似关键词。
        
        参数:
            keyword_data_list (List[KeywordData]): 要分析相似性的KeywordData对象列表。
        
        返回:
            Dict[str, List[KeywordData]]: 将标准化关键词映射到相似KeywordData对象列表的字典。
        """
        # 按基本形式对关键词进行初始聚类分组
        keyword_groups = {}
        for kd in keyword_data_list:
            # 简单标准化：转换为小写进行初始分组
            normalized = kd.keyword.lower()
            if normalized not in keyword_groups:
                keyword_groups[normalized] = []
            keyword_groups[normalized].append(kd)
        
        # 使用AI验证和优化相似性
        final_groups = {}
        for base_keyword, group in keyword_groups.items():
            if len(group) > 1:
                # 只处理有多个出现次数的组
                verified_group = await self._ai_verify_similarity(group)
                if verified_group:
                    final_groups[base_keyword] = verified_group
        
        return final_groups
    
    async def _ai_verify_similarity(self, keyword_group: List[KeywordData]) -> List[KeywordData]:
        """
        使用AI验证组中的关键词是否指向同一个概念，
        并对心理学概念具有改进的语义理解。
        
        参数:
            keyword_group (List[KeywordData]): 要验证相似性的KeywordData对象组。
        
        返回:
            List[KeywordData]: 经验证的相似关键词组，如果不相似则返回空列表。
        """
        if len(keyword_group) < 2:
            return keyword_group
        
        # 准备详细的上下文供AI分析
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
            # 更健壮的肯定响应检查
            affirmative_responses = {"是", "是的", "相同", "一样", "同一个概念", "相同概念"}
            response_lower = response.strip().lower()
            
            if any(affirmative in response_lower for affirmative in affirmative_responses):
                return keyword_group
            else:
                return []
        except Exception as e:
            print(f"AI similarity verification error: {e}")
            return []  # 在AI失败时不假设相似性
