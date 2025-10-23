import tiktoken
import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
import glob
import os

def num_tokens_from_string(string: str, model_name) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class TokenCalculator:
    """
    A utility class for calculating tokens from various input sources including
    files, folders, and pattern-based file matching.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the TokenCalculator with a specific model.
        
        Args:
            model_name: The model name to use for token calculation (default: gpt-3.5-turbo)
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
            self.logger.info(f"Initialized TokenCalculator with model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize encoding for model {model_name}: {e}")
            # Fallback to cl100k_base encoding (used by gpt-3.5-turbo and gpt-4)
            self.encoding = tiktoken.get_encoding("cl100k_base")
            self.logger.warning(f"Using fallback encoding: cl100k_base")
    
    def calculate_tokens_from_string(self, text: str) -> int:
        """
        Calculate tokens from a string.
        
        Args:
            text: The input text string
            
        Returns:
            Number of tokens in the text
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def calculate_tokens_from_file(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Calculate tokens from a single file.
        
        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary containing file info and token count
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            token_count = self.calculate_tokens_from_string(content)
            
            result = {
                'file_path': str(file_path),
                'file_size_bytes': file_path.stat().st_size,
                'token_count': token_count,
                'encoding': encoding,
                'status': 'success'
            }
            
            self.logger.debug(f"Calculated {token_count} tokens for file: {file_path}")
            return result
            
        except Exception as e:
            error_result = {
                'file_path': str(file_path),
                'token_count': 0,
                'error': str(e),
                'status': 'error'
            }
            self.logger.error(f"Error calculating tokens for file {file_path}: {e}")
            return error_result
    
    def calculate_tokens_from_files(self, file_paths: List[Union[str, Path]], encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Calculate tokens from a list of files.
        
        Args:
            file_paths: List of file paths
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary containing summary and individual file results
        """
        if not file_paths:
            return {
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0,
                'total_tokens': 0,
                'file_results': [],
                'status': 'success'
            }
        
        file_results = []
        total_tokens = 0
        successful_files = 0
        failed_files = 0
        
        for file_path in file_paths:
            result = self.calculate_tokens_from_file(file_path, encoding)
            file_results.append(result)
            
            if result['status'] == 'success':
                total_tokens += result['token_count']
                successful_files += 1
            else:
                failed_files += 1
        
        summary = {
            'total_files': len(file_paths),
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_tokens': total_tokens,
            'file_results': file_results,
            'status': 'success' if failed_files == 0 else 'partial_success'
        }
        
        self.logger.info(f"Processed {len(file_paths)} files: {successful_files} successful, {failed_files} failed, {total_tokens} total tokens")
        return summary
    
    def calculate_tokens_from_folder(self, folder_path: Union[str, Path], recursive: bool = True, 
                                   file_patterns: Optional[List[str]] = None, 
                                   encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Calculate tokens from all files in a folder.
        
        Args:
            folder_path: Path to the folder
            recursive: Whether to search recursively (default: True)
            file_patterns: List of file patterns to match (e.g., ['*.java', '*.py'])
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary containing summary and individual file results
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
        
        # Find all files
        files = []
        if file_patterns:
            for pattern in file_patterns:
                if recursive:
                    files.extend(folder_path.rglob(pattern))
                else:
                    files.extend(folder_path.glob(pattern))
        else:
            if recursive:
                files = [f for f in folder_path.rglob('*') if f.is_file()]
            else:
                files = [f for f in folder_path.glob('*') if f.is_file()]
        
        # Remove duplicates and sort
        files = sorted(list(set(files)))
        
        self.logger.info(f"Found {len(files)} files in folder: {folder_path}")
        
        return self.calculate_tokens_from_files(files, encoding)
    
    def calculate_tokens_from_folders(self, folder_paths: List[Union[str, Path]], 
                                    recursive: bool = True,
                                    file_patterns: Optional[List[str]] = None,
                                    encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Calculate tokens from multiple folders.
        
        Args:
            folder_paths: List of folder paths
            recursive: Whether to search recursively (default: True)
            file_patterns: List of file patterns to match
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary containing summary and folder results
        """
        if not folder_paths:
            return {
                'total_folders': 0,
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0,
                'total_tokens': 0,
                'folder_results': [],
                'status': 'success'
            }
        
        folder_results = []
        total_tokens = 0
        total_files = 0
        successful_files = 0
        failed_files = 0
        
        for folder_path in folder_paths:
            try:
                result = self.calculate_tokens_from_folder(folder_path, recursive, file_patterns, encoding)
                folder_results.append({
                    'folder_path': str(folder_path),
                    'result': result,
                    'status': 'success'
                })
                
                total_tokens += result['total_tokens']
                total_files += result['total_files']
                successful_files += result['successful_files']
                failed_files += result['failed_files']
                
            except Exception as e:
                error_result = {
                    'folder_path': str(folder_path),
                    'result': None,
                    'error': str(e),
                    'status': 'error'
                }
                folder_results.append(error_result)
                self.logger.error(f"Error processing folder {folder_path}: {e}")
        
        summary = {
            'total_folders': len(folder_paths),
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_tokens': total_tokens,
            'folder_results': folder_results,
            'status': 'success' if failed_files == 0 else 'partial_success'
        }
        
        self.logger.info(f"Processed {len(folder_paths)} folders: {total_files} files, {successful_files} successful, {failed_files} failed, {total_tokens} total tokens")
        return summary
    
    def calculate_tokens_by_pattern(self, base_paths: List[Union[str, Path]], 
                                  patterns: List[str],
                                  recursive: bool = True,
                                  encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Calculate tokens from files matching specific patterns.
        
        Args:
            base_paths: List of base paths to search in
            patterns: List of glob patterns (e.g., ['*.java', '**/*.py'])
            recursive: Whether to search recursively (default: True)
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary containing summary and pattern results
        """
        if not base_paths or not patterns:
            return {
                'total_patterns': 0,
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0,
                'total_tokens': 0,
                'pattern_results': [],
                'status': 'success'
            }
        
        pattern_results = []
        total_tokens = 0
        total_files = 0
        successful_files = 0
        failed_files = 0
        
        for pattern in patterns:
            pattern_files = []
            
            for base_path in base_paths:
                base_path = Path(base_path)
                if not base_path.exists():
                    self.logger.warning(f"Base path does not exist: {base_path}")
                    continue
                
                if recursive:
                    pattern_files.extend(base_path.rglob(pattern))
                else:
                    pattern_files.extend(base_path.glob(pattern))
            
            # Remove duplicates and filter files only
            pattern_files = sorted(list(set([f for f in pattern_files if f.is_file()])))
            
            self.logger.info(f"Pattern '{pattern}' matched {len(pattern_files)} files")
            
            # Calculate tokens for files matching this pattern
            if pattern_files:
                file_result = self.calculate_tokens_from_files(pattern_files, encoding)
                pattern_results.append({
                    'pattern': pattern,
                    'file_count': len(pattern_files),
                    'result': file_result,
                    'status': 'success'
                })
                
                total_tokens += file_result['total_tokens']
                total_files += file_result['total_files']
                successful_files += file_result['successful_files']
                failed_files += file_result['failed_files']
            else:
                pattern_results.append({
                    'pattern': pattern,
                    'file_count': 0,
                    'result': None,
                    'status': 'no_matches'
                })
        
        summary = {
            'total_patterns': len(patterns),
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_tokens': total_tokens,
            'pattern_results': pattern_results,
            'status': 'success' if failed_files == 0 else 'partial_success'
        }
        
        self.logger.info(f"Processed {len(patterns)} patterns: {total_files} files, {successful_files} successful, {failed_files} failed, {total_tokens} total tokens")
        return summary
    
    def get_common_file_patterns(self) -> Dict[str, List[str]]:
        """
        Get common file patterns for different programming languages and file types.
        
        Returns:
            Dictionary mapping language/file type to list of patterns
        """
        return {
            'java': ['*.java'],
            'python': ['*.py', '*.pyi'],
            'javascript': ['*.js', '*.jsx', '*.ts', '*.tsx'],
            'html': ['*.html', '*.htm'],
            'css': ['*.css', '*.scss', '*.sass'],
            'xml': ['*.xml'],
            'json': ['*.json'],
            'yaml': ['*.yml', '*.yaml'],
            'markdown': ['*.md', '*.markdown'],
            'shell': ['*.sh', '*.bash', '*.zsh'],
            'config': ['*.properties', '*.conf', '*.ini', '*.cfg'],
            'all_text': ['*.txt', '*.log', '*.md', '*.rst'],
            'all_code': ['*.java', '*.py', '*.js', '*.ts', '*.html', '*.css', '*.xml', '*.json']
        }
    
    def calculate_tokens_by_language(self, base_paths: List[Union[str, Path]], 
                                   languages: List[str],
                                   recursive: bool = True,
                                   encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Calculate tokens for specific programming languages.
        
        Args:
            base_paths: List of base paths to search in
            languages: List of language names (e.g., ['java', 'python'])
            recursive: Whether to search recursively (default: True)
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary containing summary and language results
        """
        common_patterns = self.get_common_file_patterns()
        
        # Get patterns for specified languages
        patterns = []
        for language in languages:
            if language.lower() in common_patterns:
                patterns.extend(common_patterns[language.lower()])
            else:
                self.logger.warning(f"Unknown language: {language}")
        
        if not patterns:
            return {
                'total_languages': 0,
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0,
                'total_tokens': 0,
                'language_results': [],
                'status': 'error',
                'error': 'No valid language patterns found'
            }
        
        # Use pattern-based calculation
        result = self.calculate_tokens_by_pattern(base_paths, patterns, recursive, encoding)
        
        # Add language-specific information
        result['total_languages'] = len(languages)
        result['languages'] = languages
        result['language_results'] = result.pop('pattern_results', [])
        
        return result
