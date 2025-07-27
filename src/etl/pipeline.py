"""
Main ETL Pipeline orchestrator following SOLID principles
Single Responsibility: Orchestrate the complete ETL process
Dependency Inversion: Depends on abstractions, not concretions
"""
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .extract import DataExtractor
from .transform import create_standard_pipeline
from .load import DataLoader
from ..validators import (
    SchemaValidator,
    DataQualityValidator, 
    BusinessRuleValidator,
    DataValidationPipeline
)
from ..data_models import ETLMetadata, DataQualityReport
from ..utils import ConfigManager, setup_project_logging, get_logger

logger = get_logger(__name__)


class ETLPipeline:
    """
    Main ETL Pipeline class
    Single Responsibility: Orchestrate complete ETL process
    Open/Closed: Easy to extend with new components
    Dependency Inversion: Depends on abstractions
    """
    
    def __init__(self, config_path: str = "config/etl_config.yaml"):
        """
        Initialize ETL Pipeline
        
        Args:
            config_path: Path to configuration file
        """
        # Setup logging
        setup_project_logging()
        
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        
        # Initialize metadata
        self.metadata = ETLMetadata(
            process_id=str(uuid.uuid4()),
            start_time=datetime.now()
        )
        
        # Initialize components
        self.extractor = DataExtractor(self.metadata)
        self.transformer = create_standard_pipeline()
        self.transformer.metadata = self.metadata
        self.loader = DataLoader(self.metadata)
        
        # Initialize validators
        expected_columns = [
            'año_comercial', 'comuna', 'provincia', 'region', 'rubro_economico',
            'numero_empresas', 'ventas_anuales_uf', 'numero_trabajadores_dependientes',
            'renta_neta_uf', 'trabajadores_ponderados_meses'
        ]
        
        self.validators = DataValidationPipeline([
            SchemaValidator(expected_columns),
            DataQualityValidator(max_null_percentage=0.3),
            BusinessRuleValidator(min_year=2005, max_year=2024)
        ])
        
        logger.info(f"ETL Pipeline initialized with process ID: {self.metadata.process_id}")
    
    def run_full_pipeline(
        self, 
        input_file: Optional[str] = None,
        validate_data: bool = True,
        save_intermediates: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline
        
        Args:
            input_file: Path to input data file (optional, uses config if not provided)
            validate_data: Whether to run data validation
            save_intermediates: Whether to save intermediate results
            
        Returns:
            Dict with pipeline results and metadata
        """
        logger.info("Starting ETL pipeline execution")
        
        try:
            # 1. EXTRACT
            logger.info("=== EXTRACT PHASE ===")
            input_path = input_file or self.config.raw_data_path
            raw_data = self.extractor.extract_sii_data(
                file_path=self._resolve_path(input_path),
                source_type='csv'
            )
            
            if save_intermediates:
                self._save_intermediate(raw_data, "01_raw_data.csv")
            
            # 2. TRANSFORM  
            logger.info("=== TRANSFORM PHASE ===")
            transformed_data = self.transformer.run_transformations(raw_data)
            
            if save_intermediates:
                self._save_intermediate(transformed_data, "02_transformed_data.csv")
            
            # 3. VALIDATE (optional)
            quality_report = None
            if validate_data:
                logger.info("=== VALIDATION PHASE ===")
                quality_report = self.validators.run_validation(transformed_data)
                
                if save_intermediates:
                    self._save_quality_report(quality_report)
                
                # Log quality issues
                if quality_report.issues:
                    logger.warning(f"Data quality issues found: {len(quality_report.issues)}")
                    for issue in quality_report.issues[:5]:  # Log first 5 issues
                        logger.warning(f"  - {issue}")
            
            # 4. LOAD
            logger.info("=== LOAD PHASE ===")
            output_config = self._create_output_config()
            load_results = self.loader.load_processed_data(transformed_data, output_config)
            
            # Update final metadata
            self.metadata.end_time = datetime.now()
            if all(load_results.values()):
                self.metadata.status = "completed"
            else:
                self.metadata.status = "completed_with_warnings"
            
            # Prepare results
            results = {
                'metadata': self.metadata,
                'quality_report': quality_report,
                'load_results': load_results,
                'final_data_shape': transformed_data.shape,
                'process_duration': (self.metadata.end_time - self.metadata.start_time).total_seconds()
            }
            
            logger.info(f"ETL pipeline completed successfully in {results['process_duration']:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            self.metadata.end_time = datetime.now()
            self.metadata.status = "failed"
            self.metadata.errors.append(str(e))
            raise
    
    def run_extract_only(self, input_file: Optional[str] = None):
        """Run only the extract phase"""
        logger.info("Running extract-only pipeline")
        
        input_path = input_file or self.config.raw_data_path
        return self.extractor.extract_sii_data(
            file_path=self._resolve_path(input_path),
            source_type='csv'
        )
    
    def run_transform_only(self, data):
        """Run only the transform phase"""
        logger.info("Running transform-only pipeline")
        return self.transformer.run_transformations(data)
    
    def run_validation_only(self, data):
        """Run only the validation phase"""
        logger.info("Running validation-only pipeline")
        return self.validators.run_validation(data)
    
    def _resolve_path(self, path: str) -> str:
        """Resolve relative paths from project root"""
        if Path(path).is_absolute():
            return path
        return str(self.config_manager.resolve_path(path))
    
    def _create_output_config(self) -> Dict[str, Any]:
        """Create output configuration for loading"""
        project_root = self.config_manager.get_project_root()
        
        return {
            'formats': {
                'csv': str(project_root / "data/processed"),
                'parquet': str(project_root / "data/processed")
            },
            'base_name': f"sii_empresas_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    
    def _save_intermediate(self, data, filename: str):
        """Save intermediate data for debugging"""
        output_path = self.config_manager.get_project_root() / "data/processed" / filename
        data.to_csv(output_path, index=False)
        logger.info(f"Saved intermediate data: {output_path}")
    
    def _save_quality_report(self, report: DataQualityReport):
        """Save quality report"""
        output_path = self.config_manager.get_project_root() / "data/processed" / "quality_report.json"
        
        # Convert to dict and save
        report_dict = report.dict()
        
        import json
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info(f"Saved quality report: {output_path}")


def run_etl_pipeline(
    config_path: str = "config/etl_config.yaml",
    input_file: Optional[str] = None,
    validate_data: bool = True,
    save_intermediates: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to run ETL pipeline
    
    Args:
        config_path: Path to configuration file
        input_file: Path to input data file
        validate_data: Whether to run data validation  
        save_intermediates: Whether to save intermediate results
        
    Returns:
        Dict with pipeline results and metadata
    """
    pipeline = ETLPipeline(config_path)
    return pipeline.run_full_pipeline(
        input_file=input_file,
        validate_data=validate_data,
        save_intermediates=save_intermediates
    )
