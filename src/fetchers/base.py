"""Base classes for data fetchers"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class BaseFetcher(ABC):
    """Abstract base class for data fetchers"""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def fetch(self, **kwargs) -> pd.DataFrame:
        """Fetch data and return as DataFrame"""
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        pass


class BaseGdeltFetcher(BaseFetcher):
    """Base class for GDELT data fetchers"""
    
    def filter_by_keyword(self, df: pd.DataFrame, keyword: str) -> pd.DataFrame:
        """Filter DataFrame by keyword"""
        if df.empty:
            return df
        
        return df[df.apply(
            lambda row: row.astype(str).str.contains(keyword, case=False).any(), 
            axis=1
        )]
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate GDELT data"""
        if data.empty:
            return False
        
        # Check for required columns
        required_columns = ['DATE']
        return all(col in data.columns for col in required_columns)