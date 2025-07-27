"""
Data Models for SII Empresas ETL Process
Following SOLID Principles and Clean Code practices
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class EmpresaRecord(BaseModel):
    """
    Single Responsibility: Define the structure and validation rules 
    for a single empresa record from SII data
    """
    año_comercial: int = Field(..., ge=2005, le=2030, description="Commercial year")
    comuna: str = Field(..., min_length=1, description="Municipality")
    provincia: str = Field(..., min_length=1, description="Province")
    region: str = Field(..., min_length=1, description="Region")
    rubro_economico: str = Field(..., min_length=1, description="Economic sector")
    
    # Company metrics
    numero_empresas: Optional[int] = Field(None, ge=0, description="Number of companies")
    ventas_anuales_uf: Optional[float] = Field(None, ge=0, description="Annual sales in UF")
    
    # Employee metrics - Total
    numero_trabajadores_dependientes: Optional[int] = Field(None, ge=0)
    renta_neta_uf: Optional[float] = Field(None, ge=0)
    trabajadores_ponderados_meses: Optional[float] = Field(None, ge=0)
    
    # Employee metrics - Female
    numero_trabajadores_femenino: Optional[int] = Field(None, ge=0)
    renta_neta_femenino_uf: Optional[float] = Field(None, ge=0)
    trabajadores_femenino_ponderados: Optional[float] = Field(None, ge=0)
    
    # Employee metrics - Male
    numero_trabajadores_masculino: Optional[int] = Field(None, ge=0)
    renta_neta_masculino_uf: Optional[float] = Field(None, ge=0)
    trabajadores_masculino_ponderados: Optional[float] = Field(None, ge=0)
    
    # Contractor metrics - Total
    numero_trabajadores_honorarios: Optional[int] = Field(None, ge=0)
    honorarios_pagados_uf: Optional[float] = Field(None, ge=0)
    trabajadores_honorarios_ponderados: Optional[float] = Field(None, ge=0)
    
    # Contractor metrics - Female
    numero_trabajadores_honorarios_femenino: Optional[int] = Field(None, ge=0)
    honorarios_femenino_uf: Optional[float] = Field(None, ge=0)
    trabajadores_honorarios_femenino_ponderados: Optional[float] = Field(None, ge=0)
    
    # Contractor metrics - Male
    numero_trabajadores_honorarios_masculino: Optional[int] = Field(None, ge=0)
    honorarios_masculino_uf: Optional[float] = Field(None, ge=0)
    trabajadores_honorarios_masculino_ponderados: Optional[float] = Field(None, ge=0)

    @validator('rubro_economico')
    def validate_rubro_economico(cls, v):
        """Validate economic sector format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Economic sector cannot be empty')
        return v.strip()

    @validator('region')
    def validate_region(cls, v):
        """Validate region name"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Region cannot be empty')
        return v.strip()

    class Config:
        """Pydantic configuration"""
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"


class ETLMetadata(BaseModel):
    """
    Single Responsibility: Track ETL process metadata
    """
    process_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    records_processed: int = 0
    records_failed: int = 0
    errors: list = []
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True


class DataQualityReport(BaseModel):
    """
    Single Responsibility: Define data quality metrics and thresholds
    """
    total_records: int
    valid_records: int
    invalid_records: int
    null_percentage: float
    duplicate_records: int
    quality_score: float
    issues: list = []
    
    @validator('quality_score')
    def validate_quality_score(cls, v):
        """Ensure quality score is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError('Quality score must be between 0 and 1')
        return v
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True
