"""
ROI Calculator
AI Baikal Fish Plant
"""

class ROICalculator:
    def calculate_roi(self, investment, annual_savings):
        return (annual_savings / investment) * 100
    
    def calculate_payback_period(self, investment, monthly_savings):
        return investment / monthly_savings
