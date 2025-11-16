"""
Performance Analytics
AI Baikal Fish Plant
"""

class PerformanceAnalytics:
    def calculate_oee(self, availability, performance, quality):
        return (availability * performance * quality) / 10000
    
    def analyze_trends(self, data_points):
        if len(data_points) < 2:
            return "Insufficient data"
        
        trend = "stable"
        if data_points[-1] > data_points[0]:
            trend = "improving"
        elif data_points[-1] < data_points[0]:
            trend = "declining"
        
        return trend
