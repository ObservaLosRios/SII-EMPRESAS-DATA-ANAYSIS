"""
File handling utilities following SOLID principles
Single Responsibility: Handle file operations and data I/O
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
from ..utils.logging import get_logger

logger = get_logger(__name__)


class FileHandler:
    """
    Single Responsibility: Handle file I/O operations
    Open/Closed: Easy to extend with new file formats
    """
    
    @staticmethod
    def read_csv(
        file_path: str,
        encoding: str = 'utf-8',
        **kwargs
    ) -> pd.DataFrame:
        """
        Read CSV file with error handling
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            **kwargs: Additional pandas read_csv parameters
            
        Returns:
            pd.DataFrame: Loaded DataFrame
        """
        try:
            logger.info(f"Reading CSV file: {file_path}")
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            logger.info(f"Successfully loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise
    
    @staticmethod
    def save_csv(
        df: pd.DataFrame,
        file_path: str,
        index: bool = False,
        **kwargs
    ) -> None:
        """
        Save DataFrame to CSV with error handling
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            index: Whether to include index
            **kwargs: Additional pandas to_csv parameters
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Saving {len(df)} records to {file_path}")
            df.to_csv(file_path, index=index, **kwargs)
            logger.info(f"Successfully saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving CSV file {file_path}: {e}")
            raise
    
    @staticmethod
    def save_parquet(
        df: pd.DataFrame,
        file_path: str,
        **kwargs
    ) -> None:
        """
        Save DataFrame to Parquet format
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            **kwargs: Additional pandas to_parquet parameters
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Saving {len(df)} records to {file_path} (Parquet)")
            df.to_parquet(file_path, **kwargs)
            logger.info(f"Successfully saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving Parquet file {file_path}: {e}")
            raise


class DataTypeConverter:
    """
    Single Responsibility: Handle data type conversions
    """
    
    @staticmethod
    def clean_numeric_string(value: str) -> str:
        """
        Clean numeric string by removing common formatting
        
        Args:
            value: String value to clean
            
        Returns:
            str: Cleaned string
        """
        if pd.isna(value) or value == '*':
            return None
        
        # Remove quotes and clean formatting
        cleaned = str(value).replace('"', '').replace(',', '').replace('.', '')
        
        # Handle empty strings
        if cleaned.strip() == '':
            return None
            
        return cleaned
    
    @staticmethod
    def convert_to_numeric(
        series: pd.Series,
        errors: str = 'coerce'
    ) -> pd.Series:
        """
        Convert series to numeric, handling common formatting issues
        
        Args:
            series: Pandas series to convert
            errors: How to handle conversion errors
            
        Returns:
            pd.Series: Converted series
        """
        # Clean string formatting
        if series.dtype == 'object':
            series = series.astype(str).str.replace('"', '')
            series = series.str.replace(',', '')
            series = series.replace('*', np.nan)
        
        return pd.to_numeric(series, errors=errors)
    
    @staticmethod
    def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names following Python naming conventions
        
        Args:
            df: DataFrame with columns to standardize
            
        Returns:
            pd.DataFrame: DataFrame with standardized column names
        """
        column_mapping = {
            '﻿Año Comercial': 'año_comercial',
            'Comuna del domicilio o casa matriz': 'comuna',
            'Provincia del domicilio o casa matriz': 'provincia',
            'Region del domicilio o casa matriz': 'region',
            'Rubro economico': 'rubro_economico',
            'Número de empresas': 'numero_empresas',
            'Ventas anuales en UF': 'ventas_anuales_uf',
            'Número de trabajadores dependientes informados': 'numero_trabajadores_dependientes',
            'Renta neta informada en UF': 'renta_neta_uf',
            'Trabajadores ponderados por meses trabajados': 'trabajadores_ponderados_meses',
            'Número de trabajadores dependientes de género femenino informados': 'numero_trabajadores_femenino',
            'Renta neta informada en UF, trabajadores de género femenino': 'renta_neta_femenino_uf',
            'Trabajadores de género femenino ponderados por meses trabajados': 'trabajadores_femenino_ponderados',
            'Número de trabajadores dependientes de género masculino informados': 'numero_trabajadores_masculino',
            'Renta neta informada en UF, trabajadores de género masculino': 'renta_neta_masculino_uf',
            'Trabajadores de género masculino ponderados por meses trabajados': 'trabajadores_masculino_ponderados',
            'Número de trabajadores a honorarios informados': 'numero_trabajadores_honorarios',
            'Honorarios pagados informados en UF': 'honorarios_pagados_uf',
            'Trabajadores a honorarios ponderados por meses trabajados': 'trabajadores_honorarios_ponderados',
            'Número de trabajadores a honorarios de género femenino informados': 'numero_trabajadores_honorarios_femenino',
            'Honorarios pagados informados a trabajadores de género femenino en UF': 'honorarios_femenino_uf',
            'Trabajadores a honorarios de género femenino ponderados por meses trabajados': 'trabajadores_honorarios_femenino_ponderados',
            'Número de trabajadores a honorarios de género masculino informados': 'numero_trabajadores_honorarios_masculino',
            'Honorarios pagados informados a trabajadores de género masculino en UF': 'honorarios_masculino_uf',
            'Trabajadores a honorarios de género masculino ponderados por meses trabajados': 'trabajadores_honorarios_masculino_ponderados'
        }
        
        # Rename columns that exist in the mapping
        existing_columns = {col: column_mapping[col] for col in df.columns if col in column_mapping}
        df_renamed = df.rename(columns=existing_columns)
        
        logger.info(f"Standardized {len(existing_columns)} column names")
        return df_renamed
