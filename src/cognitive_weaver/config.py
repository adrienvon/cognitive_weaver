"""
Configuration module for Cognitive Weaver
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from pydantic import BaseModel, Field

class AIModelConfig(BaseModel):
    """Configuration for AI model settings"""
    provider: str = Field("openai", description="AI provider: openai, ollama, deepseek, etc.")
    model_name: str = Field("gpt-3.5-turbo", description="Model name to use")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Base URL for API calls")
    temperature: float = Field(0.1, description="Temperature for AI responses")

class RelationConfig(BaseModel):
    """Configuration for relationship types"""
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
    """Configuration for file monitoring"""
    watch_extensions: List[str] = Field(default_factory=lambda: [".md"], description="File extensions to watch")
    context_window_size: int = Field(100, description="Number of characters around links for context")
    ignore_patterns: List[str] = Field(default_factory=lambda: ["/.git/", "/.obsidian/"], description="Patterns to ignore")
    folders_to_scan: List[str] = Field(default_factory=list, description="List of folder paths to scan for markdown files")

class CognitiveWeaverConfig(BaseModel):
    """Main configuration model"""
    ai_model: AIModelConfig = Field(default_factory=AIModelConfig)
    relations: RelationConfig = Field(default_factory=RelationConfig)
    file_monitoring: FileMonitoringConfig = Field(default_factory=FileMonitoringConfig)
    max_retries: int = Field(3, description="Maximum retries for AI calls")
    backup_files: bool = Field(True, description="Whether to create backups before modifying files")

def load_config(config_file: Optional[str] = None) -> CognitiveWeaverConfig:
    """
    Load configuration from file or use defaults.
    
    Args:
        config_file (Optional[str]): Path to the configuration file. If None, uses default configuration.
    
    Returns:
        CognitiveWeaverConfig: The loaded configuration object.
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
    Create a default configuration file at the specified path.
    
    Args:
        config_path (Path): The path where the default configuration file should be created.
    """
    default_config = CognitiveWeaverConfig()
    config_data = default_config.dict()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)
    
    print(f"Default configuration created at {config_path}")
