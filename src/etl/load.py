"""
ETL Load component following SOLID principles
Single Responsibility: Handle data loading to various destinations
"""
import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from ..utils import FileHandler, get_logger
from ..data_models import ETLMetadata

logger = get_logger(__name__)


class BaseLoader(ABC):
    """
    Abstract base class for data loaders
    Open/Closed: Easy to add new loading destinations
    """
    
    @abstractmethod
    def load(self, df: pd.DataFrame, destination: str, **kwargs) -> bool:
        """
        Load data to destination
        
        Args:
            df: DataFrame to load
            destination: Destination identifier
            **kwargs: Additional loading parameters
            
        Returns:
            bool: Success status
        """
        pass


class CSVLoader(BaseLoader):
    """
    Single Responsibility: Load data to CSV files
    """
    
    def __init__(self):
        self.file_handler = FileHandler()
    
    def load(self, df: pd.DataFrame, destination: str, **kwargs) -> bool:
        """
        Load data to CSV file
        
        Args:
            df: DataFrame to load
            destination: Path to output CSV file
            **kwargs: Additional pandas to_csv parameters
            
        Returns:
            bool: Success status
        """
        logger.info(f"Loading data to CSV: {destination}")
        
        try:
            # Default parameters
            default_params = {
                'index': False,
                'encoding': 'utf-8'
            }
            
            # Merge with user-provided parameters
            params = {**default_params, **kwargs}
            
            self.file_handler.save_csv(df, destination, **params)
            logger.info(f"Successfully loaded {len(df)} records to {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load data to {destination}: {e}")
            return False


class ParquetLoader(BaseLoader):
    """
    Single Responsibility: Load data to Parquet files
    """
    
    def __init__(self):
        self.file_handler = FileHandler()
    
    def load(self, df: pd.DataFrame, destination: str, **kwargs) -> bool:
        """
        Load data to Parquet file
        
        Args:
            df: DataFrame to load
            destination: Path to output Parquet file
            **kwargs: Additional pandas to_parquet parameters
            
        Returns:
            bool: Success status
        """
        logger.info(f"Loading data to Parquet: {destination}")
        
        try:
            # Default parameters
            default_params = {
                'index': False,
                'compression': 'snappy'
            }
            
            # Merge with user-provided parameters
            params = {**default_params, **kwargs}
            
            self.file_handler.save_parquet(df, destination, **params)
            logger.info(f"Successfully loaded {len(df)} records to {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load data to {destination}: {e}")
            return False


class DatabaseLoader(BaseLoader):
    """
    Single Responsibility: Load data to databases
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
    
    def load(self, df: pd.DataFrame, destination: str, **kwargs) -> bool:
        """
        Load data to database
        
        Args:
            df: DataFrame to load
            destination: Table name
            **kwargs: Additional parameters
            
        Returns:
            bool: Success status
        """
        logger.info(f"Loading data to database table: {destination}")
        
        # Implementation would depend on specific database
        # This is a placeholder for future database integration
        raise NotImplementedError("Database loading not yet implemented")


class LoaderFactory:
    """
    Factory pattern for creating loaders
    Single Responsibility: Create appropriate loader based on destination type
    """
    
    @staticmethod
    def create_loader(destination_type: str, **kwargs) -> BaseLoader:
        """
        Create appropriate loader based on destination type
        
        Args:
            destination_type: Type of destination ('csv', 'parquet', 'database', etc.)
            **kwargs: Additional loader parameters
            
        Returns:
            BaseLoader: Appropriate loader instance
        """
        loaders = {
            'csv': CSVLoader,
            'parquet': ParquetLoader,
            'database': DatabaseLoader,
        }
        
        if destination_type not in loaders:
            raise ValueError(f"Unsupported destination type: {destination_type}")
        
        return loaders[destination_type](**kwargs)


class MultiFormatLoader:
    """
    Single Responsibility: Load data to multiple formats simultaneously
    """
    
    def __init__(self, formats: Dict[str, str]):
        """
        Initialize with format configurations
        
        Args:
            formats: Dict mapping format names to file paths
        """
        self.formats = formats
    
    def load_all_formats(self, df: pd.DataFrame, base_name: str) -> Dict[str, bool]:
        """
        Load data to all configured formats
        
        Args:
            df: DataFrame to load
            base_name: Base name for output files
            
        Returns:
            Dict[str, bool]: Success status for each format
        """
        results = {}
        
        for format_name, base_path in self.formats.items():
            try:
                # Determine file extension and loader type
                if format_name.lower() == 'csv':
                    file_path = f"{base_path}/{base_name}.csv"
                    loader = LoaderFactory.create_loader('csv')
                elif format_name.lower() == 'parquet':
                    file_path = f"{base_path}/{base_name}.parquet"
                    loader = LoaderFactory.create_loader('parquet')
                else:
                    logger.warning(f"Unsupported format: {format_name}")
                    results[format_name] = False
                    continue
                
                # Load data
                success = loader.load(df, file_path)
                results[format_name] = success
                
            except Exception as e:
                logger.error(f"Failed to load {format_name} format: {e}")
                results[format_name] = False
        
        return results


class DataLoader:
    """
    Main loading orchestrator
    Single Responsibility: Orchestrate data loading process
    Dependency Inversion: Depends on abstraction (BaseLoader)
    """
    
    def __init__(self, metadata: Optional[ETLMetadata] = None):
        self.metadata = metadata
    
    def load_processed_data(
        self,
        df: pd.DataFrame,
        output_config: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Load processed data according to configuration
        
        Args:
            df: Processed DataFrame to load
            output_config: Configuration for output destinations
            
        Returns:
            Dict[str, bool]: Success status for each destination
        """
        logger.info("Starting data loading process")
        
        results = {}
        
        try:
            # Load to multiple formats if configured
            if 'formats' in output_config:
                multi_loader = MultiFormatLoader(output_config['formats'])
                base_name = output_config.get('base_name', 'sii_empresas_processed')
                format_results = multi_loader.load_all_formats(df, base_name)
                results.update(format_results)
            
            # Load to specific destinations
            if 'destinations' in output_config:
                for dest_config in output_config['destinations']:
                    dest_type = dest_config['type']
                    dest_path = dest_config['path']
                    dest_params = dest_config.get('params', {})
                    
                    loader = LoaderFactory.create_loader(dest_type, **dest_params)
                    success = loader.load(df, dest_path, **dest_params)
                    results[f"{dest_type}_{dest_path}"] = success
            
            # Update metadata
            if self.metadata:
                successful_loads = sum(1 for success in results.values() if success)
                total_loads = len(results)
                
                if successful_loads == total_loads:
                    self.metadata.status = "completed"
                elif successful_loads > 0:
                    self.metadata.status = "partially_completed"
                else:
                    self.metadata.status = "failed"
                    self.metadata.errors.append("All loading operations failed")
            
            logger.info(f"Data loading completed. Success rate: {sum(results.values())}/{len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            if self.metadata:
                self.metadata.errors.append(f"Loading error: {e}")
                self.metadata.status = "failed"
            raise
