import os
import json
import csv
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Handles file I/O operations for the AI Film Editor.
    Manages temporary files, exports, and file validation.
    """
    
    def __init__(self, config: dict):
        """
        Initialize FileHandler with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.temp_dir = Path(config.get('temp_dir', './data/cache'))
        self.output_dir = Path('./data/output')
        
        # Create directories if they don't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported file formats
        self.video_formats = set(config.get('video', {}).get('supported_formats', ['.mp4', '.avi', '.mov', '.mkv']))
        self.script_formats = set(config.get('script', {}).get('supported_formats', ['.txt', '.srt', '.vtt']))
        self.audio_formats = set(config.get('audio', {}).get('supported_formats', ['.wav', '.mp3', '.m4a']))
        
    def validate_file(self, file_path: Union[str, Path], file_type: str) -> bool:
        """
        Validate file format and accessibility.
        
        Args:
            file_path: Path to file
            file_type: Type of file ('video', 'script', 'audio')
            
        Returns:
            True if file is valid, False otherwise
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            logger.error(f"File does not exist: {path}")
            return False
        
        # Check file extension
        extension = path.suffix.lower()
        
        if file_type == 'video' and extension not in self.video_formats:
            logger.error(f"Unsupported video format: {extension}")
            return False
        elif file_type == 'script' and extension not in self.script_formats:
            logger.error(f"Unsupported script format: {extension}")
            return False
        elif file_type == 'audio' and extension not in self.audio_formats:
            logger.error(f"Unsupported audio format: {extension}")
            return False
        
        # Check file size
        file_size = path.stat().st_size
        file_limits = self.config.get('file_limits', {})
        max_sizes = {
            'video': file_limits.get('max_video_size_mb', 2048) * 1024 * 1024,
            'script': file_limits.get('max_script_size_kb', 500) * 1024,
            'audio': file_limits.get('max_audio_size_mb', 500) * 1024 * 1024
        }
        
        if file_size > max_sizes.get(file_type, float('inf')):
            logger.error(f"File too large: {file_size} bytes")
            return False
        
        return True
    
    def create_temp_file(self, suffix: str = '', prefix: str = 'ai_editor_') -> str:
        """
        Create a temporary file and return its path.
        
        Args:
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            prefix=prefix,
            dir=self.temp_dir
        )
        temp_file.close()
        
        logger.info(f"Created temporary file: {temp_file.name}")
        return temp_file.name
    
    def save_uploaded_file(self, uploaded_file, file_type: str) -> Optional[str]:
        """
        Save uploaded file to temporary location.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            file_type: Type of file for validation
            
        Returns:
            Path to saved file or None if failed
        """
        if uploaded_file is None:
            return None
        
        try:
            # Create temporary file with appropriate extension
            suffix = Path(uploaded_file.name).suffix
            temp_path = self.create_temp_file(suffix=suffix)
            
            # Write uploaded content
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Validate saved file
            if self.validate_file(temp_path, file_type):
                logger.info(f"Successfully saved uploaded file: {temp_path}")
                return temp_path
            else:
                self.cleanup_file(temp_path)
                return None
                
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            return None
    
    def export_suggestions(self, 
                         suggestions: List,
                         format: str = 'json',
                         filename: Optional[str] = None) -> Optional[str]:
        """
        Export suggestions to file.
        
        Args:
            suggestions: List of suggestions to export
            format: Export format ('json', 'csv', 'txt')
            filename: Optional custom filename
            
        Returns:
            Path to exported file or None if failed
        """
        if not suggestions:
            logger.warning("No suggestions to export")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"suggestions_{timestamp}.{format}"
        
        output_path = self.output_dir / filename
        
        try:
            if format == 'json':
                return self._export_json(suggestions, output_path)
            elif format == 'csv':
                return self._export_csv(suggestions, output_path)
            elif format == 'txt':
                return self._export_txt(suggestions, output_path)
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting suggestions: {e}")
            return None
    
    def _export_json(self, suggestions: List, output_path: Path) -> str:
        """Export suggestions as JSON."""
        suggestion_data = []
        
        for suggestion in suggestions:
            data = {
                'timestamp': getattr(suggestion, 'timestamp', 0),
                'confidence': getattr(suggestion, 'confidence', 0.5),
                'reason': getattr(suggestion, 'reason', ''),
                'suggestion_type': getattr(suggestion, 'suggestion_type', 'unknown'),
                'metadata': getattr(suggestion, 'metadata', {})
            }
            suggestion_data.append(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(suggestion_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported suggestions to JSON: {output_path}")
        return str(output_path)
    
    def _export_csv(self, suggestions: List, output_path: Path) -> str:
        """Export suggestions as CSV."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Timestamp', 'Confidence', 'Type', 'Reason'])
            
            # Write suggestions
            for suggestion in suggestions:
                writer.writerow([
                    getattr(suggestion, 'timestamp', 0),
                    getattr(suggestion, 'confidence', 0.5),
                    getattr(suggestion, 'suggestion_type', 'unknown'),
                    getattr(suggestion, 'reason', '')
                ])
        
        logger.info(f"Exported suggestions to CSV: {output_path}")
        return str(output_path)
    
    def _export_txt(self, suggestions: List, output_path: Path) -> str:
        """Export suggestions as text file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("AI Film Editor - Cut Suggestions\n")
            f.write("=" * 50 + "\n\n")
            
            for i, suggestion in enumerate(suggestions):
                timestamp = getattr(suggestion, 'timestamp', 0)
                confidence = getattr(suggestion, 'confidence', 0.5)
                reason = getattr(suggestion, 'reason', '')
                suggestion_type = getattr(suggestion, 'suggestion_type', 'unknown')
                
                # Format timestamp
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                f.write(f"Cut #{i+1}: {time_str}\n")
                f.write(f"Type: {suggestion_type.replace('_', ' ').title()}\n")
                f.write(f"Confidence: {confidence:.2%}\n")
                f.write(f"Reason: {reason}\n")
                f.write("-" * 30 + "\n\n")
        
        logger.info(f"Exported suggestions to text: {output_path}")
        return str(output_path)
    
    def cleanup_file(self, file_path: Union[str, Path]):
        """
        Remove a file safely.
        
        Args:
            file_path: Path to file to remove
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Cleaned up file: {path}")
        except Exception as e:
            logger.warning(f"Could not cleanup file {file_path}: {e}")
    
    def cleanup_temp_files(self):
        """Clean up all temporary files."""
        try:
            temp_files = list(self.temp_dir.glob('ai_editor_*'))
            for temp_file in temp_files:
                temp_file.unlink()
                logger.info(f"Cleaned up temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"Error during temp file cleanup: {e}")
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'extension': path.suffix,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'is_file': path.is_file(),
            'is_readable': os.access(path, os.R_OK)
        }
