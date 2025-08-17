"""
Logging configuration for VideoCraft AI Video Editor
"""
import logging
import logging.config
import os
from datetime import datetime


def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate log filename with timestamp
    log_filename = f"logs/videocraft_{datetime.now().strftime('%Y%m%d')}.log"
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": log_filename,
                "mode": "a",
                "encoding": "utf-8"
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/errors.log",
                "mode": "a",
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": "INFO",
                "handlers": ["console", "file"]
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app": {
                "level": "DEBUG",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("🚀 VideoCraft AI Video Editor logging initialized")
    logger.info(f"📁 Log file: {log_filename}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"app.{name}")
