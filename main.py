#!/usr/bin/env python3
"""
SII Empresas Data Analysis - ETL Pipeline
Main entry point for the ETL process

This script demonstrates Clean Code and SOLID principles:
- Single Responsibility: Each function has one clear purpose
- Open/Closed: Easy to extend with new features
- Liskov Substitution: Components can be substituted
- Interface Segregation: Clean interfaces for each component
- Dependency Inversion: Depends on abstractions
"""
import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.etl import run_etl_pipeline
from src.utils import setup_project_logging, get_logger

logger = get_logger(__name__)


def main():
    """
    Main entry point for ETL pipeline
    Single Responsibility: Parse arguments and orchestrate pipeline execution
    """
    parser = argparse.ArgumentParser(
        description="SII Empresas Data Analysis ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Run full pipeline with default settings
  python main.py --input data/raw/custom.csv       # Use custom input file
  python main.py --no-validation                   # Skip data validation
  python main.py --save-intermediates              # Save intermediate results
  python main.py --config config/custom.yaml      # Use custom configuration
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Path to input CSV file (default: from config)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/etl_config.yaml',
        help='Path to configuration file (default: config/etl_config.yaml)'
    )
    
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Skip data validation phase'
    )
    
    parser.add_argument(
        '--save-intermediates',
        action='store_true',
        help='Save intermediate results for debugging'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_project_logging(log_level=args.log_level)
    
    try:
        logger.info("Starting SII Empresas ETL Pipeline")
        logger.info(f"Configuration: {args.config}")
        logger.info(f"Input file: {args.input or 'from config'}")
        logger.info(f"Validation: {'disabled' if args.no_validation else 'enabled'}")
        logger.info(f"Save intermediates: {args.save_intermediates}")
        
        # Run ETL pipeline
        results = run_etl_pipeline(
            config_path=args.config,
            input_file=args.input,
            validate_data=not args.no_validation,
            save_intermediates=args.save_intermediates
        )
        
        # Print summary
        print_pipeline_summary(results)
        
        # Exit with appropriate code
        if results['metadata'].status == 'completed':
            logger.info("ETL Pipeline completed successfully")
            sys.exit(0)
        elif results['metadata'].status == 'completed_with_warnings':
            logger.warning("ETL Pipeline completed with warnings")
            sys.exit(1)
        else:
            logger.error("ETL Pipeline failed")
            sys.exit(2)
            
    except Exception as e:
        logger.error(f"ETL Pipeline failed with error: {e}")
        sys.exit(3)


def print_pipeline_summary(results):
    """
    Print pipeline execution summary
    Single Responsibility: Format and display results
    """
    print("\n" + "="*60)
    print("ETL PIPELINE EXECUTION SUMMARY")
    print("="*60)
    
    metadata = results['metadata']
    
    print(f"Process ID: {metadata.process_id}")
    print(f"Status: {metadata.status}")
    print(f"Duration: {results['process_duration']:.2f} seconds")
    print(f"Records Processed: {metadata.records_processed:,}")
    print(f"Final Data Shape: {results['final_data_shape']}")
    
    # Quality report
    if results.get('quality_report'):
        quality_report = results['quality_report']
        print(f"\nDATA QUALITY:")
        print(f"  Quality Score: {quality_report.quality_score:.2%}")
        print(f"  Total Records: {quality_report.total_records:,}")
        print(f"  Valid Records: {quality_report.valid_records:,}")
        print(f"  Null Percentage: {quality_report.null_percentage:.2%}")
        print(f"  Duplicate Records: {quality_report.duplicate_records:,}")
        
        if quality_report.issues:
            print(f"  Issues Found: {len(quality_report.issues)}")
            for i, issue in enumerate(quality_report.issues[:3], 1):
                print(f"    {i}. {issue}")
            if len(quality_report.issues) > 3:
                print(f"    ... and {len(quality_report.issues) - 3} more")
    
    # Load results
    if results.get('load_results'):
        print(f"\nLOAD RESULTS:")
        for destination, success in results['load_results'].items():
            status = "SUCCESS" if success else "FAILED"
            print(f"  {destination}: {status}")
    
    # Errors
    if metadata.errors:
        print(f"\nERRORS:")
        for i, error in enumerate(metadata.errors, 1):
            print(f"  {i}. {error}")
    
    print("="*60)


if __name__ == "__main__":
    main()
