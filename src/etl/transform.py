"""
ETL Transform component following SOLID principles
Single Responsibility: Handle data transformation and cleaning
"""
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..utils import DataTypeConverter, get_logger
from ..data_models import ETLMetadata

logger = get_logger(__name__)


class BaseTransformer(ABC):
    """
    Abstract base class for transformers
    Open/Closed: Easy to add new transformation rules
    """
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Transformed DataFrame
        """
        pass


class ColumnStandardizer(BaseTransformer):
    """
    Single Responsibility: Standardize column names and structure
    """
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        logger.info("Standardizing column names")
        
        converter = DataTypeConverter()
        df_transformed = converter.standardize_column_names(df.copy())
        
        logger.info("Column standardization completed")
        return df_transformed


class DataTypeTransformer(BaseTransformer):
    """
    Single Responsibility: Convert data types appropriately
    """
    
    def __init__(self):
        self.converter = DataTypeConverter()
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data types"""
        logger.info("Starting data type transformation")
        df_transformed = df.copy()
        
        # Define numeric columns
        numeric_columns = [
            'numero_empresas', 'ventas_anuales_uf', 'numero_trabajadores_dependientes',
            'renta_neta_uf', 'trabajadores_ponderados_meses', 'numero_trabajadores_femenino',
            'renta_neta_femenino_uf', 'trabajadores_femenino_ponderados',
            'numero_trabajadores_masculino', 'renta_neta_masculino_uf',
            'trabajadores_masculino_ponderados', 'numero_trabajadores_honorarios',
            'honorarios_pagados_uf', 'trabajadores_honorarios_ponderados',
            'numero_trabajadores_honorarios_femenino', 'honorarios_femenino_uf',
            'trabajadores_honorarios_femenino_ponderados',
            'numero_trabajadores_honorarios_masculino', 'honorarios_masculino_uf',
            'trabajadores_honorarios_masculino_ponderados'
        ]
        
        # Convert numeric columns
        for col in numeric_columns:
            if col in df_transformed.columns:
                try:
                    df_transformed[col] = self.converter.convert_to_numeric(df_transformed[col])
                    logger.debug(f"Converted {col} to numeric")
                except Exception as e:
                    logger.warning(f"Failed to convert {col} to numeric: {e}")
        
        # Convert year to integer
        if 'año_comercial' in df_transformed.columns:
            df_transformed['año_comercial'] = pd.to_numeric(
                df_transformed['año_comercial'], errors='coerce'
            ).astype('Int64')
        
        # Clean categorical columns
        categorical_columns = ['comuna', 'provincia', 'region', 'rubro_economico']
        for col in categorical_columns:
            if col in df_transformed.columns:
                df_transformed[col] = df_transformed[col].astype(str).str.strip()
                df_transformed[col] = df_transformed[col].replace('nan', np.nan)
        
        logger.info("Data type transformation completed")
        return df_transformed


class DataCleaner(BaseTransformer):
    """
    Single Responsibility: Clean and handle missing data
    """
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data"""
        logger.info("Starting data cleaning")
        df_cleaned = df.copy()
        
        # Remove completely empty rows
        df_cleaned = df_cleaned.dropna(how='all')
        
        # Handle asterisks (*) in data - convert to NaN
        df_cleaned = df_cleaned.replace('*', np.nan)
        
        # Remove rows where all key fields are missing
        key_fields = ['comuna', 'provincia', 'region', 'rubro_economico']
        available_key_fields = [col for col in key_fields if col in df_cleaned.columns]
        
        if available_key_fields:
            df_cleaned = df_cleaned.dropna(subset=available_key_fields, how='all')
        
        # Clean text fields
        text_columns = df_cleaned.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col in ['comuna', 'provincia', 'region', 'rubro_economico']:
                # Remove extra whitespace and standardize
                df_cleaned[col] = df_cleaned[col].str.strip()
                df_cleaned[col] = df_cleaned[col].str.replace(r'\s+', ' ', regex=True)
        
        logger.info(f"Data cleaning completed. Records: {len(df)} -> {len(df_cleaned)}")
        return df_cleaned


class FeatureEngineer(BaseTransformer):
    """
    Single Responsibility: Create derived features
    """
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer new features"""
        logger.info("Starting feature engineering")
        df_enhanced = df.copy()
        
        # Calculate average salary per employee (if data available)
        if all(col in df_enhanced.columns for col in ['renta_neta_uf', 'numero_trabajadores_dependientes']):
            df_enhanced['salario_promedio_uf'] = (
                df_enhanced['renta_neta_uf'] / df_enhanced['numero_trabajadores_dependientes']
            ).replace([np.inf, -np.inf], np.nan)
        
        # Calculate gender ratios
        if all(col in df_enhanced.columns for col in ['numero_trabajadores_femenino', 'numero_trabajadores_masculino']):
            total_gendered = df_enhanced['numero_trabajadores_femenino'].fillna(0) + df_enhanced['numero_trabajadores_masculino'].fillna(0)
            df_enhanced['ratio_femenino'] = (
                df_enhanced['numero_trabajadores_femenino'] / total_gendered
            ).replace([np.inf, -np.inf], np.nan)
        
        # Create size categories based on number of employees
        if 'numero_trabajadores_dependientes' in df_enhanced.columns:
            df_enhanced['categoria_empresa'] = pd.cut(
                df_enhanced['numero_trabajadores_dependientes'],
                bins=[0, 10, 50, 200, np.inf],
                labels=['Micro', 'Pequeña', 'Mediana', 'Grande'],
                include_lowest=True
            )
        
        # Extract sector code from economic activity
        if 'rubro_economico' in df_enhanced.columns:
            df_enhanced['codigo_sector'] = df_enhanced['rubro_economico'].str.extract(r'^([A-Z])')
        
        logger.info("Feature engineering completed")
        return df_enhanced


class TransformationPipeline:
    """
    Single Responsibility: Orchestrate transformation pipeline
    Dependency Inversion: Depends on abstractions (BaseTransformer)
    """
    
    def __init__(self, transformers: List[BaseTransformer], metadata: Optional[ETLMetadata] = None):
        self.transformers = transformers
        self.metadata = metadata
    
    def run_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run all transformations in sequence
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Fully transformed DataFrame
        """
        logger.info("Starting transformation pipeline")
        
        current_df = df.copy()
        
        try:
            for i, transformer in enumerate(self.transformers):
                logger.info(f"Running transformer {i+1}/{len(self.transformers)}: {transformer.__class__.__name__}")
                
                previous_shape = current_df.shape
                current_df = transformer.transform(current_df)
                current_shape = current_df.shape
                
                logger.info(f"Transformation completed. Shape: {previous_shape} -> {current_shape}")
            
            if self.metadata:
                self.metadata.records_processed = len(current_df)
            
            logger.info("Transformation pipeline completed successfully")
            return current_df
            
        except Exception as e:
            logger.error(f"Transformation pipeline failed: {e}")
            if self.metadata:
                self.metadata.errors.append(f"Transformation error: {e}")
            raise


def create_standard_pipeline() -> TransformationPipeline:
    """
    Factory function to create standard transformation pipeline
    
    Returns:
        TransformationPipeline: Configured pipeline
    """
    transformers = [
        ColumnStandardizer(),
        DataTypeTransformer(),
        DataCleaner(),
        FeatureEngineer()
    ]
    
    return TransformationPipeline(transformers)
