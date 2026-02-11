"""
Bayesian Change Point Detection for Brent oil prices using PyMC.
"""

import pymc as pm
import numpy as np
import pandas as pd
import arviz as az
from scipy import stats
import xarray as xr
from typing import Dict, Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')

class BayesianChangePointModel:
    """Bayesian change point detection model for time series data."""
    
    def __init__(self, data: pd.Series, model_config: Optional[Dict] = None):
        """
        Initialize the change point model.
        
        Parameters
        ----------
        data : pd.Series
            Time series data (preferably log returns for stationarity)
        model_config : dict, optional
            Configuration parameters for the model
        """
        self.data = data.dropna().values
        self.dates = data.dropna().index
        self.n_obs = len(self.data)
        
        # Default configuration
        self.config = {
            'model_type': 'single_change_point',
            'tau_prior': {'distribution': 'uniform', 'lower': 0, 'upper': self.n_obs},
            'mu_prior': {'distribution': 'normal', 'mu': 0, 'sigma': 1},
            'sigma_prior': {'distribution': 'halfnormal', 'sigma': 1},
            'sampling': {'draws': 3000, 'tune': 1000, 'chains': 4, 'target_accept': 0.99},
            'convergence': {'rhat_threshold': 1.01, 'ess_threshold': 400}
        }
        
        # Update with user configuration
        if model_config:
            self.config.update(model_config)
        
        self.model = None
        self.trace = None
        self.summary = None
        self.posterior = None
        
    def build_single_change_point_model(self):
        with pm.Model() as model:
            import pytensor.tensor as pt
            t = pt.arange(self.n_obs)

        # Continuous change point
            tau = pm.Normal(
            "tau",
            mu=self.n_obs / 2,
            sigma=self.n_obs / 10
            )

        # Smoothness of transition
            k = pm.Exponential("k", 1 / 5)

        # Regime means
            mu1 = pm.Normal("mu1", mu=0, sigma=0.02)
            mu2 = pm.Normal("mu2", mu=0, sigma=0.02)

            sigma = pm.HalfNormal("sigma", sigma=0.05)

        # Smooth transition
            w = pm.math.sigmoid((t - tau) / k)
            mean = mu1 * (1 - w) + mu2 * w

            pm.Normal("y", mu=mean, sigma=sigma, observed=self.data)

        self.model = model
        return model

    
    def build_multiple_change_points_model(self, n_changepoints: int = 3):
        """
        Build a Bayesian model with multiple change points.
        
        Parameters
        ----------
        n_changepoints : int
            Number of change points to detect
        """
        with pm.Model() as model:
            # Priors for change points (ordered)
            taus = pm.Dirichlet("taus", a=np.ones(n_changepoints + 1))
            changepoints = pm.Deterministic(
                "changepoints",
                pm.math.cumsum(taus * self.n_obs).astype(int)
            )
            
            # Priors for segment means
            mus = pm.Normal("mus", mu=0, sigma=1, shape=n_changepoints + 1)
            
            # Prior for standard deviation
            sigma = pm.HalfNormal("sigma", sigma=1)
            
            # Create mean array based on change points
            mean_array = np.zeros(self.n_obs)
            segment_idx = 0
            
            for i in range(self.n_obs):
                if segment_idx < n_changepoints and i >= changepoints[segment_idx]:
                    segment_idx += 1
                mean_array[i] = mus[segment_idx]
            
            mean = pm.Deterministic("mean", mean_array)
            
            # Likelihood
            likelihood = pm.Normal(
                "y",
                mu=mean,
                sigma=sigma,
                observed=self.data
            )
            
        self.model = model
        return model
    
    def sample(self, model_type: str = 'single', **kwargs):
        """
        Sample from the posterior distribution.
        
        Parameters
        ----------
        model_type : str
            'single' or 'multiple' change point model
        **kwargs
            Additional arguments for pm.sample()
            
        Returns
        -------
        az.InferenceData
            Sampling trace
        """
        # Build model
        if model_type == 'single':
            self.build_single_change_point_model()
        elif model_type == 'multiple':
            n_changepoints = kwargs.pop('n_changepoints', 3)
            self.build_multiple_change_points_model(n_changepoints)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Sampling parameters
        sampling_params = self.config['sampling'].copy()
        sampling_params.update(kwargs)
        
        print(f"Sampling with {sampling_params['chains']} chains, "
              f"{sampling_params['draws']} draws, {sampling_params['tune']} tuning steps...")
        
        # Run sampling
        with self.model:
            self.trace = pm.sample(**sampling_params)
        
        # Calculate summary statistics
        self.summary = az.summary(self.trace)
        
        # Extract posterior samples
        self.posterior = self.trace.posterior
        
        return self.trace
    
    def check_convergence(self):
        """
        Check MCMC convergence diagnostics.
        
        Returns
        -------
        dict
            Convergence diagnostics
        """
        if self.trace is None:
            raise ValueError("No trace available. Run sampling first.")
        
        diagnostics = {}
        
        # R-hat statistics
        rhat_max = self.summary['r_hat'].max()
        diagnostics['rhat_max'] = rhat_max
        diagnostics['rhat_converged'] = rhat_max < self.config['convergence']['rhat_threshold']
        
        # Effective sample size
        ess_min = self.summary['ess_bulk'].min()
        diagnostics['ess_min'] = ess_min
        diagnostics['ess_sufficient'] = ess_min > self.config['convergence']['ess_threshold']
        
        # Trace plots inspection (qualitative)
        diagnostics['trace_plots_ok'] = True  # Would need visual inspection
        
        # Monte Carlo standard error
        diagnostics['mcse_ratio_max'] = (self.summary['mcse_mean'] / self.summary['sd']).max()
        
        return diagnostics
    
    def get_change_point_posterior(self):
        """
        Extract posterior distribution of change point(s).
        
        Returns
        -------
        dict
            Change point posterior information
        """
        if self.trace is None:
            raise ValueError("No trace available. Run sampling first.")
        
        if 'tau' in self.trace.posterior:
            # Single change point model
            tau_samples = self.trace.posterior['tau'].values.flatten()
            
            # Convert to dates
            tau_dates = [self.dates[int(t)] if t < len(self.dates) else self.dates[-1] 
                        for t in tau_samples]
            
            # Calculate statistics
            tau_mean = int(tau_samples.mean())
            tau_median = int(np.median(tau_samples))


            
            tau_mode = int(stats.mode(tau_samples, keepdims=True)[0])
            tau_hdi = az.hdi(tau_samples, hdi_prob=0.95)
            
            return {
                'type': 'single',
                'samples': tau_samples,
                'dates': tau_dates,
                'mean': tau_mean,
                'median': tau_median,
                'mode': tau_mode,
                'mean_date': self.dates[tau_mean] if tau_mean < len(self.dates) else self.dates[-1],
                'median_date': self.dates[tau_median] if tau_median < len(self.dates) else self.dates[-1],
                'mode_date': self.dates[tau_mode] if tau_mode < len(self.dates) else self.dates[-1],
                'hdi_95': tau_hdi,
                'hdi_95_dates': (
                    self.dates[int(tau_hdi[0])] if tau_hdi[0] < len(self.dates) else self.dates[-1],
                    self.dates[int(tau_hdi[1])] if tau_hdi[1] < len(self.dates) else self.dates[-1]
                )
            }
        elif 'changepoints' in self.trace.posterior:
            # Multiple change points model
            changepoint_samples = self.trace.posterior['changepoints'].values
            
            results = []
            for i in range(changepoint_samples.shape[2]):  # For each change point
                cp_samples = changepoint_samples[:, :, i].flatten()
                cp_mean = int(cp_samples.mean())
                
                results.append({
                    'index': i,
                    'samples': cp_samples,
                    'mean': cp_mean,
                    'mean_date': self.dates[cp_mean] if cp_mean < len(self.dates) else self.dates[-1],
                    'hdi_95': az.hdi(cp_samples, hdi_prob=0.95)
                })
            
            return {'type': 'multiple', 'change_points': results}
        else:
            raise ValueError("No change point variables found in trace")
    
    def calculate_impact(self, window_before: int = 30, window_after: int = 30):
        """
        Calculate the impact of detected change points.
        
        Parameters
        ----------
        window_before : int
            Days before change point to analyze
        window_after : int
            Days after change point to analyze
            
        Returns
        -------
        dict
            Impact analysis results
        """
        if self.trace is None:
            raise ValueError("No trace available. Run sampling first.")
        
        change_point_info = self.get_change_point_posterior()
        
        if change_point_info['type'] == 'single':
            # Get the most probable change point
            tau_mode = change_point_info['mode']
            
            # Extract data around change point
            start_idx = max(0, tau_mode - window_before)
            end_idx = min(len(self.data), tau_mode + window_after)
            
            before_data = self.data[max(0, tau_mode - window_before):tau_mode]
            after_data = self.data[tau_mode:min(len(self.data), tau_mode + window_after)]
            
            # Calculate impact metrics
            impact = {
                'change_point_index': tau_mode,
                'change_point_date': change_point_info['mode_date'],
                'before': {
                    'mean': float(before_data.mean()),
                    'std': float(before_data.std()),
                    'n_obs': len(before_data)
                },
                'after': {
                    'mean': float(after_data.mean()),
                    'std': float(after_data.std()),
                    'n_obs': len(after_data)
                },
                'impact': {
                    'mean_change': float(after_data.mean() - before_data.mean()),
                    'percent_change': float((after_data.mean() - before_data.mean()) / before_data.mean() * 100),
                    'volatility_change': float(after_data.std() - before_data.std()),
                    'effect_size': float((after_data.mean() - before_data.mean()) / before_data.std())
                }
            }
            
            return impact
        else:
            # Handle multiple change points
            impacts = []
            for cp_info in change_point_info['change_points']:
                cp_idx = int(cp_info['mean'])
                
                before_data = self.data[max(0, cp_idx - window_before):cp_idx]
                after_data = self.data[cp_idx:min(len(self.data), cp_idx + window_after)]
                
                impact = {
                    'change_point_index': cp_idx,
                    'change_point_date': cp_info['mean_date'],
                    'before_mean': float(before_data.mean()),
                    'after_mean': float(after_data.mean()),
                    'mean_change': float(after_data.mean() - before_data.mean()),
                    'percent_change': float((after_data.mean() - before_data.mean()) / before_data.mean() * 100)
                }
                impacts.append(impact)
            
            return {'multiple_change_points': impacts}
    
    def save_results(self, output_dir: str = "models/saved"):
        """
        Save model results to disk.
        
        Parameters
        ----------
        output_dir : str
            Directory to save results
        """
        import pickle
        import json
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save model summary
        if self.summary is not None:
            self.summary.to_csv(output_path / "model_summary.csv")
        
        # Save trace (can be large)
        if self.trace is not None:
            az.to_netcdf(self.trace, output_path / "trace.netcdf")
        
        # Save change point information
        cp_info = self.get_change_point_posterior()
        with open(output_path / "change_points.pkl", 'wb') as f:
            pickle.dump(cp_info, f)
        
        # Save impact analysis
        impact = self.calculate_impact()
        with open(output_path / "impact_analysis.json", 'w') as f:
            json.dump(impact, f, indent=2, default=str)
        
        print(f"Results saved to {output_path}")
    
    def load_results(self, input_dir: str = "models/saved"):
        """
        Load previously saved model results.
        
        Parameters
        ----------
        input_dir : str
            Directory containing saved results
        """
        import pickle
        from pathlib import Path
        
        input_path = Path(input_dir)
        
        # Load trace
        trace_file = input_path / "trace.netcdf"
        if trace_file.exists():
            self.trace = az.from_netcdf(trace_file)
        
        # Load summary
        summary_file = input_path / "model_summary.csv"
        if summary_file.exists():
            self.summary = pd.read_csv(summary_file, index_col=0)
        
        print("Results loaded from disk")