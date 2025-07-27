"""
Configuration utilities following SOLID principles
Single Responsibility: Handle configuration loading and validation
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class ETLConfig(BaseModel):
    """Configuration model with validation"""
    raw_data_path: str
    processed_data_path: str
    output_data_path: str
    encoding: str = "utf-8"
    decimal_separator: str = ","
    thousands_separator: str = "."
    chunk_size: int = 10000
    max_workers: int = 4
    
    class Config:
        extra = "allow"


class ConfigManager:
    """
    Single Responsibility: Manage configuration loading from multiple sources
    Open/Closed: Easy to extend with new configuration sources
    """
    
    def __init__(self, config_path: str = "config/etl_config.yaml"):
        self.config_path = Path(config_path)
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file"""
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
    
    def load_config(self) -> ETLConfig:
        """
        Load configuration from YAML file and environment variables
        
        Returns:
            ETLConfig: Validated configuration object
        """
        # Load from YAML
        yaml_config = self._load_yaml_config()
        
        # Override with environment variables
        env_config = self._load_env_config()
        
        # Merge configurations (env takes precedence)
        merged_config = {**yaml_config, **env_config}
        
        return ETLConfig(**merged_config)
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_mapping = {
            'RAW_DATA_PATH': 'raw_data_path',
            'PROCESSED_DATA_PATH': 'processed_data_path',
            'OUTPUT_DATA_PATH': 'output_data_path',
            'ENCODING': 'encoding',
            'CHUNK_SIZE': 'chunk_size',
            'MAX_WORKERS': 'max_workers',
        }
        
        config = {}
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert numeric values
                if config_key in ['chunk_size', 'max_workers']:
                    value = int(value)
                config[config_key] = value
        
        return config
    
    def get_project_root(self) -> Path:
        """Get the project root directory"""
        return Path(__file__).parent.parent.parent
    
    def resolve_path(self, relative_path: str) -> Path:
        """Resolve relative path from project root"""
        return self.get_project_root() / relative_path
