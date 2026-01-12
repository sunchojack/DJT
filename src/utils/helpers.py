"""Utility functions"""
import logging
import os
import shutil
import time
from datetime import datetime
from typing import Dict, Any


def setup_logging(config) -> logging.Logger:
    """Setup logging configuration"""
    # Create logs directory
    os.makedirs(os.path.dirname(config.logging.log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging.log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def validate_date_range(start_date: str, end_date: str, date_format: str = '%Y-%m-%d') -> bool:
    """Validate date range format and logic"""
    try:
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
        return start <= end
    except ValueError:
        return False


def create_output_directory(path: str) -> bool:
    """Create output directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def save_results(data: Dict[str, Any], output_file: str, format: str = 'json') -> bool:
    """Save analysis results to file"""
    try:
        import json
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception:
        return False


def format_number(value: float, decimals: int = 4) -> str:
    """Format number with appropriate precision"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def safe_float_conversion(value, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def clean_directories(directories: list[str]) -> None:
    """Clean all files and subdirectories from specified directories"""
    logger = logging.getLogger(__name__)

    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    logger.info(f"Removed file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {file_path}: {e}")
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_path)
                    logger.info(f"Removed directory: {dir_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove directory {dir_path}: {e}")


def load_valid_tickers(file_path: str) -> list[str]:
    """Load valid tickers from file, fetch if not exists"""
    if not os.path.exists(file_path):
        try:
            from get_all_tickers import get_tickers
            tickers = get_tickers()
            with open(file_path, 'w') as f:
                f.write('\n'.join(tickers))
            return [t.upper() for t in tickers]
        except ImportError:
            logging.getLogger(__name__).warning("get_all_tickers not installed, using empty list")
            return []
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to fetch tickers: {e}")
            return []
    try:
        with open(file_path, 'r') as f:
            tickers = [line.strip().upper() for line in f if line.strip()]
        return tickers
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to load tickers from {file_path}: {e}")
        return []