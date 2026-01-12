import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class GdeltConfig:
    """Configuration for GDELT data fetching"""
    keyword: str = "trump"
    country: str = "US"
    start_date: str = "2024-01-01"
    end_date: str = "2024-06-25"
    max_workers: int = 4
    
    # API vs Direct GDELT settings
    use_api: bool = False
    gdelt_version: int = 2
    table: str = "gkg"
    coverage: bool = False
    
    # Output settings
    output_folder: str = "data/gdelt"
    file_prefix: str = "gdelt_results"


@dataclass
class StockConfig:
    """Configuration for stock data fetching"""
    tickers: Optional[List[str]] = None
    companies: Optional[List[Dict[str, str]]] = None
    
    def __post_init__(self):
        if self.companies is None:
            self.companies = [{"name": "Trump Media & Technology", "ticker": "DJT"}]
        if self.tickers is None:
            self.tickers = [comp["ticker"] for comp in self.companies]
    
    start_date: str = "2024-01-01"
    end_date: str = "2024-06-25"
    interval: str = "1d"
    output_file: str = "data/stock/djt_stock.csv"


@dataclass
class AnalysisConfig:
    """Configuration for data analysis"""
    sentiment_column: str = "V2Tone"
    stock_column: str = "Adj Close"
    date_column: str = "Date"
    
    # Visualization settings
    plot_differences: bool = True
    plot_correlation: bool = True
    output_plots: bool = True
    plot_folder: str = "data/results"
    
    # Statistical analysis
    perform_regression: bool = True
    confidence_level: float = 0.95


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    log_file: str = "logs/gdelt_djt.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class Config:
    """Main configuration class"""
    gdelt: GdeltConfig = field(default_factory=GdeltConfig)
    stock: StockConfig = field(default_factory=StockConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # General settings
    cache_enabled: bool = True
    cache_folder: str = "data/cache"
    parallel_processing: bool = True
    valid_tickers_file: str = "data/valid_tickers.txt"
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from JSON or YAML file"""
        # Implementation for loading from file can be added later
        return cls()
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to file"""
        # Implementation for saving to file can be added later
        pass


# Default configuration instance
default_config = Config()