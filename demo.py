#!/usr/bin/env python3
"""
Demo script to showcase the SII Empresas ETL system
This script demonstrates the complete functionality of our Clean Code & SOLID ETL pipeline
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.etl import ETLPipeline
from src.utils import setup_project_logging, get_logger
import pandas as pd

def main():
    """Main demo function"""
    print("🚀 SII EMPRESAS ETL SYSTEM DEMO")
    print("=" * 60)
    print("Demonstrating Clean Code & SOLID principles in action!")
    print("")
    
    # Setup logging
    setup_project_logging(log_level='INFO')
    logger = get_logger(__name__)
    
    try:
        # 1. Initialize pipeline
        print("1️⃣  INITIALIZING ETL PIPELINE")
        print("-" * 40)
        pipeline = ETLPipeline("config/etl_config.yaml")
        print(f"✅ Pipeline initialized: {pipeline.metadata.process_id}")
        print("")
        
        # 2. Extract data
        print("2️⃣  EXTRACTING DATA")
        print("-" * 40)
        raw_data = pipeline.run_extract_only()
        print(f"✅ Extracted {len(raw_data):,} records")
        print(f"📊 Data shape: {raw_data.shape}")
        print(f"📋 Columns: {list(raw_data.columns[:5])}...")
        print("")
        
        # 3. Transform data
        print("3️⃣  TRANSFORMING DATA")
        print("-" * 40)
        transformed_data = pipeline.run_transform_only(raw_data)
        print(f"✅ Transformed to {len(transformed_data):,} records")
        print(f"📊 New shape: {transformed_data.shape}")
        print("🔧 Transformations applied:")
        print("   - Column standardization")
        print("   - Data type conversion")
        print("   - Data cleaning")
        print("   - Feature engineering")
        print("")
        
        # 4. Validate data
        print("4️⃣  VALIDATING DATA QUALITY")
        print("-" * 40)
        quality_report = pipeline.run_validation_only(transformed_data)
        print(f"✅ Quality score: {quality_report.quality_score:.1%}")
        print(f"📊 Total records: {quality_report.total_records:,}")
        print(f"🔍 Valid records: {quality_report.valid_records:,}")
        print(f"⚠️  Issues found: {len(quality_report.issues)}")
        print("")
        
        # 5. Display sample insights
        print("5️⃣  BUSINESS INSIGHTS PREVIEW")
        print("-" * 40)
        
        # Basic statistics
        if 'numero_empresas' in transformed_data.columns:
            total_companies = transformed_data['numero_empresas'].sum()
            print(f"🏢 Total companies: {total_companies:,}")
        
        if 'region' in transformed_data.columns:
            regions = transformed_data['region'].nunique()
            print(f"🌍 Regions covered: {regions}")
        
        if 'año_comercial' in transformed_data.columns:
            years = transformed_data['año_comercial'].nunique()
            year_range = f"{transformed_data['año_comercial'].min()}-{transformed_data['año_comercial'].max()}"
            print(f"📅 Years covered: {years} ({year_range})")
        
        if 'numero_trabajadores_dependientes' in transformed_data.columns:
            total_workers = transformed_data['numero_trabajadores_dependientes'].sum()
            print(f"👥 Total workers: {total_workers:,}")
        
        print("")
        
        # 6. Show derived features
        print("6️⃣  DERIVED FEATURES")
        print("-" * 40)
        derived_features = [col for col in transformed_data.columns 
                          if col in ['salario_promedio_uf', 'ratio_femenino', 'categoria_empresa', 'codigo_sector']]
        
        for feature in derived_features:
            print(f"🔧 {feature}: Available")
        
        print("")
        
        # 7. Architecture demonstration
        print("7️⃣  ARCHITECTURE PRINCIPLES DEMONSTRATED")
        print("-" * 40)
        print("✅ Single Responsibility: Each class has one clear purpose")
        print("✅ Open/Closed: Easy to extend with new transformations")
        print("✅ Liskov Substitution: Components are interchangeable")
        print("✅ Interface Segregation: Clean, specific interfaces")
        print("✅ Dependency Inversion: Depends on abstractions")
        print("")
        print("🧹 Clean Code Practices:")
        print("   - Meaningful variable names")
        print("   - Small, focused functions")
        print("   - Comprehensive error handling")
        print("   - Extensive logging")
        print("   - Type hints throughout")
        print("   - Comprehensive documentation")
        print("")
        
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Your ETL system is ready for production use!")
        print("📚 Next steps:")
        print("   1. Run: python main.py (full pipeline)")
        print("   2. Open: notebooks/sii_empresas_analysis.ipynb")
        print("   3. Explore: data/processed/ folder")
        print("   4. Check: logs/ folder for detailed logs")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
