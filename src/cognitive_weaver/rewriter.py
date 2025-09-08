"""
Cognitive Weaver 的文件重写模块
处理安全的文件修改以添加关系链接

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
    """处理 Cognitive Weaver 的安全文件重写操作
    
    Handles safe file rewriting operations for Cognitive Weaver.
    
    这个类提供安全修改文件的方法，包括创建备份、
    在写入时使用临时文件，以及在需要时从备份恢复。
    
    This class provides methods to safely modify files by creating backups,
    using temporary files during writes, and restoring from backups when needed.
    
    Args:
        config: 包含备份文件标志和其他操作参数的应用程序配置对象
        config: The application configuration object containing settings
                like backup_files flag and other operational parameters.
    """
    
    def __init__(self, config):
        """使用配置初始化文件重写器
        
        Initialize the FileRewriter with configuration.
        
        Args:
            config: 应用程序配置对象
            config: The application configuration object.
        """
        self.config = config
    
    async def add_relation_to_file(self, file_path: Path, link_data: LinkData, relation_link: str) -> bool:
        """在指定文件的正确位置添加关系链接
        
        Add a relation link to the specified file at the correct position.
        
        此方法通过以下步骤安全地向文件添加关系链接：
        1. 如果配置了，创建备份
        2. 读取文件内容
        3. 基于链接数据找到目标行
        4. 检查重复链接以避免多次添加相同链接
        5. 将关系链接添加到目标行的末尾
        6. 使用临时文件安全地将修改后的内容写回
        
        This method safely adds a relation link to a file by:
        1. Creating a backup if configured
        2. Reading the file content
        3. Finding the target line based on link data
        4. Checking for duplicate links to avoid adding the same link multiple times
        5. Adding the relation link to the end of the target line
        6. Writing the modified content back safely using a temporary file
        
        Args:
            file_path: 要修改的文件路径
            link_data: 包含添加链接位置信息的 LinkData 对象
            relation_link: 要添加的关系链接字符串（例如，"[[related-file.md]]"）
            
            file_path: Path to the file to modify
            link_data: LinkData object containing information about where to add the link
            relation_link: The relation link string to add (e.g., "[[related-file.md]]")
            
        Returns:
            bool: 如果成功添加关系链接返回 True，否则返回 False
                  （如果链接已存在、行号超出范围或发生任何错误，返回 False）
            bool: True if the relation link was successfully added, False otherwise
                  (returns False if link already exists, line number is out of range, or any error occurs)
        """
        try:
            # 如果配置了，创建备份
            if self.config.backup_files:
                await self._create_backup(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 找到目标行并添加关系链接
            line_index = link_data.line_number - 1
            if 0 <= line_index < len(lines):
                original_line = lines[line_index].rstrip()
                
                # 检查该行是否已包含此关系链接以避免重复
                if relation_link in original_line:
                    print(f"Relation link {relation_link} already exists in line {link_data.line_number}")
                    return False
                
                # 将关系链接添加到行的末尾
                modified_line = f"{original_line} {relation_link}\n"
                lines[line_index] = modified_line
                
                # 将修改后的内容安全写回文件
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
        """在修改前创建文件的备份
        
        Create a backup of the file before modification.
        
        此方法创建文件的备份副本，使用 .bak 扩展名，
        以便在文件修改过程中出现错误时进行恢复。
        
        This method creates a backup copy of the file with a .bak extension
        to allow for recovery in case of errors during file modification.
        
        Args:
            file_path: 要创建备份的文件路径
            file_path: Path to the file for which to create a backup
            
        Note:
            如果备份创建失败，会打印警告但操作继续，
            以避免阻塞主重写过程。
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
        """使用临时文件安全写入文件以防止数据丢失
        
        Safely write to a file using a temporary file to prevent data loss.
        
        此方法首先使用临时文件写入内容，然后
        原子性地替换原始文件。这确保如果写入
        操作失败，原始文件不会被损坏。
        
        This method uses a temporary file to write the content first, then
        atomically replaces the original file. This ensures that if the write
        operation fails, the original file is not corrupted.
        
        Args:
            file_path: 要写入的文件路径
            lines: 要写入文件的行的列表
            
            file_path: Path to the file to write to
            lines: List of lines to write to the file
            
        Raises:
            Exception: 如果在写入操作期间发生任何错误，
                       临时文件会被清理并重新引发异常
            Exception: If any error occurs during the write operation,
                       the temporary file is cleaned up and the exception is re-raised
        """
        # 创建临时文件
        temp_file = None
        try:
            # 首先写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                           suffix='.tmp', delete=False) as f:
                temp_file = Path(f.name)
                f.writelines(lines)
            
            # 用临时文件替换原始文件
            shutil.move(str(temp_file), str(file_path))
            
        except Exception as e:
            # 出错时清理临时文件
            if temp_file and temp_file.exists():
                temp_file.unlink()
            raise e
    
    async def add_keyword_links_to_file(self, file_path: Path, keyword_data, base_keyword: str) -> bool:
        """为文件中的关键词添加Obsidian链接
        
        Add Obsidian links for keywords in a file.
        
        此方法基于用户知识图谱分析，将文本中的关键词转换为Obsidian双链链接。
        它会在关键词周围添加[[]]标记，使其成为可点击的链接。
        
        This method converts keywords in text to Obsidian double-bracket links
        based on user knowledge graph analysis. It adds [[ ]] markers around
        keywords to make them clickable links.
        
        Args:
            file_path: 要修改的文件路径
            keyword_data: 包含关键词信息的KeywordData对象
            base_keyword: 标准化的基础关键词名称
            
            file_path: Path to the file to modify
            keyword_data: KeywordData object containing keyword information
            base_keyword: Normalized base keyword name
            
        Returns:
            bool: 如果成功添加链接返回 True，否则返回 False
            bool: True if links were successfully added, False otherwise
        """
        try:
            # 如果配置了，创建备份
            if self.config.backup_files:
                await self._create_backup(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 找到目标行并添加链接
            line_index = keyword_data.line_number - 1
            if 0 <= line_index < len(lines):
                original_line = lines[line_index].rstrip()
                
                # 检查关键词是否已经是链接格式
                if f"[[{keyword_data.keyword}]]" in original_line:
                    print(f"Keyword '{keyword_data.keyword}' already linked in line {keyword_data.line_number}")
                    return False
                
                # 将关键词转换为链接格式
                linked_keyword = f"[[{base_keyword}]]"
                modified_line = original_line.replace(keyword_data.keyword, linked_keyword, 1)
                
                # 如果行发生了变化，更新它
                if modified_line != original_line:
                    lines[line_index] = modified_line + '\n'
                    
                    # 将修改后的内容安全写回文件
                    await self._safe_write_file(file_path, lines)
                    
                    print(f"Added link [[{base_keyword}]] for '{keyword_data.keyword}' in {file_path.name} at line {keyword_data.line_number}")
                    return True
                else:
                    print(f"No changes made for keyword '{keyword_data.keyword}' in {file_path.name}")
                    return False
            else:
                print(f"Line number {keyword_data.line_number} out of range for {file_path.name}")
                return False
                
        except Exception as e:
            print(f"Error adding keyword links to file {file_path.name}: {e}")
            return False

    async def restore_backup(self, file_path: Path) -> bool:
        """从备份中恢复文件（如果可用）
        
        Restore a file from backup if available.
        
        此方法尝试从备份副本（.bak 文件）恢复文件，
        如果备份存在。这对于从失败的文件修改操作中恢复非常有用。
        
        This method attempts to restore a file from its backup copy (.bak file)
        if the backup exists. This is useful for recovering from failed file
        modification operations.
        
        Args:
            file_path: 要从备份中恢复的文件路径
            file_path: Path to the file to restore from backup
            
        Returns:
            bool: 如果成功从备份恢复文件返回 True，
                  如果备份不存在或恢复失败返回 False
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
