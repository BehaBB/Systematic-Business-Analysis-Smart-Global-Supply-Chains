"""
Alert System
AI Baikal Fish Plant
"""

class AlertSystem:
    def send_temperature_alert(self, sensor_id, current_temp, limit_temp):
        return f"ALERT: Sensor {sensor_id} temperature {current_temp}°C exceeds limit {limit_temp}°C"
    
    def send_document_alert(self, document_type, days_until_expiry):
        return f"REMINDER: {document_type} expires in {days_until_expiry} days"
