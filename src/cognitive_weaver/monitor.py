"""
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
    """Monitors the Obsidian vault for file changes and processes them"""
    
    def __init__(self, vault_path: Path, config):
        self.vault_path = vault_path
        self.config = config
        self.observer = Observer()
        self.event_handler = VaultEventHandler(self.process_file_sync, config)
        self.processed_files: Set[Path] = set()
        self.processing_lock = threading.Lock()
        
        # Initialize components
        self.link_parser = LinkParser(config)
        self.ai_engine = AIInferenceEngine(config)
        self.file_rewriter = FileRewriter(config)
        self.keyword_extractor = KeywordExtractor(config, self.ai_engine)
        self.knowledge_graph = KnowledgeGraph()
    
    def start_watching(self):
        """Start watching the vault for file changes"""
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
        """Process all markdown files in the vault in batch mode"""
        print("Processing entire vault in batch mode...")
        md_files = list(self.vault_path.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")
        
        for file_path in md_files:
            if self.should_process_file(file_path):
                await self.process_file(file_path)
        
        print("Batch processing completed.")
    
    async def process_folder(self, folder_path: Path):
        """Process all markdown files in a specific folder"""
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
        """Async processing of a single file"""
        if not self.should_process_file(file_path):
            return
        
        with self.processing_lock:
            if file_path in self.processed_files:
                return
            
            self.processed_files.add(file_path)
            print(f"Processing file: {file_path.name}")
            
            try:
                # Parse links from the file
                links_with_context = self.link_parser.parse_file(file_path)
                
                if links_with_context:
                    print(f"Found {len(links_with_context)} links in {file_path.name}")
                    
                    # Process each link with AI
                    for link_data in links_with_context:
                        relation_link = await self.ai_engine.infer_relation(link_data)
                        if relation_link:
                            # Rewrite the file with the relation link
                            await self.file_rewriter.add_relation_to_file(
                                file_path, link_data, relation_link
                            )
                            # Update knowledge graph with nodes and edges
                            self._update_knowledge_graph(link_data, relation_link)
                else:
                    print(f"No links found in {file_path.name}")
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
            finally:
                self.processed_files.remove(file_path)
    
    async def process_keywords_for_folder(self, folder_path: Path):
        """Process keywords across all files in a folder for automatic linking"""
        print(f"Processing keywords for folder: {folder_path}")
        
        # Collect all markdown files
        md_files = list(folder_path.rglob("*.md"))
        if not md_files:
            print("No markdown files found in the folder.")
            return
        
        # Extract keywords from all files
        all_keywords = []
        for file_path in md_files:
            if self.should_process_file(file_path):
                keywords = self.keyword_extractor.extract_keywords_from_file(file_path)
                all_keywords.extend(keywords)
        
        if not all_keywords:
            print("No keywords found in any files.")
            return
        
        print(f"Found {len(all_keywords)} potential keywords across {len(md_files)} files")
        
        # Use AI to find similar keywords
        similar_keyword_groups = await self.keyword_extractor.find_similar_keywords(all_keywords)
        
        if not similar_keyword_groups:
            print("No similar keyword groups found.")
            return
        
        print(f"Found {len(similar_keyword_groups)} groups of similar keywords")
        
        # Add links for similar keywords
        for base_keyword, keyword_group in similar_keyword_groups.items():
            if len(keyword_group) > 1:
                print(f"Linking {len(keyword_group)} occurrences of '{base_keyword}'")
                for keyword_data in keyword_group:
                    await self.file_rewriter.add_keyword_links_to_file(
                        keyword_data.file_path, keyword_data, base_keyword
                    )
        
        print("Keyword linking completed.")
        
        # Save the knowledge graph after keyword processing
        self.knowledge_graph.save()
    
    def process_file_sync(self, file_path: Path):
        """Synchronous wrapper for async file processing (for event handler)"""
        if not self.should_process_file(file_path):
            return
        
        # Create a new event loop for synchronous context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_file(file_path))
        finally:
            loop.close()
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed based on config"""
        if not file_path.is_file() or file_path.suffix != ".md":
            return False
        
        # Check ignore patterns
        file_str = str(file_path)
        for pattern in self.config.file_monitoring.ignore_patterns:
            if pattern in file_str:
                return False
        
        return True
    
    async def update_knowledge_graph_from_existing_files(self):
        """Update knowledge graph from all existing files, including those with relation links"""
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
        """Update knowledge graph from a single file, including existing relation links"""
        try:
            # Parse file without skipping relation links to extract all relationships
            links_with_relations = self.link_parser.parse_file(file_path, skip_relation_links=False)
            
            if not links_with_relations:
                return
            
            print(f"Found {len(links_with_relations)} links in {file_path.name} for knowledge graph")
            
            # Extract relation links from the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all relation links in the file
            relation_matches = self.link_parser.relation_pattern.finditer(content)
            
            for match in relation_matches:
                relation_link = match.group(0)  # Full relation link like "[[简单提及]]"
                relation_type = relation_link.strip("[]")
                
                # For each relation link, we need to find the source and target concepts
                # This is complex because we need to parse the context around the relation link
                # For now, we'll focus on the main link parsing approach
                pass
            
            # Process each link to update knowledge graph
            for link_data in links_with_relations:
                # For existing relation links, we need to extract the relation type from the line
                if self.link_parser.has_relation_links(link_data.original_line):
                    # Extract relation type from the line
                    relation_match = self.link_parser.relation_pattern.search(link_data.original_line)
                    if relation_match:
                        relation_link = relation_match.group(0)
                        self._update_knowledge_graph(link_data, relation_link)
            
        except Exception as e:
            print(f"Error updating knowledge graph from {file_path.name}: {e}")
    
    def _update_knowledge_graph(self, link_data, relation_link):
        """Update knowledge graph with nodes and relationships from processed links"""
        try:
            # Extract source and target concepts from link data
            source_concept = link_data.source_note  # The file where the link is
            target_concept = link_data.target_note  # The linked note
            
            # Extract relation type from relation_link (e.g., "[[简单提及]]" -> "简单提及")
            relation_type = relation_link.strip("[]")
            
            # Add nodes to knowledge graph
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
            
            # Add edge between nodes with the relation type
            self.knowledge_graph.add_edge(
                source_concept,
                target_concept,
                relation_type,  # Use the relation type as edge label
                strength=1.0
            )
            
            # Save the knowledge graph
            self.knowledge_graph.save()
            
        except Exception as e:
            print(f"Error updating knowledge graph: {e}")

class VaultEventHandler(FileSystemEventHandler):
    """Handles file system events for the vault"""
    
    def __init__(self, process_callback: Callable, config):
        self.process_callback = process_callback
        self.config = config
        self.last_processed = 0
        self.debounce_time = 2.0  # seconds
    
    def on_modified(self, event):
        """Handle file modification events"""
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
        """Check if an event should be processed"""
        if not file_path.is_file() or file_path.suffix != ".md":
            return False
        
        # Check ignore patterns
        file_str = str(file_path)
        for pattern in self.config.file_monitoring.ignore_patterns:
            if pattern in file_str:
                return False
        
        return True
