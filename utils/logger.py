"""
Logger Utility
==============

Simple, clean logging setup.

By OkayYouGotMe
"""

import logging
import sys
from config.settings import LOG_LEVEL, LOG_FORMAT, SAVE_LOGS_TO_FILE, LOG_FILE_PATH


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if SAVE_LOGS_TO_FILE:
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
    
    return logger
