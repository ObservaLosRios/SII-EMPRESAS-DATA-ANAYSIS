"""
Logging utilities following SOLID principles
Single Responsibility: Handle logging configuration and setup
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class LoggerManager:
    """
    Single Responsibility: Manage logging configuration
    Open/Closed: Easy to extend with new logging formats or destinations
    """
    
    def __init__(self):
        self._configured = False
    
    def setup_logging(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        log_format: Optional[str] = None
    ) -> None:
        """
        Setup logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
            log_format: Optional custom log format
        """
        if self._configured:
            return
        
        # Remove default handler
        logger.remove()
        
        # Default format
        if log_format is None:
            log_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        
        # Add console handler
        logger.add(
            sys.stdout,
            format=log_format,
            level=log_level,
            colorize=True
        )
        
        # Add file handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                log_file,
                format=log_format,
                level=log_level,
                rotation="10 MB",
                retention="7 days",
                compression="zip"
            )
        
        self._configured = True
        logger.info("Logging configured successfully")
    
    def get_logger(self, name: str):
        """Get a logger instance with the given name"""
        return logger.bind(name=name)


# Global logger manager instance
logger_manager = LoggerManager()


def setup_project_logging(log_level: str = "INFO") -> None:
    """Setup logging for the entire project"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger_manager.setup_logging(
        log_level=log_level,
        log_file="logs/etl_process.log"
    )


def get_logger(name: str):
    """Get a project logger instance"""
    return logger_manager.get_logger(name)
