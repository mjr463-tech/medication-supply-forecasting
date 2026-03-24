"""
Risk Engine Module
Calculates shortage risk scores and reorder recommendations
"""

import numpy as np
import pandas as pd


class ShortageRiskEngine:
    """AI-powered shortage risk assessment and scoring"""
    
    def __init__(self, reorder_threshold=14):
        """
        Initialize risk engine
        
        Parameters:
        - reorder_threshold: Days of supply at which to reorder
        """
        self.reorder_threshold = reorder_threshold
    
    def calculate_risk_score(self, current_inventory, avg_daily_usage, lead_time):
        """
        Calculate shortage risk score (0-100)
        
        Parameters:
        - current_inventory: Current stock level (units)
        - avg_daily_usage: Average daily usage (units/day)
        - lead_time: Supplier lead time (days)
        
        Returns:
        - Risk score (0=low, 100=critical)
        """
        if avg_daily_usage == 0:
            return 0
        
        days_of_supply = current_inventory / avg_daily_usage
        
        # Risk scoring logic
        if days_of_supply < lead_time:
            # CRITICAL: Will run out before delivery arrives
            risk_score = 95
        elif days_of_supply < self.reorder_threshold:
            # HIGH: Below reorder point
            risk_score = 70
        elif days_of_supply < 30:
            # MEDIUM: Healthy but monitor
            risk_score = 40
        else:
            # LOW: Healthy inventory
            risk_score = 15
        
        return risk_score
    
    def calculate_shortage_probability(self, risk_score):
        """
        Calculate probability of shortage in next 7 days
        
        Parameters:
        - risk_score: Risk score (0-100)
        
        Returns:
        - Shortage probability (0-1)
        """
        if risk_score > 80:
            return 0.8
        elif risk_score > 60:
            return 0.5
        elif risk_score > 30:
            return 0.15
        else:
            return 0.02
    
    def calculate_reorder_point(self, avg_daily_usage, lead_time, safety_stock_days=5):
        """
        Calculate optimal reorder point
        
        Parameters:
        - avg_daily_usage: Average daily usage (units/day)
        - lead_time: Supplier lead time (days)
        - safety_stock_days: Safety stock buffer (days)
        
        Returns:
        - Reorder point (units)
        """
        return int(avg_daily_usage * (lead_time + safety_stock_days))
    
    def recommend_order_quantity(self, avg_daily_usage, days_to_forecast=30):
        """
        Recommend order quantity
        
        Parameters:
        - avg_daily_usage: Average daily usage (units/day)
        - days_to_forecast: How many days of supply to order
        
        Returns:
        - Recommended order quantity (units)
        """
        return int(avg_daily_usage * days_to_forecast)
    
    def generate_reorder_action(self, current_inventory, avg_daily_usage, lead_time, unit_cost):
        """
        Generate complete reorder recommendation
        
        Parameters:
        - current_inventory: Current stock (units)
        - avg_daily_usage: Average daily usage (units/day)
        - lead_time: Supplier lead time (days)
        - unit_cost: Cost per unit ($)
        
        Returns:
        - Dictionary with action, quantity, cost, urgency
        """
        days_of_supply = current_inventory / (avg_daily_usage + 1) if avg_daily_usage > 0 else 0
        
        if days_of_supply <= lead_time:
            action = "🔴 REORDER IMMEDIATELY"
            urgency = "CRITICAL"
        elif days_of_supply <= self.reorder_threshold:
            action = "🟡 REORDER SOON"
            urgency = "HIGH"
        elif days_of_supply <= 25:
            action = "🟢 PLAN REORDER"
            urgency = "NORMAL"
        else:
            action = "✅ NO ACTION NEEDED"
            urgency = "LOW"
        
        quantity = self.recommend_order_quantity(avg_daily_usage)
        cost = quantity * unit_cost
        days_until_reorder = max(0, int(days_of_supply - lead_time))
        
        return {
            'action': action,
            'reorder_quantity': quantity,
            'estimated_cost': cost,
            'urgency': urgency,
            'days_until_reorder': days_until_reorder
        }