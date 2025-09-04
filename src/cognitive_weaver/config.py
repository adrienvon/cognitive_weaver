"""
Cognitive Weaver 配置模块
处理应用程序的配置设置

Configuration module for Cognitive Weaver
Handles application configuration settings
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from pydantic import BaseModel, Field

class AIModelConfig(BaseModel):
    """AI 模型设置的配置"""
    provider: str = Field("openai", description="AI provider: openai, ollama, deepseek, etc.")
    model_name: str = Field("gpt-3.5-turbo", description="Model name to use")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Base URL for API calls")
    temperature: float = Field(0.1, description="Temperature for AI responses")

class RelationConfig(BaseModel):
    """关系类型的配置"""
    predefined_relations: List[str] = Field(
        default_factory=lambda: [
            "支撑观点",
            "反驳观点", 
            "举例说明",
            "定义概念",
            "属于分类",
            "包含部分",
            "引出主题",
            "简单提及"
        ],
        description="Predefined relationship types"
    )
    custom_relations: List[str] = Field(default_factory=list, description="Custom relationship types")

class FileMonitoringConfig(BaseModel):
    """文件监控的配置"""
    watch_extensions: List[str] = Field(default_factory=lambda: [".md"], description="File extensions to watch")
    context_window_size: int = Field(100, description="Number of characters around links for context")
    ignore_patterns: List[str] = Field(default_factory=lambda: ["/.git/", "/.obsidian/"], description="Patterns to ignore")
    folders_to_scan: List[str] = Field(default_factory=list, description="List of folder paths to scan for markdown files")

class CognitiveWeaverConfig(BaseModel):
    """主配置模型"""
    ai_model: AIModelConfig = Field(default_factory=AIModelConfig)
    relations: RelationConfig = Field(default_factory=RelationConfig)
    file_monitoring: FileMonitoringConfig = Field(default_factory=FileMonitoringConfig)
    max_retries: int = Field(3, description="Maximum retries for AI calls")
    backup_files: bool = Field(True, description="Whether to create backups before modifying files")

def load_config(config_file: Optional[str] = None) -> CognitiveWeaverConfig:
    """
    从文件加载配置或使用默认配置。
    
    参数:
        config_file (Optional[str]): 配置文件的路径。如果为 None，则使用默认配置。
    
    返回:
        CognitiveWeaverConfig: 加载的配置对象。
    """
    default_config = CognitiveWeaverConfig()
    
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                return CognitiveWeaverConfig(**config_data)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                print("Using default configuration.")
    
    return default_config

def create_default_config(config_path: Path):
    """
    在指定路径创建默认配置文件。
    
    参数:
        config_path (Path): 默认配置文件应创建的路径。
    """
    default_config = CognitiveWeaverConfig()
    config_data = default_config.dict()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)
    
    print(f"Default configuration created at {config_path}")
