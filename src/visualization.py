"""
Visualization utilities for Brent oil price analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates

def set_plot_style(style='seaborn-darkgrid'):
    """Set consistent plotting style."""
    plt.style.use(style)
    sns.set_palette("husl")
    
    # Custom colors
    colors = {
        'price': '#2E86AB',
        'change_point': '#A23B72',
        'before': '#3C91E6',
        'after': '#FA824C',
        'events': '#342E37',
        'trend': '#F24236',
        'volatility': '#7D82B8'
    }
    
    return colors

def plot_time_series_with_events(price_data, events_df, change_points=None, 
                                figsize=(15, 8), title=None):
    """
    Plot time series with event markers and change points.
    
    Parameters
    ----------
    price_data : pd.Series
        Time series data
    events_df : pd.DataFrame
        Events with 'event_date' and 'severity' columns
    change_points : list, optional
        List of change point dates
    figsize : tuple
        Figure size
    title : str, optional
        Plot title
    """
    colors = set_plot_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot price series
    ax.plot(price_data.index, price_data.values, 
            linewidth=1.5, color=colors['price'], label='Brent Price', alpha=0.8)
    
    # Add change points if provided
    if change_points:
        for i, cp_date in enumerate(change_points):
            ax.axvline(x=cp_date, color=colors['change_point'], 
                      linestyle='--', linewidth=2, alpha=0.8,
                      label=f'Change Point {i+1}' if i == 0 else None)
    
    # Add event markers with severity-based colors
    severity_colors = {
        'Very High': 'red',
        'High': 'orange',
        'Medium': 'yellow',
        'Low': 'green'
    }
    
    for _, event in events_df.iterrows():
        color = severity_colors.get(event['severity'], 'gray')
        ax.axvline(x=event['event_date'], color=color, 
                  linestyle=':', alpha=0.5, linewidth=1)
    
    # Custom legend for events
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=colors['price'], lw=2, label='Brent Price'),
    ]
    
    if change_points:
        legend_elements.append(
            Line2D([0], [0], color=colors['change_point'], linestyle='--', 
                  lw=2, label='Change Point')
        )
    
    for severity, color in severity_colors.items():
        legend_elements.append(
            Line2D([0], [0], color=color, linestyle=':', 
                  lw=1, label=f'{severity} Event')
        )
    
    ax.legend(handles=legend_elements, loc='upper left')
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Brent Oil Price with Events and Change Points', 
                    fontsize=16, fontweight='bold')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (USD per barrel)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis for dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig, ax

def plot_change_point_analysis(price_data, change_point_date, window_days=60,
                              figsize=(15, 10)):
    """
    Create comprehensive change point analysis visualization.
    
    Parameters
    ----------
    price_data : pd.Series
        Price time series
    change_point_date : pd.Timestamp
        Detected change point date
    window_days : int
        Days to show before/after change point
    figsize : tuple
        Figure size
    """
    colors = set_plot_style()
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # 1. Full series with change point
    ax1 = axes[0, 0]
    ax1.plot(price_data.index, price_data.values, 
            linewidth=1, color=colors['price'], alpha=0.7)
    ax1.axvline(x=change_point_date, color=colors['change_point'], 
               linestyle='--', linewidth=2)
    ax1.set_title('Full Price Series with Change Point', fontsize=14)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price (USD)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Zoomed window around change point
    ax2 = axes[0, 1]
    window_start = change_point_date - pd.Timedelta(days=window_days)
    window_end = change_point_date + pd.Timedelta(days=window_days)
    
    mask = (price_data.index >= window_start) & (price_data.index <= window_end)
    window_data = price_data[mask]
    
    ax2.plot(window_data.index, window_data.values, 
            linewidth=1.5, color=colors['price'])
    ax2.axvline(x=change_point_date, color=colors['change_point'], 
               linestyle='--', linewidth=2)
    
    # Highlight before/after regions
    ax2.axvspan(window_start, change_point_date, alpha=0.1, 
               color=colors['before'], label='Before')
    ax2.axvspan(change_point_date, window_end, alpha=0.1, 
               color=colors['after'], label='After')
    
    ax2.set_title(f'{window_days}-Day Window Around Change Point', fontsize=14)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Price (USD)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # 3. Rolling statistics before/after
    ax3 = axes[1, 0]
    
    # Calculate rolling mean and std
    rolling_window = 10
    rolling_mean = price_data.rolling(window=rolling_window).mean()
    rolling_std = price_data.rolling(window=rolling_window).std()
    
    # Plot before change point
    before_mask = price_data.index < change_point_date
    ax3.plot(price_data.index[before_mask], rolling_mean[before_mask], 
            color=colors['before'], label='Rolling Mean (Before)', alpha=0.7)
    ax3.fill_between(price_data.index[before_mask],
                     rolling_mean[before_mask] - rolling_std[before_mask],
                     rolling_mean[before_mask] + rolling_std[before_mask],
                     color=colors['before'], alpha=0.2, label='±1 STD')
    
    # Plot after change point
    after_mask = price_data.index >= change_point_date
    ax3.plot(price_data.index[after_mask], rolling_mean[after_mask], 
            color=colors['after'], label='Rolling Mean (After)', alpha=0.7)
    ax3.fill_between(price_data.index[after_mask],
                     rolling_mean[after_mask] - rolling_std[after_mask],
                     rolling_mean[after_mask] + rolling_std[after_mask],
                     color=colors['after'], alpha=0.2)
    
    ax3.axvline(x=change_point_date, color=colors['change_point'], 
               linestyle='--', linewidth=2, label='Change Point')
    
    ax3.set_title(f'{rolling_window}-Day Rolling Statistics', fontsize=14)
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Price (USD)')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # 4. Distribution comparison
    ax4 = axes[1, 1]
    
    # Extract data before and after
    before_data = price_data[before_mask].dropna()
    after_data = price_data[after_mask].dropna()
    
    # Histograms
    bins = 50
    ax4.hist(before_data, bins=bins, density=True, alpha=0.5, 
            color=colors['before'], label=f'Before (n={len(before_data)})')
    ax4.hist(after_data, bins=bins, density=True, alpha=0.5,
            color=colors['after'], label=f'After (n={len(after_data)})')
    
    # Add vertical lines for means
    ax4.axvline(before_data.mean(), color=colors['before'], 
               linestyle='--', linewidth=2, label=f'Before Mean: ${before_data.mean():.2f}')
    ax4.axvline(after_data.mean(), color=colors['after'], 
               linestyle='--', linewidth=2, label=f'After Mean: ${after_data.mean():.2f}')
    
    ax4.set_title('Price Distribution Before/After Change', fontsize=14)
    ax4.set_xlabel('Price (USD)')
    ax4.set_ylabel('Density')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle(f'Change Point Analysis: {change_point_date.date()}', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    return fig, axes

def plot_model_diagnostics(trace, var_names=None, figsize=(15, 10)):
    """
    Plot MCMC diagnostics for model evaluation.
    
    Parameters
    ----------
    trace : az.InferenceData
        PyMC trace
    var_names : list, optional
        Variables to plot
    figsize : tuple
        Figure size
    """
    import arviz as az
    
    if var_names is None:
        var_names = list(trace.posterior.data_vars)[:4]
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()
    
    for i, var in enumerate(var_names[:4]):
        # Trace plot
        ax = axes[i]
        var_data = trace.posterior[var].values.flatten()
        
        # Plot trace
        ax.plot(var_data, alpha=0.7)
        ax.set_title(f'Trace Plot: {var}', fontsize=12)
        ax.set_xlabel('Sample')
        ax.set_ylabel('Value')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('MCMC Diagnostics - Trace Plots', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    return fig, axes

def plot_posterior_distributions(trace, var_names=None, figsize=(15, 8)):
    """
    Plot posterior distributions with HDI intervals.
    
    Parameters
    ----------
    trace : az.InferenceData
        PyMC trace
    var_names : list, optional
        Variables to plot
    figsize : tuple
        Figure size
    """
    import arviz as az
    
    if var_names is None:
        var_names = list(trace.posterior.data_vars)
    
    n_vars = len(var_names)
    n_cols = min(3, n_vars)
    n_rows = (n_vars + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    
    if n_vars == 1:
        axes = [axes]
    elif n_rows > 1 and n_cols > 1:
        axes = axes.flatten()
    
    for i, var in enumerate(var_names):
        ax = axes[i] if i < len(axes) else None
        if ax is None:
            break
            
        # Plot posterior density
        var_data = trace.posterior[var].values.flatten()
        
        # Histogram
        ax.hist(var_data, bins=50, density=True, alpha=0.7, 
               edgecolor='black', linewidth=0.5)
        
        # Add HDI
        hdi = az.hdi(var_data, hdi_prob=0.95)
        ax.axvspan(hdi[0], hdi[1], alpha=0.2, color='gray', label='95% HDI')
        
        # Add mean line
        mean_val = var_data.mean()
        ax.axvline(mean_val, color='red', linestyle='--', 
                  linewidth=2, label=f'Mean: {mean_val:.3f}')
        
        ax.set_title(f'Posterior: {var}', fontsize=12)
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Posterior Distributions', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    return fig, axes