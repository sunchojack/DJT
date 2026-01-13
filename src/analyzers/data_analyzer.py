"""Statistical analysis and visualization"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import logging
import os
from typing import Optional, Tuple


class DataAnalyzer:
    """Analyzes GDELT and stock data relationship"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        plt.style.use('default')
    
    def analyze_correlation(self, df: pd.DataFrame) -> dict:
        """Analyze correlation between sentiment and stock data"""
        if df.empty:
            self.logger.warning("Empty DataFrame provided for correlation analysis")
            return {}
        
        try:
            results = {}
            
            # Basic correlations
            if all(col in df.columns for col in ['V2ToneOut', 'Adj Close']):
                results['correlation'] = df['V2ToneOut'].corr(df['Adj Close'])
                results['spearman_correlation'] = df['V2ToneOut'].corr(df['Adj Close'], method='spearman')
                self.logger.info(f"Correlation: {results['correlation']:.3f}")
            
            # Differences correlation
            if all(col in df.columns for col in ['diff_V2ToneOut', 'diff_Adj Close']):
                results['diff_correlation'] = df['diff_V2ToneOut'].corr(df['diff_Adj Close'])
                results['diff_spearman_correlation'] = df['diff_V2ToneOut'].corr(df['diff_Adj Close'], method='spearman')
                self.logger.info(f"Differences correlation: {results['diff_correlation']:.3f}")
            
            # Lag correlations
            if all(col in df.columns for col in ['V2ToneOut', 'Adj Close']):
                results['lag_correlations'] = self._calculate_lag_correlations(df)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}")
            return {}
    
    def perform_regression(self, df: pd.DataFrame) -> dict:
        """Perform linear regression analysis"""
        if df.empty:
            self.logger.warning("Empty DataFrame provided for regression analysis")
            return {}
        
        try:
            results = {}
            
            # Level regression
            if all(col in df.columns for col in ['V2ToneOut', 'Adj Close']):
                result = stats.linregress(
                    df['V2ToneOut'].astype('float'),
                    df['Adj Close'].astype('float')
                )
                slope, intercept, r_value, p_value, std_err = result.slope, result.intercept, result.rvalue, result.pvalue, result.stderr
                
                results['level'] = {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'std_err': std_err
                }
                
                self.logger.info(f"Level regression - R²: {r_value ** 2:.3f}, p-value: {p_value:.4f}")
            
            # Differences regression
            if all(col in df.columns for col in ['diff_V2ToneOut', 'diff_Adj Close']):
                result = stats.linregress(
                    df['diff_V2ToneOut'].astype('float'),
                    df['diff_Adj Close'].astype('float')
                )
                slope, intercept, r_value, p_value, std_err = result.slope, result.intercept, result.rvalue, result.pvalue, result.stderr
                
                results['differences'] = {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'std_err': std_err
                }
                
                self.logger.info(f"Differences regression - R²: {r_value ** 2:.3f}, p-value: {p_value:.4f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in regression analysis: {e}")
            return {}
    
    def create_visualizations(self, df: pd.DataFrame, save_plots: bool = True) -> None:
        """Create visualization plots"""
        if df.empty:
            self.logger.warning("Empty DataFrame provided for visualization")
            return
        
        try:
            # Create plots directory
            os.makedirs(self.config.analysis.plot_folder, exist_ok=True)
            
            # Plot 1: Time series comparison
            if all(col in df.columns for col in ['Date', 'Adj Close', 'V2ToneOut']):
                self._plot_time_series(df, save_plots)
            
            # Plot 2: Differences comparison
            if all(col in df.columns for col in ['Date', 'diff_Adj Close', 'diff_V2ToneOut']):
                self._plot_differences(df, save_plots)
            
            # Plot 3: Scatter plot
            if all(col in df.columns for col in ['diff_V2ToneOut', 'diff_Adj Close']):
                self._plot_scatter(df, save_plots)

            # Plot 4: Stock Price vs V2Tone scatter
            if all(col in df.columns for col in ['V2ToneOut', 'Adj Close']):
                self._plot_stock_vs_tone(df, save_plots)
            
            # Plot 5: Correlation heatmap
            if len(df.columns) > 2:
                self._plot_correlation_heatmap(df, save_plots)
                
        except Exception as e:
            self.logger.error(f"Error creating visualizations: {e}")
    
    def _plot_time_series(self, df: pd.DataFrame, save_plots: bool) -> None:
        """Plot time series comparison"""
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Stock price
        ax1.plot(df['Date'], df['Adj Close'], color='darkgreen', label='Stock Price', alpha=0.7)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Price', color='darkgreen')
        ax1.tick_params(axis='y', labelcolor='darkgreen')
        
        # Sentiment on secondary axis
        ax2 = ax1.twinx()
        ax2.plot(df['Date'], df['V2ToneOut'], color='brown', label='Sentiment', linestyle='dashed', alpha=0.7)
        ax2.set_ylabel('Sentiment', color='brown')
        ax2.tick_params(axis='y', labelcolor='brown')
        
        plt.title('Stock Price vs Sentiment Over Time')
        plt.grid(True, alpha=0.3)
        
        if save_plots:
            plt.savefig(f'{self.config.analysis.plot_folder}/time_series.png', dpi=300, bbox_inches='tight')

        plt.close()
    
    def _plot_differences(self, df: pd.DataFrame, save_plots: bool) -> None:
        """Plot daily differences"""
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Stock differences
        ax1.plot(df['Date'], df['diff_Adj Close'], color='darkgreen', label='Stock Price Change', alpha=0.7)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Price Change', color='darkgreen')
        ax1.tick_params(axis='y', labelcolor='darkgreen')
        ax1.grid(True, alpha=0.3)
        
        # Sentiment differences on secondary axis
        ax2 = ax1.twinx()
        ax2.plot(df['Date'], df['diff_V2ToneOut'], color='brown', label='Sentiment Change', linestyle='dashed', alpha=0.7)
        ax2.set_ylabel('Sentiment Change', color='brown')
        ax2.tick_params(axis='y', labelcolor='brown')
        
        plt.title('Daily Changes: Stock Price vs Sentiment')
        
        if save_plots:
            plt.savefig(f'{self.config.analysis.plot_folder}/differences.png', dpi=300, bbox_inches='tight')

        plt.close()
    
    def _plot_scatter(self, df: pd.DataFrame, save_plots: bool) -> None:
        """Plot scatter with regression line"""
        plt.figure(figsize=(8, 6))
        
        x = df['diff_V2ToneOut']
        y = df['diff_Adj Close']
        
        # Scatter plot
        plt.scatter(x, y, alpha=0.6, color='steelblue')
        
        # Regression line
        if len(x) > 1:
            result = stats.linregress(x.astype('float'), y.astype('float'))
            slope, intercept = result.slope, result.intercept
            x_line = np.array([x.min(), x.max()])
            y_line = slope * x_line + intercept
            plt.plot(x_line, y_line, 'r--', label=f'y = {slope:.3f}x + {intercept:.3f}')
            plt.legend()
        
        plt.xlabel('Sentiment Change')
        plt.ylabel('Stock Price Change')
        plt.title('Correlation between Sentiment and Stock Price Changes')
        plt.grid(True, alpha=0.3)
        
        if save_plots:
            plt.savefig(f'{self.config.analysis.plot_folder}/scatter.png', dpi=300, bbox_inches='tight')

        plt.close()

    def _plot_stock_vs_tone(self, df: pd.DataFrame, save_plots: bool) -> None:
        """Plot scatter of stock price vs V2Tone (levels)"""
        plt.figure(figsize=(8, 6))

        x = df['V2ToneOut']
        y = df['Adj Close']

        # Scatter plot
        plt.scatter(x, y, alpha=0.6, color='steelblue')

        # Regression line
        if len(x) > 1:
            result = stats.linregress(x.astype('float'), y.astype('float'))
            slope, intercept = result.slope, result.intercept
            x_line = np.array([x.min(), x.max()])
            y_line = slope * x_line + intercept
            plt.plot(x_line, y_line, 'r--', label=f'y = {slope:.3f}x + {intercept:.3f}')
            plt.legend()

        plt.xlabel('V2Tone (Sentiment)')
        plt.ylabel('Stock Price (Adj Close)')
        plt.title('Stock Price vs V2Tone Sentiment')
        plt.grid(True, alpha=0.3)

        if save_plots:
            plt.savefig(f'{self.config.analysis.plot_folder}/stock_vs_tone.png', dpi=300, bbox_inches='tight')

        plt.close()

    def _plot_correlation_heatmap(self, df: pd.DataFrame, save_plots: bool) -> None:
        """Plot correlation heatmap"""
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return
        
        correlation_matrix = df[numeric_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f')
        plt.title('Correlation Matrix')
        
        if save_plots:
            plt.savefig(f'{self.config.analysis.plot_folder}/correlation_heatmap.png', dpi=300, bbox_inches='tight')

        plt.close()
    
    def _calculate_lag_correlations(self, df: pd.DataFrame, max_lags: int = 5) -> dict:
        """Calculate correlations with different lags"""
        correlations = {}
        
        for lag in range(-max_lags, max_lags + 1):
            if lag == 0:
                continue
                
            if lag > 0:
                # Stock lags sentiment
                shifted_sentiment = df['V2ToneOut'].shift(lag)
                valid_data = ~shifted_sentiment.isna() & ~df['Adj Close'].isna()
                if valid_data.sum() > 1:
                    corr = shifted_sentiment[valid_data].corr(df.loc[valid_data, 'Adj Close'])
                    correlations[f'stock_lag_{lag}'] = corr
            else:
                # Sentiment lags stock
                shifted_stock = df['Adj Close'].shift(abs(lag))
                valid_data = ~shifted_stock.isna() & ~df['V2ToneOut'].isna()
                if valid_data.sum() > 1:
                    corr = df.loc[valid_data, 'V2ToneOut'].corr(shifted_stock[valid_data])
                    correlations[f'sentiment_lag_{abs(lag)}'] = corr
        
        return correlations