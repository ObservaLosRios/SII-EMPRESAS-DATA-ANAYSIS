"""
Tests for data models
"""
import pytest
from datetime import datetime
from src.data_models import EmpresaRecord, ETLMetadata, DataQualityReport


class TestEmpresaRecord:
    """Test EmpresaRecord data model"""
    
    def test_valid_empresa_record(self):
        """Test creation of valid empresa record"""
        record = EmpresaRecord(
            año_comercial=2020,
            comuna="Santiago",
            provincia="Santiago",
            region="RM",
            rubro_economico="A - Agricultura",
            numero_empresas=100,
            ventas_anuales_uf=1000000.0
        )
        
        assert record.año_comercial == 2020
        assert record.comuna == "Santiago"
        assert record.numero_empresas == 100
    
    def test_invalid_year(self):
        """Test validation of invalid year"""
        with pytest.raises(ValueError):
            EmpresaRecord(
                año_comercial=1999,  # Invalid year
                comuna="Santiago",
                provincia="Santiago", 
                region="RM",
                rubro_economico="A - Agricultura"
            )
    
    def test_empty_required_fields(self):
        """Test validation of empty required fields"""
        with pytest.raises(ValueError):
            EmpresaRecord(
                año_comercial=2020,
                comuna="",  # Empty comuna
                provincia="Santiago",
                region="RM", 
                rubro_economico="A - Agricultura"
            )
    
    def test_negative_numeric_values(self):
        """Test validation of negative numeric values"""
        with pytest.raises(ValueError):
            EmpresaRecord(
                año_comercial=2020,
                comuna="Santiago",
                provincia="Santiago",
                region="RM",
                rubro_economico="A - Agricultura",
                numero_empresas=-1  # Negative value
            )


class TestETLMetadata:
    """Test ETLMetadata model"""
    
    def test_etl_metadata_creation(self):
        """Test ETL metadata creation"""
        metadata = ETLMetadata(
            process_id="test-123",
            start_time=datetime.now()
        )
        
        assert metadata.process_id == "test-123"
        assert metadata.status == "running"
        assert metadata.records_processed == 0
    
    def test_metadata_updates(self):
        """Test metadata updates"""
        metadata = ETLMetadata(
            process_id="test-123",
            start_time=datetime.now()
        )
        
        metadata.records_processed = 1000
        metadata.status = "completed"
        
        assert metadata.records_processed == 1000
        assert metadata.status == "completed"


class TestDataQualityReport:
    """Test DataQualityReport model"""
    
    def test_quality_report_creation(self):
        """Test quality report creation"""
        report = DataQualityReport(
            total_records=1000,
            valid_records=950,
            invalid_records=50,
            null_percentage=0.05,
            duplicate_records=10,
            quality_score=0.85
        )
        
        assert report.total_records == 1000
        assert report.quality_score == 0.85
    
    def test_invalid_quality_score(self):
        """Test validation of invalid quality score"""
        with pytest.raises(ValueError):
            DataQualityReport(
                total_records=1000,
                valid_records=950,
                invalid_records=50,
                null_percentage=0.05,
                duplicate_records=10,
                quality_score=1.5  # Invalid score > 1
            )
