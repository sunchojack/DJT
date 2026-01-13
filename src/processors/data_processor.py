"""Data processing utilities"""
import os
import pandas as pd
import numpy as np
import logging
from typing import Optional, List
from datetime import datetime


class DataProcessor:
    """Processes GDELT and stock data for analysis"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_gdelt_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw GDELT data"""
        if df.empty:
            self.logger.warning("Empty GDELT DataFrame provided")
            return df
        
        try:
            # Handle GDELT API data (has seendate column)
            if 'seendate' in df.columns:
                df['Date'] = pd.to_datetime(df['seendate']).dt.strftime('%Y-%m-%d')
                # For API data, we need to create a dummy sentiment since we don't have V2Tone
                # Use article count as proxy for sentiment volume
                df['V2ToneOut'] = 1.0  # Neutral sentiment for API data
            # Handle GDELT direct data (has DATE column)
            elif 'DATE' in df.columns:
                df['Date'] = pd.to_datetime(df['DATE'], format='%Y%m%d%H%M%S').dt.strftime('%Y-%m-%d')
                # Extract sentiment from V2Tone for direct data
                if self.config.analysis.sentiment_column in df.columns:
                    df['V2ToneOut'] = df[self.config.analysis.sentiment_column].apply(
                        lambda x: self._extract_tone_value(x)
                    )
                else:
                    # Create dummy sentiment if V2Tone not available
                    df['V2ToneOut'] = 1.0
            # Handle 'date' column
            elif 'date' in df.columns:
                df['Date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                df['V2ToneOut'] = 1.0
            else:
                self.logger.warning("No date column found in GDELT data")
                # Create dummy data for testing
                df['Date'] = '2025-01-01'
                df['V2ToneOut'] = 1.0
            
            # Aggregate by date - average sentiment for each day
            if 'V2ToneOut' in df.columns and 'Date' in df.columns:
                processed_df = df.groupby('Date')['V2ToneOut'].mean().reset_index()
                self.logger.info(f"Processed {len(df)} GDELT records into {len(processed_df)} daily aggregates")
                # Debug: save processed GDELT data
                debug_dir = os.path.join(os.path.dirname(__file__), '../../data/results/debug')
                os.makedirs(debug_dir, exist_ok=True)
                processed_df.to_csv(os.path.join(debug_dir, 'gdelt_processed.csv'), index=False)
                return processed_df
            else:
                self.logger.warning("No sentiment data to aggregate")
                return df
                
        except Exception as e:
            self.logger.error(f"Error processing GDELT data: {e}")
            return pd.DataFrame()
    
    def process_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw stock data"""
        if df.empty:
            self.logger.warning("Empty stock DataFrame provided")
            return df
        
        try:
            # Handle the weird yfinance output format
            if df.shape[0] >= 3 and df.iloc[0, 0] == 'Price' and df.iloc[1, 0] == 'Ticker':
                # Skip the header rows and use proper column names
                df_clean = df.iloc[4:].copy()
                df_clean.columns = df.iloc[2].values  # Use third row as headers
                df_clean = df_clean.reset_index(drop=True)
            else:
                df_clean = df.copy()
            
            # Handle multi-level columns if present
            if isinstance(df_clean.columns, pd.MultiIndex):
                df_clean.columns = ['_'.join(col).strip() for col in df_clean.columns.values]
            
            # Find date column and format it
            date_col = None
            for col in df_clean.columns:
                if col.lower() == 'date' or 'date' in col.lower():
                    date_col = col
                    break
            
            if date_col:
                df_clean['Date'] = pd.to_datetime(df_clean[date_col]).dt.strftime('%Y-%m-%d')
            else:
                self.logger.warning("No date column found, using index")
                df_clean['Date'] = pd.to_datetime(df_clean.index).strftime('%Y-%m-%d')
            
            # Find price column (Close or Adj Close)
            price_col = None
            for col in df_clean.columns:
                if 'close' in col.lower():
                    price_col = col
                    break
                elif 'adj close' in col.lower():
                    price_col = col
                    break
            
            if price_col is None:
                self.logger.error("No price column found, available columns: " + str(df_clean.columns.tolist()))
                return pd.DataFrame()
            
            # Convert to numeric
            df_clean[price_col] = pd.to_numeric(df_clean[price_col], errors='coerce')
            
            # Create simplified DataFrame
            processed_df = df_clean[['Date', price_col]].copy()
            processed_df = processed_df.rename(columns={price_col: 'Adj Close'})
            processed_df = processed_df.dropna()

            self.logger.info(f"Processed stock data with {len(processed_df)} records")
            # Debug: save processed stock data
            debug_dir = os.path.join(os.path.dirname(__file__), '../../data/results/debug')
            os.makedirs(debug_dir, exist_ok=True)
            processed_df.to_csv(os.path.join(debug_dir, 'stock_processed.csv'), index=False)
            return processed_df
            
        except Exception as e:
            self.logger.error(f"Error processing stock data: {e}")
            return pd.DataFrame()
    
    def merge_datasets(self, gdelt_df: pd.DataFrame, stock_df: pd.DataFrame) -> pd.DataFrame:
        """Merge GDELT and stock data for analysis"""
        try:
            if gdelt_df.empty or stock_df.empty:
                self.logger.warning("Cannot merge empty datasets")
                return pd.DataFrame()

            # Ensure both have Date column
            if 'Date' not in gdelt_df.columns:
                self.logger.warning("Date column missing from GDELT dataset")
                return pd.DataFrame()

            if 'Date' not in stock_df.columns:
                self.logger.warning("Date column missing from stock dataset")
                return pd.DataFrame()

            # Reset index to avoid conflicts
            gdelt_df = gdelt_df.reset_index(drop=True)
            stock_df = stock_df.reset_index(drop=True)

            # Convert Date to string to ensure consistent merge
            gdelt_df['Date'] = gdelt_df['Date'].astype(str)
            stock_df['Date'] = stock_df['Date'].astype(str)

            # Merge on Date
            merged_df = gdelt_df.merge(stock_df, on='Date', how='inner')

            self.logger.info(f"Merged datasets resulting in {len(merged_df)} records")

            # Debug: save merged data
            debug_dir = os.path.join(os.path.dirname(__file__), '../../data/results/debug')
            os.makedirs(debug_dir, exist_ok=True)
            merged_df.to_csv(os.path.join(debug_dir, 'merged.csv'), index=False)

            return merged_df

        except Exception as e:
            self.logger.error(f"Error merging datasets: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def calculate_differences(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily differences for analysis"""
        if df.empty:
            return df
        
        try:
            # Calculate differences
            df['diff_Adj Close'] = df['Adj Close'] - df['Adj Close'].shift(1)
            df['diff_V2ToneOut'] = df['V2ToneOut'] - df['V2ToneOut'].shift(1)
            
            # Remove rows with NaN in differences
            df_clean = df.dropna(subset=['diff_V2ToneOut', 'diff_Adj Close'])
            
            self.logger.info(f"Calculated differences for {len(df_clean)} records")
            return df_clean
            
        except Exception as e:
            self.logger.error(f"Error calculating differences: {e}")
            return df
    
    def _extract_tone_value(self, tone_str: str, which: int = 2) -> Optional[float]:
        """Extract specific tone value from V2Tone string"""
        if pd.isna(tone_str) or not isinstance(tone_str, str):
            return None
        
        try:
            values = tone_str.split(',')
            if len(values) > which:
                return float(values[which])
            else:
                return None
        except (ValueError, IndexError):
            return None