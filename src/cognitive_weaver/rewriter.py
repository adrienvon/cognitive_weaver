"""
File rewriting module for Cognitive Weaver
Handles safe file modifications to add relation links
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from .parser import LinkData

class FileRewriter:
    """Handles safe file rewriting operations for Cognitive Weaver.
    
    This class provides methods to safely modify files by creating backups,
    using temporary files during writes, and restoring from backups when needed.
    
    Args:
        config: The application configuration object containing settings
                like backup_files flag and other operational parameters.
    """
    
    def __init__(self, config):
        """Initialize the FileRewriter with configuration.
        
        Args:
            config: The application configuration object.
        """
        self.config = config
    
    async def add_relation_to_file(self, file_path: Path, link_data: LinkData, relation_link: str) -> bool:
        """Add a relation link to the specified file at the correct position.
        
        This method safely adds a relation link to a file by:
        1. Creating a backup if configured
        2. Reading the file content
        3. Finding the target line based on link data
        4. Checking for duplicate links to avoid adding the same link multiple times
        5. Adding the relation link to the end of the target line
        6. Writing the modified content back safely using a temporary file
        
        Args:
            file_path: Path to the file to modify
            link_data: LinkData object containing information about where to add the link
            relation_link: The relation link string to add (e.g., "[[related-file.md]]")
            
        Returns:
            bool: True if the relation link was successfully added, False otherwise
                  (returns False if link already exists, line number is out of range, or any error occurs)
        """
        try:
            # Create backup if configured
            if self.config.backup_files:
                await self._create_backup(file_path)
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the target line and add the relation link
            line_index = link_data.line_number - 1
            if 0 <= line_index < len(lines):
                original_line = lines[line_index].rstrip()
                
                # Check if the line already has this relation link to avoid duplicates
                if relation_link in original_line:
                    print(f"Relation link {relation_link} already exists in line {link_data.line_number}")
                    return False
                
                # Add the relation link to the end of the line
                modified_line = f"{original_line} {relation_link}\n"
                lines[line_index] = modified_line
                
                # Write the modified content back to the file
                await self._safe_write_file(file_path, lines)
                
                print(f"Added {relation_link} to {file_path.name} at line {link_data.line_number}")
                return True
            else:
                print(f"Line number {link_data.line_number} out of range for {file_path.name}")
                return False
                
        except Exception as e:
            print(f"Error rewriting file {file_path.name}: {e}")
            return False
    
    async def _create_backup(self, file_path: Path):
        """Create a backup of the file before modification.
        
        This method creates a backup copy of the file with a .bak extension
        to allow for recovery in case of errors during file modification.
        
        Args:
            file_path: Path to the file for which to create a backup
            
        Note:
            If backup creation fails, a warning is printed but the operation continues
            to avoid blocking the main rewriting process.
        """
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        try:
            shutil.copy2(file_path, backup_path)
            print(f"Created backup: {backup_path.name}")
        except Exception as e:
            print(f"Warning: Could not create backup for {file_path.name}: {e}")
    
    async def _safe_write_file(self, file_path: Path, lines: list):
        """Safely write to a file using a temporary file to prevent data loss.
        
        This method uses a temporary file to write the content first, then
        atomically replaces the original file. This ensures that if the write
        operation fails, the original file is not corrupted.
        
        Args:
            file_path: Path to the file to write to
            lines: List of lines to write to the file
            
        Raises:
            Exception: If any error occurs during the write operation,
                       the temporary file is cleaned up and the exception is re-raised
        """
        # Create a temporary file
        temp_file = None
        try:
            # Write to temporary file first
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                           suffix='.tmp', delete=False) as f:
                temp_file = Path(f.name)
                f.writelines(lines)
            
            # Replace the original file with the temporary file
            shutil.move(str(temp_file), str(file_path))
            
        except Exception as e:
            # Clean up temporary file on error
            if temp_file and temp_file.exists():
                temp_file.unlink()
            raise e
    
    async def restore_backup(self, file_path: Path) -> bool:
        """Restore a file from backup if available.
        
        This method attempts to restore a file from its backup copy (.bak file)
        if the backup exists. This is useful for recovering from failed file
        modification operations.
        
        Args:
            file_path: Path to the file to restore from backup
            
        Returns:
            bool: True if the file was successfully restored from backup,
                  False if no backup exists or if restoration fails
        """
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        if backup_path.exists():
            try:
                shutil.move(str(backup_path), str(file_path))
                print(f"Restored {file_path.name} from backup")
                return True
            except Exception as e:
                print(f"Error restoring backup for {file_path.name}: {e}")
                return False
        return False
