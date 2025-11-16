# Data Processors

## temperature-monitoring.py
```python
"""
Temperature Monitoring System
AI Baikal Fish Plant
"""

import pandas as pd
from datetime import datetime

class TemperatureMonitor:
    def __init__(self):
        self.temperature_limits = {
            'frozen_fish': {'min': -18, 'max': -15},
            'chilled_fish': {'min': 0, 'max': 4}
        }
    
    def check_compliance(self, product_type, current_temp):
        limits = self.temperature_limits.get(product_type)
        if not limits:
            return False
        
        return limits['min'] <= current_temp <= limits['max']
    
    def generate_report(self, temperature_data):
        df = pd.DataFrame(temperature_data)
        compliance_rate = (df['compliant'].sum() / len(df)) * 100
        return {
            'compliance_rate': compliance_rate,
            'total_checks': len(df),
            'violations': len(df[df['compliant'] == False])
        }

# Usage example
if __name__ == "__main__":
    monitor = TemperatureMonitor()
    sample_data = [
        {'product': 'frozen_fish', 'temperature': -16, 'timestamp': datetime.now()},
        {'product': 'chilled_fish', 'temperature': 2, 'timestamp': datetime.now()}
    ]
    report = monitor.generate_report(sample_data)
    print(f"Compliance Rate: {report['compliance_rate']}%")
