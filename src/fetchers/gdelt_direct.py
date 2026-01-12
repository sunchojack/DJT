"""Direct GDELT fetcher using gdelt library"""
from datetime import datetime, timedelta
import os
import pandas as pd
import logging
from io import StringIO
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import gdelt
except ImportError:
    gdelt = None
    logging.warning("gdelt library not available")

from .base import BaseGdeltFetcher


class GdeltDirectFetcher(BaseGdeltFetcher):
    """GDELT data fetcher using direct GDELT access"""
    
    def __init__(self, config):
        super().__init__(config)
        if gdelt is None:
            raise ImportError("gdelt library is required for GdeltDirectFetcher")
        
        self.gd2 = gdelt.gdelt(version=config.gdelt.gdelt_version)
        self.logger = logging.getLogger(__name__)
    
    def fetch(self, **kwargs) -> pd.DataFrame:
        """Fetch GDELT data directly"""
        all_data = []
        
        # Convert dates
        start_date = datetime.strptime(self.config.gdelt.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(self.config.gdelt.end_date, '%Y-%m-%d')
        
        # Create output folder
        os.makedirs(self.config.gdelt.output_folder, exist_ok=True)
        
        # Generate date pairs (1-day chunks for accuracy)
        date_pairs = self._generate_date_pairs(start_date, end_date)
        
        if self.config.parallel_processing:
            all_data = self._fetch_parallel(date_pairs)
        else:
            all_data = self._fetch_sequential(date_pairs)
        
        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
    
    def _generate_date_pairs(self, start_date: datetime, end_date: datetime):
        """Generate 1-day date pairs for accurate processing"""
        date_pairs = []
        current_date = start_date

        while current_date < end_date:
            next_date = current_date + timedelta(days=1)
            if next_date > end_date:
                next_date = end_date

            # Check if file already exists
            output_filename = f'{self.config.gdelt.output_folder}/gdelt_direct_{current_date.strftime("%Y%m%d")}_{next_date.strftime("%Y%m%d")}.csv'

            if not os.path.exists(output_filename):
                date_pairs.append((current_date, next_date, output_filename))

            current_date = next_date

        return date_pairs
    
    def _fetch_single_pair(self, date_pair):
        """Fetch data for a single date pair"""
        current_date, next_date, output_filename = date_pair
        
        try:
            # Convert dates to GDELT format (daily)
            start_date_str = current_date.strftime('%Y%m%d')
            end_date_str = next_date.strftime('%Y%m%d')
            
            self.logger.info(f'Processing from {current_date} to {next_date}')
            
            # Search GDELT
            results = self.gd2.Search(
                [start_date_str, end_date_str], 
                table=self.config.gdelt.table,
                coverage=self.config.gdelt.coverage, 
                output='csv'
            )
            
            # Read results into DataFrame
            df = pd.read_csv(StringIO(results))
            
            # Filter by keyword
            df_filtered = self.filter_by_keyword(df, self.config.gdelt.keyword)
            
            # Save filtered data
            df_filtered.to_csv(output_filename, index=False)
            self.logger.info(f'Results saved to {output_filename}')
            
            return df_filtered
            
        except Exception as e:
            self.logger.error(f"Error processing dates {current_date} to {next_date}: {e}")
            return pd.DataFrame()
    
    def _fetch_parallel(self, date_pairs):
        """Fetch data in parallel"""
        all_data = []
        
        with ThreadPoolExecutor(max_workers=self.config.gdelt.max_workers) as executor:
            futures = {executor.submit(self._fetch_single_pair, date_pair): date_pair 
                      for date_pair in date_pairs}
            
            for future in as_completed(futures):
                try:
                    df = future.result()
                    if not df.empty:
                        all_data.append(df)
                except Exception as e:
                    date_pair = futures[future]
                    self.logger.error(f"Error processing {date_pair}: {e}")
        
        return all_data
    
    def _fetch_sequential(self, date_pairs):
        """Fetch data sequentially"""
        all_data = []
        
        for date_pair in date_pairs:
            df = self._fetch_single_pair(date_pair)
            if not df.empty:
                all_data.append(df)
        
        return all_data
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        if not super().validate_data(data):
            return False
        
        # Check for direct GDELT specific required columns
        required_columns = ['DATE']
        return all(col in data.columns for col in required_columns)