"""
Forecasting Module
Handles demand forecasting logic for medication supply chain
"""

import numpy as np
import pandas as pd
from datetime import timedelta
from numpy.polynomial.polynomial import Polynomial


class MedicationForecaster:
    """AI-powered forecasting engine for medication demand"""
    
    def __init__(self, data, forecast_days=30):
        """
        Initialize forecaster
        
        Parameters:
        - data: DataFrame with daily usage data
        - forecast_days: Number of days to forecast ahead
        """
        self.data = data
        self.forecast_days = forecast_days
        self.model = None
        
    def fit_polynomial_model(self, degree=2):
        """
        Fit polynomial regression model to usage data
        
        Parameters:
        - degree: Polynomial degree (default: 2 for quadratic)
        
        Returns:
        - Fitted polynomial model
        """
        x = np.arange(len(self.data))
        y = self.data['daily_usage'].values
        
        self.model = Polynomial.fit(x, y, degree)
        return self.model
    
    def forecast(self):
        """
        Generate demand forecast
        
        Returns:
        - Dictionary with forecast values and dates
        """
        if self.model is None:
            self.fit_polynomial_model()
        
        # Generate future predictions
        x = np.arange(len(self.data))
        future_x = np.arange(len(self.data), len(self.data) + self.forecast_days)
        
        forecast_values = self.model(future_x)
        forecast_values = np.maximum(forecast_values, self.data['daily_usage'].min() * 0.8)
        
        # Generate forecast dates
        last_date = self.data.index[-1] if isinstance(self.data.index[0], pd.Timestamp) else self.data['date'].max()
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=self.forecast_days,
            freq='D'
        )
        
        # Calculate confidence intervals
        residuals = self.data['daily_usage'].values - self.model(x)
        std_error = np.std(residuals)
        upper_bound = forecast_values + (1.96 * std_error)
        lower_bound = np.maximum(forecast_values - (1.96 * std_error), 0)
        
        return {
            'dates': forecast_dates,
            'forecast': forecast_values,
            'upper_bound': upper_bound,
            'lower_bound': lower_bound,
            'std_error': std_error
        }
    
    def calculate_metrics(self):
        """
        Calculate forecast accuracy metrics
        
        Returns:
        - Dictionary with MAPE, MAE, RMSE
        """
        if self.model is None:
            self.fit_polynomial_model()
        
        x = np.arange(len(self.data))
        y_true = self.data['daily_usage'].values
        y_pred = self.model(x)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1))) * 100
        
        # MAE (Mean Absolute Error)
        mae = np.mean(np.abs(y_true - y_pred))
        
        # RMSE (Root Mean Square Error)
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        
        return {
            'MAPE': mape,
            'MAE': mae,
            'RMSE': rmse
        }