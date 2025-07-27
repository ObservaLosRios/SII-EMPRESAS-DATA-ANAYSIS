"""
Test configuration and fixtures
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def sample_raw_data():
    """Sample raw SII data for testing"""
    return pd.DataFrame({
        '﻿Año Comercial': [2020, 2020, 2021],
        'Comuna del domicilio o casa matriz': ['Santiago', 'Valparaíso', 'Concepción'],
        'Provincia del domicilio o casa matriz': ['Santiago', 'Valparaíso', 'Concepción'],
        'Region del domicilio o casa matriz': ['RM', 'V Región', 'VIII Región'],
        'Rubro economico': ['A - Agricultura', 'B - Minería', 'C - Manufactura'],
        'Número de empresas': [100, 50, 75],
        'Ventas anuales en UF': ['1,000,000', '500,000', '750,000'],
        'Número de trabajadores dependientes informados': [1000, 500, 750],
        'Renta neta informada en UF': ['100,000', '50,000', '75,000']
    })


@pytest.fixture
def sample_transformed_data():
    """Sample transformed data for testing"""
    return pd.DataFrame({
        'año_comercial': [2020, 2020, 2021],
        'comuna': ['Santiago', 'Valparaíso', 'Concepción'],
        'provincia': ['Santiago', 'Valparaíso', 'Concepción'],
        'region': ['RM', 'V Región', 'VIII Región'],
        'rubro_economico': ['A - Agricultura', 'B - Minería', 'C - Manufactura'],
        'numero_empresas': [100, 50, 75],
        'ventas_anuales_uf': [1000000.0, 500000.0, 750000.0],
        'numero_trabajadores_dependientes': [1000, 500, 750],
        'renta_neta_uf': [100000.0, 50000.0, 75000.0]
    })


@pytest.fixture
def temp_csv_file(sample_raw_data):
    """Create temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_raw_data.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_directory():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
