"""
Exploratory Data Analysis for Brent oil prices.
Includes time series decomposition, stationarity tests, and volatility analysis.
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import jarque_bera
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesAnalyzer:
    """Class for comprehensive time series analysis of Brent oil prices."""
    def __init__(self):
        self.jarque_bera=None

    def __init__(self, data, date_column='date', price_column='price'):
        """
        Initialize analyzer with time series data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Time series data with datetime index
        date_column : str
            Name of date column (if index is not datetime)
        price_column : str
            Name of price column
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            data = data.copy()
            data.index = pd.to_datetime(data[date_column])
        
        self.data = data
        self.price_series = data[price_column]
        self.date_column = date_column
        self.price_column = price_column
        
        # Calculate log returns
        self.log_returns = self._calculate_log_returns()
        
    def _calculate_log_returns(self):
        """Calculate log returns for stationarity analysis."""
        return np.log(self.price_series).diff().dropna()
    
    def decompose_series(self, period=252, model='additive'):
        """
        Decompose time series into trend, seasonal, and residual components.
        
        Parameters
        ----------
        period : int
            Period for seasonal decomposition (trading days in a year)
        model : str
            'additive' or 'multiplicative' decomposition
            
        Returns
        -------
        dict
            Decomposition results
        """
        decomposition = sm.tsa.seasonal_decompose(
            self.price_series,
            model=model,
            period=period,
            extrapolate_trend='freq'
        )
        
        return {
            'observed': decomposition.observed,
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid
        }
    
    def test_stationarity(self, series=None, test='both'):
        """
        Test time series stationarity using ADF and KPSS tests.
        
        Parameters
        ----------
        series : pd.Series, optional
            Series to test (default: price series)
        test : str
            'adf', 'kpss', or 'both'
            
        Returns
        -------
        dict
            Test results
        """
        if series is None:
            series = self.price_series
        
        results = {}
        
        if test in ['adf', 'both']:
            # Augmented Dickey-Fuller test
            adf_result = adfuller(series.dropna(), autolag='AIC')
            results['adf'] = {
                'statistic': adf_result[0],
                'p_value': adf_result[1],
                'critical_values': adf_result[4],
                'stationary': adf_result[1] < 0.05
            }
        
        if test in ['kpss', 'both']:
            # KPSS test
            try:
                kpss_result = kpss(series.dropna(), regression='c', nlags='auto')
                results['kpss'] = {
                    'statistic': kpss_result[0],
                    'p_value': kpss_result[1],
                    'critical_values': kpss_result[3],
                    'stationary': kpss_result[1] > 0.05
                }
            except:
                results['kpss'] = {'error': 'Test failed'}
        
        return results
    
    def analyze_volatility(self, window=30, garch_order=(1, 1)):
        """
        Analyze volatility patterns including rolling volatility and GARCH modeling.
        
        Parameters
        ----------
        window : int
            Window size for rolling statistics
        garch_order : tuple
            (p, q) order for GARCH model
            
        Returns
        -------
        dict
            Volatility analysis results
        """
        # Rolling statistics
        rolling_mean = self.log_returns.rolling(window=window).mean()
        rolling_std = self.log_returns.rolling(window=window).std()
        
        # Volatility clustering analysis
        abs_returns = np.abs(self.log_returns)
        
        # GARCH model fitting
        garch_results = {}
        try:
            garch_model = arch_model(self.log_returns.dropna() * 100, vol='Garch', 
                                   p=garch_order[0], q=garch_order[1])
            garch_fit = garch_model.fit(disp='off', show_warning=False)
            
            garch_results = {
                'params': garch_fit.params,
                'conditional_volatility': garch_fit.conditional_volatility / 100,
                'residuals': garch_fit.resid / 100,
                'aic': garch_fit.aic,
                'bic': garch_fit.bic
            }
        except Exception as e:
            garch_results = {'error': str(e)}
        
        return {
            'rolling_mean': rolling_mean,
            'rolling_std': rolling_std,
            'abs_returns': abs_returns,
            'garch': garch_results
        }
    
    def calculate_statistics(self):
        """Calculate comprehensive descriptive statistics."""
        stats_dict = {
            'price': {
                'mean': self.price_series.mean(),
                'median': self.price_series.median(),
                'std': self.price_series.std(),
                'skewness': self.price_series.skew(),
                'kurtosis': self.price_series.kurtosis(),
                'min': self.price_series.min(),
                'max': self.price_series.max(),
                'q1': self.price_series.quantile(0.25),
                'q3': self.price_series.quantile(0.75),
                'iqr': self.price_series.quantile(0.75) - self.price_series.quantile(0.25)
            },
            'log_returns': {
                'mean': self.log_returns.mean(),
                'std': self.log_returns.std(),
                'skewness': self.log_returns.skew(),
                'kurtosis': self.log_returns.kurtosis(),
                'sharpe': self.log_returns.mean() / self.log_returns.std() * np.sqrt(252),
                'var_95': self.log_returns.quantile(0.05),
                'cvar_95': self.log_returns[self.log_returns <= self.log_returns.quantile(0.05)].mean()
            }
        }
        
        return stats_dict
    
    def analyze_autocorrelation(self, lags=40):
        """
        Analyze autocorrelation and partial autocorrelation.
        
        Parameters
        ----------
        lags : int
            Number of lags to analyze
            
        Returns
        -------
        dict
            Autocorrelation analysis results
        """
        # ACF and PACF for prices
        acf_price = sm.tsa.acf(self.price_series.dropna(), nlags=lags)
        pacf_price = sm.tsa.pacf(self.price_series.dropna(), nlags=lags)
        
        # ACF and PACF for log returns
        acf_returns = sm.tsa.acf(self.log_returns.dropna(), nlags=lags)
        pacf_returns = sm.tsa.pacf(self.log_returns.dropna(), nlags=lags)
        
        # Ljung-Box test for returns
        lb_test = sm.stats.acorr_ljungbox(self.log_returns.dropna(), lags=[lags], return_df=True)
        
        return {
            'acf_price': acf_price,
            'pacf_price': pacf_price,
            'acf_returns': acf_returns,
            'pacf_returns': pacf_returns,
            'ljung_box': lb_test
        }
    
    
    def generate_report(self):
        """Generate comprehensive EDA report."""
        print("=" * 70)
        print("BRENT OIL PRICE - EXPLORATORY DATA ANALYSIS REPORT")
        print("=" * 70)
        
        # Basic statistics
        print(f"\n1. DATA OVERVIEW")
        print(f"   Period: {self.price_series.index.min().date()} to {self.price_series.index.max().date()}")
        print(f"   Observations: {len(self.price_series):,}")
        print(f"   Missing values: {self.price_series.isnull().sum()}")
        
        # Descriptive statistics
        stats = self.calculate_statistics()
        print(f"\n2. DESCRIPTIVE STATISTICS")
        print(f"   Price - Mean: ${stats['price']['mean']:.2f}")
        print(f"   Price - Std Dev: ${stats['price']['std']:.2f}")
        print(f"   Price - Range: ${stats['price']['min']:.2f} to ${stats['price']['max']:.2f}")
        print(f"   Log Returns - Mean: {stats['log_returns']['mean']:.6f}")
        print(f"   Log Returns - Std Dev: {stats['log_returns']['std']:.4f}")
        print(f"   Log Returns - Sharpe Ratio: {stats['log_returns']['sharpe']:.4f}")
        print(f"   Log Returns - Skewness: {stats['log_returns']['skewness']:.4f}")
        print(f"   Log Returns - Kurtosis: {stats['log_returns']['kurtosis']:.4f}")
        
        # Stationarity tests
        print(f"\n3. STATIONARITY TESTS")
        price_stationarity = self.test_stationarity(self.price_series, test='both')
        returns_stationarity = self.test_stationarity(self.log_returns, test='both')
        
        print(f"   Price - ADF p-value: {price_stationarity.get('adf', {}).get('p_value', 'N/A'):.6f}")
        print(f"   Price - KPSS p-value: {price_stationarity.get('kpss', {}).get('p_value', 'N/A'):.6f}")
        print(f"   Returns - ADF p-value: {returns_stationarity.get('adf', {}).get('p_value', 'N/A'):.6f}")
        print(f"   Returns - KPSS p-value: {returns_stationarity.get('kpss', {}).get('p_value', 'N/A'):.6f}")
        
        # Volatility analysis
        print(f"\n4. VOLATILITY ANALYSIS")
        print(f"   Returns Std Dev: {self.log_returns.std():.6f}")
        print(f"   Annualized Volatility: {self.log_returns.std() * np.sqrt(252):.4f}")
        
        # Distribution tests
        print(f"\n5. DISTRIBUTION TESTS")
        p_value = jarque_bera(self.log_returns.dropna())[1]
        print(f"   Jarque-Bera test p-value: {p_value:.6f}")
        


        #print(f"   Jarque-Bera test p-value: {self.jarque_bera(self.log_returns.dropna())[1]:.6f}")
        
        print("\n" + "=" * 70)
        
        return {
            'basic_info': {
                'period': (self.price_series.index.min(), self.price_series.index.max()),
                'observations': len(self.price_series),
                'missing': self.price_series.isnull().sum()
            },
            'statistics': stats,
            'stationarity': {
                'price': price_stationarity,
                'returns': returns_stationarity
            }
        }