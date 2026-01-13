"""Stock data fetcher using yfinance"""
import pandas as pd
import yfinance as yf
import logging
import os
from typing import Dict, List

from .base import BaseFetcher


class StockFetcher(BaseFetcher):
    """Stock data fetcher using Yahoo Finance API"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    def fetch(self, **kwargs) -> pd.DataFrame:
        """Fetch stock data for the configured ticker"""
        # Create output directory
        os.makedirs(os.path.dirname(self.config.stock.output_file), exist_ok=True)

        # Get the single ticker from config
        if not self.config.stock.companies:
            self.logger.error("No companies configured for stock fetching")
            return pd.DataFrame()

        company = self.config.stock.companies[0]  # Use the first (and typically only) company
        ticker = company['ticker']
        name = company['name']

        try:
            self.logger.info(f"Fetching data for {name} ({ticker})")

            # Fetch data
            data = self._fetch_single_ticker(ticker)

            if not data.empty:
                # Save to CSV
                data.to_csv(self.config.stock.output_file)
                self.logger.info(f"Stock data saved to {self.config.stock.output_file}")

                return data
            else:
                self.logger.warning(f"No data returned for {name} ({ticker})")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch data for {name} ({ticker}): {e}")
            return pd.DataFrame()
    
    def _fetch_single_ticker(self, ticker: str) -> pd.DataFrame:
        """Fetch data for a single ticker"""
        data = yf.download(
            ticker,
            start=self.config.stock.start_date,
            end=self.config.stock.end_date,
            interval=self.config.stock.interval
        )
        
        return data if data is not None else pd.DataFrame()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate stock data"""
        if data.empty:
            return False
        
        # Check for required columns
        required_columns = ['Close', 'Adj Close', 'Volume']
        available_columns = [col for col in required_columns if col in data.columns]
        
        if not available_columns:
            self.logger.warning(f"None of the required columns found. Available columns: {data.columns.tolist()}")
            return False
        
        return True