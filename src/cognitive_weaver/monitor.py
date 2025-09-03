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
                
                if not links_with_context:
                    print(f"No links found in {file_path.name}")
                    return
                
                print(f"Found {len(links_with_context)} links in {file_path.name}")
                
                # Process each link with AI
                for link_data in links_with_context:
                    relation_link = await self.ai_engine.infer_relation(link_data)
                    if relation_link:
                        # Rewrite the file with the relation link
                        await self.file_rewriter.add_relation_to_file(
                            file_path, link_data, relation_link
                        )
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
            finally:
                self.processed_files.remove(file_path)
    
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
