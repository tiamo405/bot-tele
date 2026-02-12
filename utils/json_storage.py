"""
Utility class for JSON file storage operations
Tránh code trùng lặp khi làm việc với JSON files
"""
import json
import os
from typing import Any, Dict, Optional


class JSONStorage:
    """Base class for JSON file storage"""
    
    def __init__(self, file_path: str, default_data: Any = None):
        """
        Initialize JSON storage
        
        Args:
            file_path: Absolute path to JSON file
            default_data: Default data structure (dict, list, etc.) if file doesn't exist
        """
        self.file_path = file_path
        self.default_data = default_data if default_data is not None else {}
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create file and directory if not exists"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> Any:
        """
        Load data from JSON file
        
        Returns:
            Data from file or default_data if error
        """
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON from {self.file_path}: {e}")
            return self.default_data
    
    def save(self, data: Any) -> bool:
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON to {self.file_path}: {e}")
            return False
    
    def update(self, key: str, value: Any) -> bool:
        """
        Update a specific key in dict-based storage
        
        Args:
            key: Key to update
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        data = self.load()
        if not isinstance(data, dict):
            raise TypeError("update() only works with dict-based storage")
        
        data[key] = value
        return self.save(data)
    
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from dict-based storage
        
        Args:
            key: Key to delete
            
        Returns:
            True if successful, False otherwise
        """
        data = self.load()
        if not isinstance(data, dict):
            raise TypeError("delete() only works with dict-based storage")
        
        if key in data:
            del data[key]
            return self.save(data)
        return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value by key from dict-based storage
        
        Args:
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Value or default
        """
        data = self.load()
        if not isinstance(data, dict):
            raise TypeError("get() only works with dict-based storage")
        
        return data.get(key, default)
