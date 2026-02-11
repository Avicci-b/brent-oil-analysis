"""
Flask Backend API for Brent Oil Price Analysis Dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import json
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Paths to data files
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
MODELS_DIR = BASE_DIR / "models"

class DataManager:
    """Manages data loading and processing for the dashboard."""
    
    def __init__(self):
        self.price_data = None
        self.events_data = None
        self.change_points = None
        self.impact_analysis = None
        self.load_all_data()
    
    def load_all_data(self):
        """Load all required data files."""
        try:
            # Load price data
            price_path = DATA_DIR / "processed" / "brent_clean.csv"
            if price_path.exists():
                self.price_data = pd.read_csv(price_path, parse_dates=['date'])
                self.price_data.set_index('date', inplace=True)
                print(f"Loaded price data: {len(self.price_data)} records")
            else:
                print(f"Price data not found at {price_path}")
            
            # Load events data
            events_path = DATA_DIR / "processed" / "historical_events.csv"
            if events_path.exists():
                self.events_data = pd.read_csv(events_path, parse_dates=['event_date'])
                print(f"Loaded events data: {len(self.events_data)} events")
            
            # Load change points
            cp_path = MODELS_DIR / "saved" / "single_change_point" / "change_points.pkl"
            if cp_path.exists():
                with open(cp_path, 'rb') as f:
                    self.change_points = pickle.load(f)
                print(f"Loaded change points data")
            
            # Load impact analysis
            impact_path = RESULTS_DIR / "tables" / "impact_analysis.csv"
            if impact_path.exists():
                self.impact_analysis = pd.read_csv(impact_path, parse_dates=['change_point_date'])
                print(f"Loaded impact analysis data")
                
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def get_price_data(self, start_date=None, end_date=None):
        """Get price data within date range."""
        if self.price_data is None:
            return None
        
        data = self.price_data.copy()
        
        if start_date:
            data = data[data.index >= pd.to_datetime(start_date)]
        if end_date:
            data = data[data.index <= pd.to_datetime(end_date)]
        
        return data.reset_index().to_dict('records')
    
    def get_events_data(self, event_type=None, severity=None, start_date=None, end_date=None):
        """Get events data with optional filters."""
        if self.events_data is None:
            return None
        
        data = self.events_data.copy()
        
        if event_type and event_type != 'all':
            data = data[data['event_type'] == event_type]
        if severity and severity != 'all':
            data = data[data['severity'] == severity]
        if start_date:
            data = data[data['event_date'] >= pd.to_datetime(start_date)]
        if end_date:
            data = data[data['event_date'] <= pd.to_datetime(end_date)]
        
        return data.to_dict('records')
    
    def get_change_points(self):
        """Get detected change points."""
        if self.change_points is None:
            return None
        
        return self.change_points
    
    def get_impact_analysis(self):
        """Get impact analysis results."""
        if self.impact_analysis is None:
            return None
        
        return self.impact_analysis.to_dict('records')
    
    def get_summary_stats(self):
        """Get summary statistics."""
        if self.price_data is None:
            return None
        
        stats = {
            'total_observations': len(self.price_data),
            'date_range': {
                'start': self.price_data.index.min().strftime('%Y-%m-%d'),
                'end': self.price_data.index.max().strftime('%Y-%m-%d')
            },
            'price_stats': {
                'mean': float(self.price_data['price'].mean()),
                'median': float(self.price_data['price'].median()),
                'std': float(self.price_data['price'].std()),
                'min': float(self.price_data['price'].min()),
                'max': float(self.price_data['price'].max())
            }
        }
        
        if self.events_data is not None:
            stats['total_events'] = len(self.events_data)
            stats['events_by_type'] = self.events_data['event_type'].value_counts().to_dict()
            stats['events_by_severity'] = self.events_data['severity'].value_counts().to_dict()
        
        return stats
    
    def get_price_around_event(self, event_date, window_days=30):
        """Get price data around a specific event."""
        if self.price_data is None:
            return None
        
        event_date = pd.to_datetime(event_date)
        start_date = event_date - pd.Timedelta(days=window_days)
        end_date = event_date + pd.Timedelta(days=window_days)
        
        mask = (self.price_data.index >= start_date) & (self.price_data.index <= end_date)
        event_data = self.price_data[mask].copy()
        
        # Calculate metrics
        before_mask = event_data.index < event_date
        after_mask = event_data.index >= event_date
        
        if before_mask.any() and after_mask.any():
            before_mean = event_data[before_mask]['price'].mean()
            after_mean = event_data[after_mask]['price'].mean()
            percent_change = ((after_mean - before_mean) / before_mean) * 100
        else:
            before_mean = after_mean = percent_change = None
        
        return {
            'price_data': event_data.reset_index().to_dict('records'),
            'metrics': {
                'before_mean': float(before_mean) if before_mean else None,
                'after_mean': float(after_mean) if after_mean else None,
                'percent_change': float(percent_change) if percent_change else None
            }
        }

# Initialize data manager
data_manager = DataManager()

# API Routes
@app.route('/')
def index():
    """Home endpoint."""
    return jsonify({
        'message': 'Brent Oil Price Analysis Dashboard API',
        'version': '1.0.0',
        'endpoints': {
            '/api/prices': 'Get historical price data',
            '/api/events': 'Get historical events',
            '/api/change-points': 'Get detected change points',
            '/api/impact': 'Get impact analysis',
            '/api/stats': 'Get summary statistics',
            '/api/event-impact/<event_date>': 'Get price data around specific event'
        }
    })

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get historical price data with optional date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data = data_manager.get_price_data(start_date, end_date)
    
    if data is None:
        return jsonify({'error': 'Price data not available'}), 500
    
    return jsonify({
        'success': True,
        'count': len(data),
        'data': data
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get historical events with optional filters."""
    event_type = request.args.get('type', 'all')
    severity = request.args.get('severity', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data = data_manager.get_events_data(event_type, severity, start_date, end_date)
    
    if data is None:
        return jsonify({'error': 'Events data not available'}), 500
    
    return jsonify({
        'success': True,
        'count': len(data),
        'data': data
    })

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Get detected change points."""
    data = data_manager.get_change_points()
    
    if data is None:
        return jsonify({'error': 'Change points data not available'}), 500
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/impact', methods=['GET'])
def get_impact():
    """Get impact analysis results."""
    data = data_manager.get_impact_analysis()
    
    if data is None:
        return jsonify({'error': 'Impact analysis data not available'}), 500
    
    return jsonify({
        'success': True,
        'count': len(data),
        'data': data
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get summary statistics."""
    stats = data_manager.get_summary_stats()
    
    if stats is None:
        return jsonify({'error': 'Statistics not available'}), 500
    
    return jsonify({
        'success': True,
        'data': stats
    })

@app.route('/api/event-impact/<event_date>', methods=['GET'])
def get_event_impact(event_date):
    """Get price data around a specific event."""
    try:
        window_days = int(request.args.get('window_days', 30))
        data = data_manager.get_price_around_event(event_date, window_days)
        
        if data is None:
            return jsonify({'error': 'Event impact analysis not available'}), 500
        
        return jsonify({
            'success': True,
            'event_date': event_date,
            'window_days': window_days,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/volatility', methods=['GET'])
def get_volatility():
    """Calculate volatility metrics."""
    if data_manager.price_data is None:
        return jsonify({'error': 'Price data not available'}), 500
    
    # Calculate log returns
    returns = np.log(data_manager.price_data['price']).diff().dropna()
    
    # Calculate volatility metrics
    volatility = {
        'daily_volatility': float(returns.std()),
        'annualized_volatility': float(returns.std() * np.sqrt(252)),
        'rolling_30d_vol': float(returns.rolling(30).std().iloc[-1] * np.sqrt(252)),
        'rolling_90d_vol': float(returns.rolling(90).std().iloc[-1] * np.sqrt(252)),
        'max_drawdown': float((data_manager.price_data['price'] / data_manager.price_data['price'].cummax() - 1).min())
    }
    
    return jsonify({
        'success': True,
        'data': volatility
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)