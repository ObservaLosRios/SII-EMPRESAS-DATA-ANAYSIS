"""
ETL Extract component following SOLID principles
Single Responsibility: Handle data extraction from various sources
"""
import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from ..utils import FileHandler, get_logger
from ..data_models import ETLMetadata

logger = get_logger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for data extractors
    Open/Closed: Easy to add new data sources
    """
    
    @abstractmethod
    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Extract data from source
        
        Args:
            source: Data source identifier
            **kwargs: Additional extraction parameters
            
        Returns:
            pd.DataFrame: Extracted data
        """
        pass


class CSVExtractor(BaseExtractor):
    """
    Single Responsibility: Extract data from CSV files
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
        self.file_handler = FileHandler()
    
    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Extract data from CSV file
        
        Args:
            source: Path to CSV file
            **kwargs: Additional pandas read_csv parameters
            
        Returns:
            pd.DataFrame: Extracted data
        """
        logger.info(f"Extracting data from CSV: {source}")
        
        # Default parameters for CSV reading
        default_params = {
            'encoding': self.encoding,
            'low_memory': False
        }
        
        # Merge with user-provided parameters
        params = {**default_params, **kwargs}
        
        try:
            df = self.file_handler.read_csv(source, **params)
            logger.info(f"Successfully extracted {len(df)} records from {source}")
            return df
        except Exception as e:
            logger.error(f"Failed to extract data from {source}: {e}")
            raise


class DatabaseExtractor(BaseExtractor):
    """
    Single Responsibility: Extract data from databases
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
    
    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Extract data from database
        
        Args:
            source: SQL query or table name
            **kwargs: Additional parameters (connection, etc.)
            
        Returns:
            pd.DataFrame: Extracted data
        """
        logger.info(f"Extracting data from database: {source}")
        
        # Implementation would depend on specific database
        # This is a placeholder for future database integration
        raise NotImplementedError("Database extraction not yet implemented")


class ExtractorFactory:
    """
    Factory pattern for creating extractors
    Single Responsibility: Create appropriate extractor based on source type
    """
    
    @staticmethod
    def create_extractor(source_type: str, **kwargs) -> BaseExtractor:
        """
        Create appropriate extractor based on source type
        
        Args:
            source_type: Type of data source ('csv', 'database', etc.)
            **kwargs: Additional extractor parameters
            
        Returns:
            BaseExtractor: Appropriate extractor instance
        """
        extractors = {
            'csv': CSVExtractor,
            'database': DatabaseExtractor,
        }
        
        if source_type not in extractors:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        return extractors[source_type](**kwargs)


class DataExtractor:
    """
    Main extraction orchestrator
    Single Responsibility: Orchestrate data extraction process
    Dependency Inversion: Depends on abstraction (BaseExtractor)
    """
    
    def __init__(self, metadata: Optional[ETLMetadata] = None):
        self.metadata = metadata
    
    def extract_sii_data(
        self, 
        file_path: str, 
        source_type: str = 'csv',
        **kwargs
    ) -> pd.DataFrame:
        """
        Extract SII empresas data
        
        Args:
            file_path: Path to data file
            source_type: Type of data source
            **kwargs: Additional extraction parameters
            
        Returns:
            pd.DataFrame: Extracted data
        """
        logger.info("Starting SII data extraction")
        
        try:
            # Create appropriate extractor
            extractor = ExtractorFactory.create_extractor(source_type, **kwargs)
            
            # Extract data
            df = extractor.extract(file_path, **kwargs)
            
            # Update metadata if provided
            if self.metadata:
                self.metadata.records_processed = len(df)
            
            logger.info(f"Data extraction completed successfully: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            if self.metadata:
                self.metadata.errors.append(f"Extraction error: {e}")
            raise
