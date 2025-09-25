"""
Configuration Module
Handles application configuration and settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class Config:
    """Configuration management for YT-Nara"""
    
    def __init__(self, config_file: str = "data/config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "app": {
                "name": "YT-Nara",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "content_discovery": {
                "max_results_per_platform": 20,
                "search_timeout": 30,
                "relevance_threshold": 0.3
            },
            "video_processing": {
                "max_video_duration": 60,
                "output_format": "mp4",
                "quality": "720p",
                "watermark_enabled": True,
                "watermark_text": "YT-Nara",
                "watermark_position": "bottom_right"
            },
            "upload": {
                "max_retries": 3,
                "retry_delay": 30,
                "upload_delay_min": 30,
                "upload_delay_max": 60
            },
            "scheduler": {
                "check_interval": 30,
                "max_concurrent_uploads": 2
            },
            "platforms": {
                "youtube": {
                    "enabled": True,
                    "accounts": 2
                },
                "instagram": {
                    "enabled": True,
                    "accounts": 2
                }
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                logging.error(f"Error loading config: {str(e)}")
                return default_config
        else:
            # Save default config
            self._save_config(default_config)
            return default_config
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self._save_config(self._config)
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        if self.config_file.exists():
            self.config_file.unlink()
        self._config = self._load_config()
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()