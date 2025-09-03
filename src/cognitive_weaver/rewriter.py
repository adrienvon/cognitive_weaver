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
    """Handles safe file rewriting operations"""
    
    def __init__(self, config):
        self.config = config
    
    async def add_relation_to_file(self, file_path: Path, link_data: LinkData, relation_link: str) -> bool:
        """
        Add a relation link to the specified file at the correct position
        Returns True if successful, False otherwise
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
        """Create a backup of the file before modification"""
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        try:
            shutil.copy2(file_path, backup_path)
            print(f"Created backup: {backup_path.name}")
        except Exception as e:
            print(f"Warning: Could not create backup for {file_path.name}: {e}")
    
    async def _safe_write_file(self, file_path: Path, lines: list):
        """
        Safely write to a file using a temporary file to prevent data loss
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
        """Restore a file from backup if available"""
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
