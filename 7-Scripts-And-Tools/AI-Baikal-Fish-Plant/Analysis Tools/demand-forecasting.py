"""
Demand Forecasting
AI Baikal Fish Plant
"""

class DemandForecasting:
    def predict_demand(self, historical_data, seasonality_factor=1.0):
        avg_demand = sum(historical_data) / len(historical_data)
        return avg_demand * seasonality_factor
    
    def calculate_safety_stock(self, avg_demand, lead_time, service_level=1.65):
        return service_level * (avg_demand ** 0.5) * (lead_time ** 0.5)
