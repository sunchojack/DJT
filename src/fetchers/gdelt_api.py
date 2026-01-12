"""GDELT API fetcher using gdeltdoc library"""
from datetime import datetime, timedelta
import os
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

try:
    from gdeltdoc import GdeltDoc, Filters
    GDELTDOC_AVAILABLE = True
except ImportError:
    GdeltDoc = None
    Filters = None
    GDELTDOC_AVAILABLE = False
    logging.warning("gdeltdoc library not available")

from .base import BaseGdeltFetcher


class GdeltApiFetcher(BaseGdeltFetcher):
    """GDELT data fetcher using gdeltdoc API"""
    
    def __init__(self, config):
        super().__init__(config)
        if not GDELTDOC_AVAILABLE:
            raise ImportError("gdeltdoc library is required for GdeltApiFetcher")
        
        if GdeltDoc is None:
            raise ImportError("gdeltdoc library is required for GdeltApiFetcher")
        self.gd = GdeltDoc()
        self.logger = logging.getLogger(__name__)
    
    def fetch(self, **kwargs) -> pd.DataFrame:
        """Fetch GDELT data using API"""
        all_data = []
        
        # Convert dates
        start_date = datetime.strptime(self.config.gdelt.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(self.config.gdelt.end_date, '%Y-%m-%d')
        
        # Create output folder
        os.makedirs(self.config.gdelt.output_folder, exist_ok=True)
        
        # Generate date ranges
        date_ranges = self._generate_date_ranges(start_date, end_date)
        
        if self.config.parallel_processing:
            all_data = self._fetch_parallel(date_ranges)
        else:
            all_data = self._fetch_sequential(date_ranges)
        
        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
    
    def _generate_date_ranges(self, start_date: datetime, end_date: datetime):
        """Generate daily date ranges"""
        current_date = start_date
        date_ranges = []
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            date_ranges.append((current_date, next_date))
            current_date = next_date
        
        return date_ranges
    
    def _fetch_single_date(self, date_range):
        """Fetch data for a single date range"""
        current_date, next_date = date_range
        
        try:
            # Set up filters
            if Filters is None:
                raise ImportError("gdeltdoc library not available")
            f = Filters(
                keyword=self.config.gdelt.keyword,
                country=self.config.gdelt.country,
                start_date=current_date.strftime('%Y-%m-%d'),
                end_date=next_date.strftime('%Y-%m-%d')
            )
            
            # Search articles
            articles = self.gd.article_search(f)
            
            if articles is not None and len(articles) > 0:
                df = pd.DataFrame(articles)
                
                # Save individual file
                output_filename = f'{self.config.gdelt.output_folder}/gdelt_api_{current_date.strftime("%Y-%m-%d")}.csv'
                df.to_csv(output_filename, index=False)
                
                self.logger.info(f"Fetched {len(df)} articles for {current_date.strftime('%Y-%m-%d')}")
                return df
            else:
                self.logger.warning(f"No articles found for {current_date.strftime('%Y-%m-%d')}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {current_date.strftime('%Y-%m-%d')}: {e}")
            return pd.DataFrame()
    
    def _fetch_parallel(self, date_ranges):
        """Fetch data in parallel"""
        all_data = []
        
        with ThreadPoolExecutor(max_workers=self.config.gdelt.max_workers) as executor:
            futures = {executor.submit(self._fetch_single_date, date_range): date_range 
                      for date_range in date_ranges}
            
            for future in as_completed(futures):
                try:
                    df = future.result()
                    if not df.empty:
                        all_data.append(df)
                except Exception as e:
                    date_range = futures[future]
                    self.logger.error(f"Error processing {date_range}: {e}")
        
        return all_data
    
    def _fetch_sequential(self, date_ranges):
        """Fetch data sequentially"""
        all_data = []
        
        for date_range in date_ranges:
            df = self._fetch_single_date(date_range)
            if not df.empty:
                all_data.append(df)
        
        return all_data
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        if not super().validate_data(data):
            return False
        
        # Check for API-specific required columns
        required_columns = ['date']
        return all(col in data.columns for col in required_columns)