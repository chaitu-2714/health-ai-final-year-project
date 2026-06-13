import logging
import os
import sys

def setup_logger(log_level=logging.INFO):
    """Sets up application-wide logger writing to console and local file."""
    # Define log format
    log_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Base logger
    root_logger = logging.getLogger("MedicalApp")
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if already configured
    if root_logger.handlers:
        return root_logger

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File Handler
    try:
        log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(log_dir, "medical_analysis.log")
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(log_format)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logger started. Logging to file: {log_file}")
    except Exception as e:
        root_logger.error(f"Failed to create file handler for logging: {e}")

    return root_logger
