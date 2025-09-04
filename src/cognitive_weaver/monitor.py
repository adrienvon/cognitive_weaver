"""
Cognitive Weaver 的文件监控模块
使用 watchdog 库监控 Obsidian 知识库中的文件变化

File monitoring module for Cognitive Weaver
Uses watchdog to monitor file changes in the Obsidian vault
"""

import asyncio
import time
from pathlib import Path
from typing import Set, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import threading
from .parser import LinkParser
from .ai_inference import AIInferenceEngine
from .rewriter import FileRewriter
from .keyword_extractor import KeywordExtractor
from .knowledge_graph import KnowledgeGraph

class VaultMonitor:
    """Monitors the Obsidian vault for file changes and processes them
    
    监控 Obsidian 知识库的文件变化并处理它们
    """
    
    def __init__(self, vault_path: Path, config):
        """
        Initialize the vault monitor with configuration and components.
        
        使用配置和组件初始化知识库监控器
        
        Args:
            vault_path (Path): Path to the Obsidian vault directory
            config: Configuration object containing monitoring settings
            
            参数:
                vault_path (Path): Obsidian 知识库目录的路径
                config: 包含监控设置的配置对象
        """
        self.vault_path = vault_path
        self.config = config
        self.observer = Observer()
        self.event_handler = VaultEventHandler(self.process_file_sync, config)
        self.processed_files: Set[Path] = set()
        self.processing_lock = threading.Lock()
        
        # 初始化组件
        self.link_parser = LinkParser(config)
        self.ai_engine = AIInferenceEngine(config)
        self.file_rewriter = FileRewriter(config)
        self.keyword_extractor = KeywordExtractor(config, self.ai_engine)
        self.knowledge_graph = KnowledgeGraph()
    
    def start_watching(self):
        """
        Start watching the vault for file changes.
        
        开始监控知识库的文件变化。
        
        This method starts the file system observer and enters an infinite loop
        to keep the monitoring active until interrupted by keyboard.
        
        此方法启动文件系统观察器并进入无限循环以保持监控活动，直到被键盘中断。
        
        Returns:
            None
            
        返回:
            无
        """
        self.observer.schedule(self.event_handler, str(self.vault_path), recursive=True)
        self.observer.start()
        print(f"Started watching vault: {self.vault_path}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
    
    async def process_entire_vault(self):
        """
        Process all markdown files in the vault in batch mode.
        
        批量处理知识库中的所有 Markdown 文件。
        
        Returns:
            None
            
        返回:
            无
        """
        print("Processing entire vault in batch mode...")
        md_files = list(self.vault_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")
        
        for file_path in md_files:
            if self.should_process_file(file_path):
                await self.process_file(file_path)
        
        print("Batch processing completed.")
    
    async def process_folder(self, folder_path: Path):
        """
        Process all markdown files in a specific folder.
        
        处理特定文件夹中的所有 Markdown 文件。
        
        Args:
            folder_path (Path): Path to the folder to process
            
            参数:
                folder_path (Path): 要处理的文件夹路径
            
        Returns:
            None
            
        返回:
            无
        """
        if not folder_path.exists():
            print(f"Error: Folder path '{folder_path}' does not exist.")
            return
        
        if not folder_path.is_dir():
            print(f"Error: '{folder_path}' is not a directory.")
            return
        
        print(f"Processing folder: {folder_path}")
        md_files = list(folder_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files in the folder")
        
        for file_path in md_files:
            if self.should_process_file(file_path):
                await self.process_file(file_path)
        
        print("Folder processing completed.")
    
    async def process_file(self, file_path: Path):
        """
        Async processing of a single file.
        
        异步处理单个文件。
        
        Args:
            file_path (Path): Path to the file to process
            
            参数:
                file_path (Path): 要处理的文件路径
            
        Returns:
            None
            
        返回:
            无
        """
        if not self.should_process_file(file_path):
            return
        
        with self.processing_lock:
            if file_path in self.processed_files:
                return
            
            self.processed_files.add(file_path)
            print(f"Processing file: {file_path.name}")
            
            try:
                # 从文件中解析链接
                links_with_context = self.link_parser.parse_file(file_path)
                
                if links_with_context:
                    print(f"Found {len(links_with_context)} links in {file_path.name}")
                    
                    # 使用 AI 处理每个链接
                    for link_data in links_with_context:
                        relation_link = await self.ai_engine.infer_relation(link_data)
                        if relation_link:
                            # 使用关系链接重写文件
                            await self.file_rewriter.add_relation_to_file(
                                file_path, link_data, relation_link
                            )
                            # 使用节点和边更新知识图谱
                            self._update_knowledge_graph(link_data, relation_link)
                else:
                    print(f"No links found in {file_path.name}")
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
            finally:
                self.processed_files.remove(file_path)
    
    async def process_keywords_for_folder(self, folder_path: Path):
        """
        Process keywords across all files in a folder for automatic linking.
        
        处理文件夹中所有文件的关键词以进行自动链接。
        
        Args:
            folder_path (Path): Path to the folder to process keywords for
            
            参数:
                folder_path (Path): 要处理关键词的文件夹路径
            
        Returns:
            None
            
        返回:
            无
        """
        print(f"Processing keywords for folder: {folder_path}")
        
        # 收集所有 Markdown 文件
        md_files = list(folder_path.rglob("*.md"))
        if not md_files:
            print("No markdown files found in the folder.")
            return
        
        # 从所有文件中提取关键词
        all_keywords = []
        for file_path in md_files:
            if self.should_process_file(file_path):
                keywords = self.keyword_extractor.extract_keywords_from_file(file_path)
                all_keywords.extend(keywords)
        
        if not all_keywords:
            print("No keywords found in any files.")
            return
        
        print(f"Found {len(all_keywords)} potential keywords across {len(md_files)} files")
        
        # 使用 AI 查找相似关键词
        similar_keyword_groups = await self.keyword_extractor.find_similar_keywords(all_keywords)
        
        if not similar_keyword_groups:
            print("No similar keyword groups found.")
            return
        
        print(f"Found {len(similar_keyword_groups)} groups of similar keywords")
        
        # 为相似关键词添加链接
        for base_keyword, keyword_group in similar_keyword_groups.items():
            if len(keyword_group) > 1:
                print(f"Linking {len(keyword_group)} occurrences of '{base_keyword}'")
                for keyword_data in keyword_group:
                    await self.file_rewriter.add_keyword_links_to_file(
                        keyword_data.file_path, keyword_data, base_keyword
                    )
        
        print("Keyword linking completed.")
        
        # 关键词处理后保存知识图谱
        self.knowledge_graph.save()
    
    def process_file_sync(self, file_path: Path):
        """
        Synchronous wrapper for async file processing (for event handler).
        
        异步文件处理的同步包装器（用于事件处理器）。
        
        Args:
            file_path (Path): Path to the file to process
            
            参数:
                file_path (Path): 要处理的文件路径
            
        Returns:
            None
            
        返回:
            无
        """
        if not self.should_process_file(file_path):
            return
        
        # 为同步上下文创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_file(file_path))
        finally:
            loop.close()
    
    def should_process_file(self, file_path: Path) -> bool:
        """
        Check if a file should be processed based on config.
        
        根据配置检查文件是否应该被处理。
        
        Args:
            file_path (Path): Path to the file to check
            
            参数:
                file_path (Path): 要检查的文件路径
            
        Returns:
            bool: True if the file should be processed, False otherwise
            
            返回:
                bool: 如果文件应该被处理则为 True，否则为 False
        """
        if not file_path.is_file() or file_path.suffix != ".md":
            return False
        
        # 检查忽略模式
        file_str = str(file_path)
        for pattern in self.config.file_monitoring.ignore_patterns:
            if pattern in file_str:
                return False
        
        return True
    
    async def update_knowledge_graph_from_existing_files(self):
        """
        Update knowledge graph from all existing files, including those with relation links.
        
        从所有现有文件更新知识图谱，包括那些包含关系链接的文件。
        
        Returns:
            None
            
        返回:
            无
        """
        print("Updating knowledge graph from existing files...")
        md_files = list(self.vault_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")
        
        for file_path in md_files:
            if self.should_process_file(file_path):
                await self._update_knowledge_graph_from_file(file_path)
        
        # Save the final knowledge graph
        self.knowledge_graph.save()
        print("Knowledge graph update completed.")
    
    async def _update_knowledge_graph_from_file(self, file_path: Path):
        """
        Update knowledge graph from a single file, including existing relation links.
        
        从单个文件更新知识图谱，包括现有的关系链接。
        
        Args:
            file_path (Path): Path to the file to update from
            
            参数:
                file_path (Path): 要从中更新知识图谱的文件路径
            
        Returns:
            None
            
        返回:
            无
        """
        try:
            # 解析文件但不跳过关系链接以提取所有关系
            links_with_relations = self.link_parser.parse_file(file_path, skip_relation_links=False)
            
            if not links_with_relations:
                return
            
            print(f"Found {len(links_with_relations)} links in {file_path.name} for knowledge graph")
            
            # 从文件内容中提取关系链接
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找文件中的所有关系链接
            relation_matches = self.link_parser.relation_pattern.finditer(content)
            
            for match in relation_matches:
                relation_link = match.group(0)  # 完整的关系链接，如 "[[简单提及]]"
                relation_type = relation_link.strip("[]")
                
                # 对于每个关系链接，我们需要找到源和目标概念
                # 这很复杂，因为我们需要解析关系链接周围的上下文
                # 目前，我们将专注于主要的链接解析方法
                pass
            
            # 处理每个链接以更新知识图谱
            for link_data in links_with_relations:
                # 对于现有的关系链接，我们需要从行中提取关系类型
                if self.link_parser.has_relation_links(link_data.original_line):
                    # 从行中提取关系类型
                    relation_match = self.link_parser.relation_pattern.search(link_data.original_line)
                    if relation_match:
                        relation_link = relation_match.group(0)
                        self._update_knowledge_graph(link_data, relation_link)
            
        except Exception as e:
            print(f"Error updating knowledge graph from {file_path.name}: {e}")
    
    def _update_knowledge_graph(self, link_data, relation_link):
        """
        Update the knowledge graph with nodes and relationships from processed links.
        
        使用处理过的链接中的节点和关系更新知识图谱。
        
        Args:
            link_data: Link data object containing source and target information
            relation_link: Relation link string (e.g., "[[简单提及]]")
            
        参数:
            link_data: 包含源和目标信息的链接数据对象
            relation_link: 关系链接字符串（例如，"[[简单提及]]"）
            
        Returns:
            None
            
        返回:
            无
        """
        try:
            # 从链接数据中提取源概念和目标概念
            source_concept = link_data.source_note  # 包含链接的文件
            target_concept = link_data.target_note  # 被链接的笔记
            
            # 从关系链接中提取关系类型（例如，"[[简单提及]]" -> "简单提及"）
            relation_type = relation_link.strip("[]")
            
            # 向知识图谱添加节点
            source_node = self.knowledge_graph.add_node(
                source_concept, 
                source_concept, 
                "concept",
                importance=1.0
            )
            target_node = self.knowledge_graph.add_node(
                target_concept,
                target_concept,
                "concept", 
                importance=1.0
            )
            
            # 使用关系类型在节点之间添加边
            self.knowledge_graph.add_edge(
                source_concept,
                target_concept,
                relation_type,  # 使用关系类型作为边标签
                strength=1.0
            )
            
            # 保存知识图谱
            self.knowledge_graph.save()
            
        except Exception as e:
            print(f"Error updating knowledge graph: {e}")

class VaultEventHandler(FileSystemEventHandler):
    """处理知识库的文件系统事件"""
    
    def __init__(self, process_callback: Callable, config):
        """
        使用处理回调和配置初始化事件处理器。
        
        参数:
            process_callback (Callable): 处理文件变化的回调函数
            config: 包含监控设置的配置对象
        """
        self.process_callback = process_callback
        self.config = config
        self.last_processed = 0
        self.debounce_time = 2.0  # seconds
    
    def on_modified(self, event):
        """
        处理文件修改事件。
        
        参数:
            event: 文件系统事件对象
            
        返回:
            无
        """
        if not isinstance(event, FileModifiedEvent):
            return
        
        file_path = Path(event.src_path)
        if not self.should_process_event(file_path):
            return
        
        # Debounce rapid file changes
        current_time = time.time()
        if current_time - self.last_processed < self.debounce_time:
            return
        
        self.last_processed = current_time
        self.process_callback(file_path)
    
    def should_process_event(self, file_path: Path) -> bool:
        """
        Check if an event should be processed.
        
        检查事件是否应该被处理。
        
        Args:
            file_path (Path): Path to the file from the event
            
            参数:
                file_path (Path): 来自事件的文件路径
                
        Returns:
            bool: True if the event should be processed, False otherwise
            
            返回:
                bool: 如果事件应该被处理则为 True，否则为 False
        """
        if not file_path.is_file() or file_path.suffix != ".md":
            return False
        
        # 检查忽略模式
        file_str = str(file_path)
        for pattern in self.config.file_monitoring.ignore_patterns:
            if pattern in file_str:
                return False
        
        return True
