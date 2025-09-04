"""
AI inference module for Cognitive Weaver
Handles communication with AI models for relationship extraction
"""

import asyncio
import json
from typing import Optional
from openai import OpenAI
from .parser import LinkData

class AIInferenceEngine:
    """Handles AI inference for relationship extraction"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize the AI client based on configuration"""
        ai_config = self.config.ai_model
        
        try:
            if ai_config.provider.lower() == "deepseek":
                # Initialize DeepSeek client
                self.client = OpenAI(
                    api_key=ai_config.api_key or "sk-3bde3d12ab464212aec4be3113016b33",
                    base_url=ai_config.base_url or "https://api.deepseek.com"
                )
            elif ai_config.provider.lower() == "openai":
                # Initialize OpenAI client
                self.client = OpenAI(
                    api_key=ai_config.api_key,
                    base_url=ai_config.base_url or "https://api.openai.com/v1"
                )
            else:
                raise ValueError(f"Unsupported AI provider: {ai_config.provider}")
        except Exception as e:
            print(f"Warning: Could not initialize AI client: {e}")
            print("Using mock mode for testing.")
            self.client = None
    
    async def infer_relation(self, link_data: LinkData) -> Optional[str]:
        """
        Infer the relationship between two notes using AI
        Returns the relationship link (e.g., "[[支撑观点]]") or None if failed
        """
        try:
            # Prepare the prompt using the template from the prompt file
            prompt = self._build_prompt(link_data)
            
            # Call the AI model
            response = await self._call_ai_model(prompt)
            
            # Extract and validate the relationship link
            relation_link = self._extract_relation_link(response)
            
            if relation_link and self._is_valid_relation(relation_link):
                return relation_link
            else:
                print(f"Invalid relation link received: {relation_link}")
                return None
                
        except Exception as e:
            print(f"AI inference error: {e}")
            # For testing purposes, return a mock relation
            print("Using mock relation for testing: [[简单提及]]")
            return "[[简单提及]]"
    
    def _build_prompt(self, link_data: LinkData) -> str:
        """Build the prompt for AI inference using the template"""
        return f"""
源笔记:《{link_data.source_note}》
目标笔记:《{link_data.target_note}》
上下文:"...{link_data.context_text}..."

请判断关系并生成链接。
"""
    
    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a response from the AI model for general prompts"""
        if system_prompt is None:
            system_prompt = "你是一位有帮助的AI助手，擅长文本分析和关键词提取。"
        
        # Make the API call
        response = self.client.chat.completions.create(
            model=self.config.ai_model.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.ai_model.temperature,
            max_tokens=200
        )
        
        return response.choices[0].message.content

    async def _call_ai_model(self, prompt: str) -> str:
        """Call the AI model with the prepared prompt"""
        # If client is not available (mock mode), return a mock response
        if self.client is None:
            print("Using mock AI response for testing")
            return "[[简单提及]]"
        
        # System prompt from the prompt file
        system_prompt = """你是一位专注于知识图谱分析的AI助手，对Obsidian的链接哲学有深刻理解。你的核心任务是：

1. 分析上下文: 阅读提供的、包含一个链接的文本片段（上下文）。
2. 判断关系: 根据上下文，从预定义关系列表中，选择一个最能描述"源笔记"与"目标笔记"之间关系。
3. 生成链接: 将选定的关系名称封装成一个标准的Obsidian wiki链接 `[[关系名称]]`。
4. 严格输出: 你的最终回答必须且只能是一个单一的、无任何多余文本的Obsidian wiki链接。不要包含任何解释、问候、标点或额外的文字。

预定义关系列表：
- 支撑观点
- 反驳观点
- 举例说明
- 定义概念
- 属于分类
- 包含部分
- 引出主题
- 简单提及"""
        
        # Make the API call
        response = self.client.chat.completions.create(
            model=self.config.ai_model.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.ai_model.temperature,
            max_tokens=50
        )
        
        return response.choices[0].message.content
    
    def _extract_relation_link(self, response: str) -> Optional[str]:
        """Extract the relation link from the AI response"""
        # Look for Obsidian wiki link pattern
        import re
        match = re.search(r'\[\[(.*?)\]\]', response)
        if match:
            return f"[[{match.group(1)}]]"
        return None
    
    def _is_valid_relation(self, relation_link: str) -> bool:
        """Check if the extracted relation is valid"""
        # Extract the relation name from the link
        import re
        match = re.search(r'\[\[(.*?)\]\]', relation_link)
        if not match:
            return False
        
        relation_name = match.group(1)
        
        # Check if it's in the predefined relations
        predefined_relations = self.config.relations.predefined_relations
        return relation_name in predefined_relations
