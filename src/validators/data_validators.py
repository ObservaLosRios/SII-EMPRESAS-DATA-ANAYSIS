"""
Data validators following SOLID principles
Open/Closed: Easy to add new validation rules
Single Responsibility: Each validator has a specific purpose
"""
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..data_models import DataQualityReport
from ..utils.logging import get_logger

logger = get_logger(__name__)


class BaseValidator(ABC):
    """
    Abstract base class for validators
    Open/Closed: Easy to extend with new validators
    """
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame and return validation results
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dict containing validation results
        """
        pass


class SchemaValidator(BaseValidator):
    """
    Single Responsibility: Validate DataFrame schema
    """
    
    def __init__(self, expected_columns: List[str]):
        self.expected_columns = expected_columns
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate DataFrame schema"""
        issues = []
        
        # Check for missing columns
        missing_columns = set(self.expected_columns) - set(df.columns)
        if missing_columns:
            issues.append(f"Missing columns: {missing_columns}")
        
        # Check for extra columns
        extra_columns = set(df.columns) - set(self.expected_columns)
        if extra_columns:
            issues.append(f"Extra columns: {extra_columns}")
        
        is_valid = len(issues) == 0
        
        return {
            'validator': 'SchemaValidator',
            'is_valid': is_valid,
            'issues': issues,
            'missing_columns': list(missing_columns),
            'extra_columns': list(extra_columns)
        }


class DataQualityValidator(BaseValidator):
    """
    Single Responsibility: Validate data quality metrics
    """
    
    def __init__(self, max_null_percentage: float = 0.1):
        self.max_null_percentage = max_null_percentage
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data quality"""
        issues = []
        
        # Calculate null percentages
        null_percentages = df.isnull().sum() / len(df)
        high_null_columns = null_percentages[null_percentages > self.max_null_percentage]
        
        if not high_null_columns.empty:
            issues.append(f"High null percentage in columns: {high_null_columns.to_dict()}")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate rows")
        
        # Check for empty DataFrame
        if len(df) == 0:
            issues.append("DataFrame is empty")
        
        is_valid = len(issues) == 0
        
        return {
            'validator': 'DataQualityValidator',
            'is_valid': is_valid,
            'issues': issues,
            'null_percentages': null_percentages.to_dict(),
            'duplicate_count': duplicates,
            'total_records': len(df)
        }


class BusinessRuleValidator(BaseValidator):
    """
    Single Responsibility: Validate business-specific rules
    """
    
    def __init__(self, min_year: int = 2005, max_year: int = 2024):
        self.min_year = min_year
        self.max_year = max_year
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate business rules"""
        issues = []
        
        # Validate year range
        if 'año_comercial' in df.columns:
            year_col = df['año_comercial']
            invalid_years = year_col[
                (year_col < self.min_year) | (year_col > self.max_year)
            ].dropna()
            
            if not invalid_years.empty:
                issues.append(f"Invalid years found: {invalid_years.unique()}")
        
        # Validate negative values in numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col.startswith(('numero_', 'ventas_', 'renta_', 'honorarios_')):
                negative_values = df[df[col] < 0][col].dropna()
                if not negative_values.empty:
                    issues.append(f"Negative values in {col}: {len(negative_values)} records")
        
        # Validate required categorical fields
        categorical_required = ['comuna', 'provincia', 'region', 'rubro_economico']
        for col in categorical_required:
            if col in df.columns:
                empty_values = df[col].isna() | (df[col].str.strip() == '')
                if empty_values.any():
                    issues.append(f"Empty values in required field {col}: {empty_values.sum()} records")
        
        is_valid = len(issues) == 0
        
        return {
            'validator': 'BusinessRuleValidator',
            'is_valid': is_valid,
            'issues': issues
        }


class DataValidationPipeline:
    """
    Single Responsibility: Orchestrate multiple validators
    Dependency Inversion: Depends on abstractions (BaseValidator)
    """
    
    def __init__(self, validators: List[BaseValidator]):
        self.validators = validators
    
    def run_validation(self, df: pd.DataFrame) -> DataQualityReport:
        """
        Run all validators and generate comprehensive report
        
        Args:
            df: DataFrame to validate
            
        Returns:
            DataQualityReport: Comprehensive validation report
        """
        logger.info("Starting data validation pipeline")
        
        all_issues = []
        validation_results = []
        
        # Run all validators
        for validator in self.validators:
            try:
                result = validator.validate(df)
                validation_results.append(result)
                
                if not result['is_valid']:
                    all_issues.extend(result['issues'])
                    
                logger.info(f"{result['validator']}: {'PASSED' if result['is_valid'] else 'FAILED'}")
            except Exception as e:
                error_msg = f"Validator {validator.__class__.__name__} failed: {e}"
                logger.error(error_msg)
                all_issues.append(error_msg)
        
        # Calculate quality metrics
        total_records = len(df)
        null_count = df.isnull().sum().sum()
        duplicate_count = df.duplicated().sum()
        
        # Calculate quality score (0-1)
        quality_score = self._calculate_quality_score(
            total_records, null_count, duplicate_count, len(all_issues)
        )
        
        report = DataQualityReport(
            total_records=total_records,
            valid_records=total_records - duplicate_count,
            invalid_records=duplicate_count,
            null_percentage=null_count / (total_records * len(df.columns)) if total_records > 0 else 0,
            duplicate_records=duplicate_count,
            quality_score=quality_score,
            issues=all_issues
        )
        
        logger.info(f"Validation completed. Quality score: {quality_score:.2f}")
        return report
    
    def _calculate_quality_score(
        self, 
        total_records: int, 
        null_count: int, 
        duplicate_count: int, 
        issue_count: int
    ) -> float:
        """Calculate overall data quality score"""
        if total_records == 0:
            return 0.0
        
        # Base score
        score = 1.0
        
        # Penalize for nulls (max 20% penalty)
        null_penalty = min(0.2, (null_count / total_records) * 0.5)
        score -= null_penalty
        
        # Penalize for duplicates (max 15% penalty)
        duplicate_penalty = min(0.15, (duplicate_count / total_records) * 0.3)
        score -= duplicate_penalty
        
        # Penalize for validation issues (max 30% penalty)
        issue_penalty = min(0.3, issue_count * 0.05)
        score -= issue_penalty
        
        return max(0.0, score)
