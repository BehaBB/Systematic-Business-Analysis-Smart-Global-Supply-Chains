"""
Quality Metrics Calculator
AI Baikal Fish Plant
"""

class QualityCalculator:
    def calculate_first_pass_yield(self, total_units, defective_units):
        return ((total_units - defective_units) / total_units) * 100
    
    def calculate_defect_rate(self, total_units, defective_units):
        return (defective_units / total_units) * 100
    
    def generate_quality_report(self, production_data):
        total_units = sum([batch['units'] for batch in production_data])
        defective_units = sum([batch['defects'] for batch in production_data])
        
        fpy = self.calculate_first_pass_yield(total_units, defective_units)
        defect_rate = self.calculate_defect_rate(total_units, defective_units)
        
        return {
            'first_pass_yield': fpy,
            'defect_rate': defect_rate,
            'total_units': total_units,
            'defective_units': defective_units
        }
