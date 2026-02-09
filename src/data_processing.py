"""
Data processing module for Brent oil price analysis.
Handles loading, cleaning, and preparing the dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrentOilData:
    """Class to handle Brent oil price data loading and processing."""
    
    def __init__(self, data_path: str = "data/raw/BrentOilPrices.csv"):
        """
        Initialize data processor.
        
        Parameters
        ----------
        data_path : str
            Path to the raw CSV file
        """
        self.data_path = Path(data_path)
        self.df = None
        self.returns = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load raw Brent oil price data.
        
        Returns
        -------
        pd.DataFrame
            Raw dataset with Date and Price columns
        """
        logger.info(f"Loading data from {self.data_path}")
        
        try:
            # Read CSV with date parsing
            self.df = pd.read_csv(
                self.data_path,
                parse_dates=['Date'],
                dayfirst=True  # Dates are in day-month-year format
            )
            
            # Ensure proper column names
            self.df.columns = ['date', 'price']
            
            # Sort by date
            self.df = self.df.sort_values('date').reset_index(drop=True)
            
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            logger.info(f"Date range: {self.df['date'].min()} to {self.df['date'].max()}")
            
            return self.df
            
        except FileNotFoundError:
            logger.error(f"File not found at {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def clean_data(self) -> pd.DataFrame:
        """
        Clean the loaded data.
        
        Returns
        -------
        pd.DataFrame
            Cleaned dataset
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        logger.info("Cleaning data...")
        
        # Remove duplicates
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=['date'])
        logger.info(f"Removed {initial_rows - len(self.df)} duplicate rows")
        
        # Check for missing values
        missing = self.df.isnull().sum()
        if missing.any():
            logger.warning(f"Missing values found:\n{missing}")
            # Forward fill missing prices (common for time series)
            self.df['price'] = self.df['price'].fillna(method='ffill')
        
        # Ensure date is datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Set date as index
        self.df.set_index('date', inplace=True)
        
        # Remove any zero or negative prices (data errors)
        invalid_prices = (self.df['price'] <= 0).sum()
        if invalid_prices > 0:
            logger.warning(f"Found {invalid_prices} invalid prices (<= 0)")
            self.df = self.df[self.df['price'] > 0]
        
        logger.info(f"Cleaned data shape: {self.df.shape}")
        
        return self.df
    
    def calculate_returns(self, log_returns: bool = True) -> pd.Series:
        """
        Calculate price returns.
        
        Parameters
        ----------
        log_returns : bool
            If True, calculate log returns, else simple returns
            
        Returns
        -------
        pd.Series
            Returns series
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() and clean_data() first.")
        
        logger.info("Calculating returns...")
        
        if log_returns:
            # Log returns: log(P_t) - log(P_{t-1})
            self.returns = np.log(self.df['price']).diff()
        else:
            # Simple returns: (P_t - P_{t-1}) / P_{t-1}
            self.returns = self.df['price'].pct_change()
        
        # Remove first NaN value
        self.returns = self.returns.dropna()
        
        logger.info(f"Returns calculated. Shape: {self.returns.shape}")
        
        return self.returns
    
    def save_processed_data(self, output_dir: str = "data/processed"):
        """
        Save processed data to CSV files.
        
        Parameters
        ----------
        output_dir : str
            Directory to save processed data
        """
        if self.df is None:
            raise ValueError("No data to save")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save cleaned prices
        prices_path = output_path / "brent_clean.csv"
        self.df.to_csv(prices_path)
        logger.info(f"Saved cleaned prices to {prices_path}")
        
        # Save returns if calculated
        if self.returns is not None:
            returns_path = output_path / "brent_returns.csv"
            self.returns.to_csv(returns_path, header=['log_return'])
            logger.info(f"Saved returns to {returns_path}")
        
        return prices_path, returns_path if self.returns is not None else None


if __name__ == "__main__":
    # Example usage
    processor = BrentOilData()
    df = processor.load_data()
    df_clean = processor.clean_data()
    returns = processor.calculate_returns()
    processor.save_processed_data()