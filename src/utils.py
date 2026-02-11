"""
Utility functions for Brent oil price analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

def ensure_directory(path):
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)

def save_json(data, filepath):
    """Save data as JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Saved JSON to {filepath}")

def load_json(filepath):
    """Load data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_pickle(data, filepath):
    """Save data as pickle file."""
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    print(f"Saved pickle to {filepath}")

def load_pickle(filepath):
    """Load data from pickle file."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def calculate_rolling_statistics(series, window=30):
    """
    Calculate rolling statistics for a time series.
    
    Parameters
    ----------
    series : pd.Series
        Time series data
    window : int
        Rolling window size
        
    Returns
    -------
    pd.DataFrame
        Rolling statistics
    """
    return pd.DataFrame({
        'mean': series.rolling(window=window).mean(),
        'std': series.rolling(window=window).std(),
        'min': series.rolling(window=window).min(),
        'max': series.rolling(window=window).max(),
        'median': series.rolling(window=window).median(),
        'q25': series.rolling(window=window).quantile(0.25),
        'q75': series.rolling(window=window).quantile(0.75)
    })

def find_nearest_events(change_point_date, events_df, n_events=5):
    """
    Find events nearest to a change point date.
    
    Parameters
    ----------
    change_point_date : pd.Timestamp
        Change point date
    events_df : pd.DataFrame
        Events dataframe with 'event_date' column
    n_events : int
        Number of nearest events to return
        
    Returns
    -------
    pd.DataFrame
        Nearest events with distance in days
    """
    events_df = events_df.copy()
    events_df['days_from_change'] = (events_df['event_date'] - change_point_date).dt.days.abs()
    nearest_events = events_df.nsmallest(n_events, 'days_from_change')
    
    return nearest_events.sort_values('event_date')

def format_currency(value):
    """Format value as currency."""
    return f"${value:,.2f}"

def format_percentage(value, decimals=2):
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"

def create_summary_table(impact_analysis, change_point_info, nearest_event):
    """
    Create a summary table for reporting.
    
    Parameters
    ----------
    impact_analysis : dict
        Impact analysis results
    change_point_info : dict
        Change point information
    nearest_event : pd.Series
        Nearest event information
        
    Returns
    -------
    pd.DataFrame
        Summary table
    """
    summary_data = {
        'Metric': [
            'Change Point Date',
            '95% HDI Start',
            '95% HDI End',
            'Nearest Event',
            'Event Date',
            'Days Difference',
            'Event Type',
            'Event Severity',
            'Mean Return Before',
            'Mean Return After',
            'Mean Change',
            'Percent Change',
            'Volatility Change',
            'Effect Size'
        ],
        'Value': [
            change_point_info['mode_date'].date(),
            change_point_info['hdi_95_dates'][0].date(),
            change_point_info['hdi_95_dates'][1].date(),
            nearest_event['event_name'],
            nearest_event['event_date'].date(),
            abs((nearest_event['event_date'] - change_point_info['mode_date']).days),
            nearest_event['event_type'],
            nearest_event['severity'],
            f"{impact_analysis['before']['mean']:.6f}",
            f"{impact_analysis['after']['mean']:.6f}",
            f"{impact_analysis['impact']['mean_change']:.6f}",
            f"{impact_analysis['impact']['percent_change']:.2f}%",
            f"{impact_analysis['impact']['volatility_change']:.6f}",
            f"{impact_analysis['impact']['effect_size']:.3f}"
        ]
    }
    
    return pd.DataFrame(summary_data)

def check_data_quality(df, date_column='date', price_column='price'):
    """
    Check data quality and report issues.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data to check
    date_column : str
        Date column name
    price_column : str
        Price column name
        
    Returns
    -------
    dict
        Data quality report
    """
    report = {
        'total_rows': len(df),
        'date_range': (df[date_column].min(), df[date_column].max()),
        'missing_dates': df[date_column].isnull().sum(),
        'missing_prices': df[price_column].isnull().sum(),
        'zero_prices': (df[price_column] == 0).sum(),
        'negative_prices': (df[price_column] < 0).sum(),
        'duplicate_dates': df[date_column].duplicated().sum(),
        'date_order_violations': (df[date_column].diff().dt.days < 0).sum()
    }
    
    # Calculate statistics
    report['price_statistics'] = {
        'mean': df[price_column].mean(),
        'median': df[price_column].median(),
        'std': df[price_column].std(),
        'min': df[price_column].min(),
        'max': df[price_column].max(),
        'q1': df[price_column].quantile(0.25),
        'q3': df[price_column].quantile(0.75)
    }
    
    return report