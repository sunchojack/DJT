"""Main entry point for GDELT vs DJT analysis"""
import argparse
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from config.settings import Config, default_config
from fetchers.gdelt_api import GdeltApiFetcher
from fetchers.gdelt_direct import GdeltDirectFetcher
from fetchers.stock import StockFetcher
from processors.data_processor import DataProcessor
from analyzers.data_analyzer import DataAnalyzer
from utils.helpers import setup_logging, validate_date_range, create_output_directory, save_results, clean_directories
import pandas as pd
import logging


class GdeltDjtAnalysis:
    """Main analysis pipeline"""
    
    def __init__(self, config: Config = None):
        self.config = config or default_config
        self.config = config or default_config
        self.logger = setup_logging(self.config)
        
        # Initialize components
        self._init_fetchers()
        self.data_processor = DataProcessor(self.config)
        self.analyzer = DataAnalyzer(self.config)
        
        # Create necessary directories
        create_output_directory(self.config.gdelt.output_folder)
        create_output_directory(os.path.dirname(self.config.stock.output_file))
        create_output_directory(self.config.analysis.plot_folder)
        create_output_directory(self.config.cache_folder)

        # Clean directories on startup
        clean_directories([
            self.config.gdelt.output_folder,
            os.path.dirname(self.config.stock.output_file),
            self.config.analysis.plot_folder,
            self.config.cache_folder
        ])
    
    def _init_fetchers(self):
        """Initialize appropriate fetchers based on configuration"""
        # GDELT fetcher
        if self.config.gdelt.use_api:
            self.gdelt_fetcher = GdeltApiFetcher(self.config)
        else:
            self.gdelt_fetcher = GdeltDirectFetcher(self.config)
        
        # Stock fetcher
        self.stock_fetcher = StockFetcher(self.config)
    
    def fetch_data(self, fetch_gdelt: bool = True, fetch_stock: bool = True):
        """Fetch raw data"""
        self.logger.info("Starting data fetching process")
        
        gdelt_data = pd.DataFrame()
        stock_data = pd.DataFrame()
        
        # Fetch GDELT data
        if fetch_gdelt:
            self.logger.info("Fetching GDELT data...")
            try:
                gdelt_data = self.gdelt_fetcher.fetch()
                if not gdelt_data.empty:
                    self.logger.info(f"Successfully fetched {len(gdelt_data)} GDELT records")
                else:
                    self.logger.warning("No GDELT data was fetched")
            except Exception as e:
                self.logger.error(f"Error fetching GDELT data: {e}")
        
        # Fetch stock data
        if fetch_stock:
            self.logger.info("Fetching stock data...")
            try:
                stock_data = self.stock_fetcher.fetch()
                if not stock_data.empty:
                    self.logger.info(f"Successfully fetched stock data with {len(stock_data)} records")
                else:
                    self.logger.warning("No stock data was fetched")
            except Exception as e:
                self.logger.error(f"Error fetching stock data: {e}")
        
        return gdelt_data, stock_data
    
    def process_data(self, gdelt_data: pd.DataFrame, stock_data: pd.DataFrame):
        """Process and merge data"""
        self.logger.info("Starting data processing")
        
        # Process individual datasets
        processed_gdelt = self.data_processor.process_gdelt_data(gdelt_data)
        processed_stock = self.data_processor.process_stock_data(stock_data)
        
        # Merge datasets
        merged_data = self.data_processor.merge_datasets(processed_gdelt, processed_stock)
        
        if not merged_data.empty:
            # Calculate differences
            final_data = self.data_processor.calculate_differences(merged_data)
            self.logger.info(f"Final processed dataset contains {len(final_data)} records")
            return final_data
        else:
            self.logger.error("Failed to merge datasets")
            return pd.DataFrame()
    
    def analyze(self, data: pd.DataFrame):
        """Perform analysis on processed data"""
        if data.empty:
            self.logger.error("No data available for analysis")
            return {}
        
        self.logger.info("Starting analysis")
        
        results = {}
        
        # Correlation analysis
        correlation_results = self.analyzer.analyze_correlation(data)
        if correlation_results:
            results['correlation'] = correlation_results
        
        # Regression analysis
        regression_results = self.analyzer.perform_regression(data)
        if regression_results:
            results['regression'] = regression_results
        
        # Create visualizations
        if self.config.analysis.output_plots:
            self.analyzer.create_visualizations(
                data, 
                save_plots=self.config.analysis.output_plots
            )
        
        return results
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        self.logger.info("Starting complete GDELT vs DJT analysis")
        
        # Fetch data
        gdelt_data, stock_data = self.fetch_data()
        
        # Process data
        processed_data = self.process_data(gdelt_data, stock_data)
        
        # Analyze
        results = self.analyze(processed_data)
        
        # Save results
        if results:
            output_file = os.path.join(self.config.analysis.plot_folder, 'analysis_results.json')
            if save_results(results, output_file):
                self.logger.info(f"Analysis results saved to {output_file}")
            else:
                self.logger.warning("Failed to save analysis results")

        # Save merged data
        if processed_data is not None and not processed_data.empty:
            merged_file = os.path.join(self.config.analysis.plot_folder, 'merged_data.csv')
            processed_data.to_csv(merged_file, index=False)
            self.logger.info(f"Merged data saved to {merged_file}")
        
        self.logger.info("Analysis complete!")
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='GDELT vs Stock Analysis')
    parser.add_argument('--use-api', action='store_true',
                         help='Use GDELT API instead of direct access')
    parser.add_argument('--start-date', type=str,
                         help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                         help='End date (YYYY-MM-DD)')
    parser.add_argument('--config', type=str,
                        help='Path to configuration file')
    parser.add_argument('--parallel', action='store_true', default=True,
                        help='Enable parallel processing')
    parser.add_argument('--no-plots', action='store_true',
                        help='Disable plot generation')

    args = parser.parse_args()

    print("Parsed arguments:", args)

    # Load configuration
    if args.config:
        config = Config.from_file(args.config)
    else:
        config = default_config

    # Prompt user for inputs
    print("GDELT vs Stock Analysis Tool")
    print("=" * 40)

    # Prompt for dates
    try:
        start_days = input("Enter number of days ago for start date (default 90): ").strip()
        start_days = int(start_days) if start_days else 90
    except ValueError:
        print("Invalid input, using default 90 days.")
        start_days = 90

    try:
        end_days = input("Enter number of days ago for end date (default 0): ").strip()
        end_days = int(end_days) if end_days else 0
    except ValueError:
        print("Invalid input, using default 0 days.")
        end_days = 0

    today = datetime.now().date()
    start_date = (today - timedelta(days=start_days)).isoformat()
    end_date = (today - timedelta(days=end_days)).isoformat()

    # Override with args if provided
    if args.start_date:
        start_date = args.start_date
    if args.end_date:
        end_date = args.end_date

    ticker = input("Enter stock ticker symbol (e.g., DJT, AAPL): ").strip().upper()
    if not ticker:
        print("Ticker cannot be empty. Exiting.")
        sys.exit(1)

    keywords = input("Enter keywords for GDELT search (comma-separated, e.g., trump, election): ").strip()
    if not keywords:
        print("Keywords cannot be empty. Exiting.")
        sys.exit(1)

    # Split keywords and take the first one for now (can be extended later)
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    if not keyword_list:
        print("No valid keywords provided. Exiting.")
        sys.exit(1)

    # Use the first keyword as primary
    primary_keyword = keyword_list[0]

    # Override configuration with command line arguments
    config.gdelt.use_api = args.use_api
    config.gdelt.start_date = start_date
    config.gdelt.end_date = end_date
    config.stock.start_date = start_date
    config.stock.end_date = end_date
    config.gdelt.keyword = primary_keyword
    config.parallel_processing = args.parallel
    config.analysis.output_plots = not args.no_plots

    # Update stock config with user ticker
    config.stock.companies = [{"name": f"{ticker} Stock", "ticker": ticker}]
    config.stock.tickers = [ticker]
    config.stock.output_file = f"data/stock/{ticker.lower()}_stock.csv"
    
    # Validate date range
    if not validate_date_range(config.gdelt.start_date, config.gdelt.end_date):
        print(f"Invalid date range: {config.gdelt.start_date} to {config.gdelt.end_date}")
        sys.exit(1)
    
    # Run analysis
    try:
        analysis = GdeltDjtAnalysis(config)
        results = analysis.run_complete_analysis()
        
        if results:
            print("\n=== Analysis Results ===")
            
            if 'correlation' in results:
                print("\nCorrelation Results:")
                for key, value in results['correlation'].items():
                    print(f"  {key}: {value}")
            
            if 'regression' in results:
                print("\nRegression Results:")
                for key, value in results['regression'].items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for subkey, subvalue in value.items():
                            print(f"    {subkey}: {subvalue}")
        else:
            print("Analysis completed but no results generated")
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()