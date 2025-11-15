#!/usr/bin/env python3
"""
Temperature Analyzer for BuryatMyasoprom
Monitors and analyzes cold chain temperature data for compliance
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TemperatureStats:
    mean: float
    std: float
    min: float
    max: float
    violations: int
    compliance_rate: float

class TemperatureAnalyzer:
    def __init__(self, config_path: str = "config/temperature_config.json"):
        self.config = self._load_config(config_path)
        self.sensor_data = pd.DataFrame()
        self.alert_history = []
    
    def _load_config(self, config_path: str) -> Dict:
        """Load temperature monitoring configuration"""
        default_config = {
            "temperature_limits": {
                "BEEF": {"min": -18, "max": -15, "critical_min": -20, "critical_max": -12},
                "LAMB": {"min": -18, "max": -15, "critical_min": -20, "critical_max": -12},
                "HORSE": {"min": -20, "max": -18, "critical_min": -22, "critical_max": -15}
            },
            "monitoring": {
                "sampling_interval": 300,  # seconds
                "violation_threshold": 3,  # consecutive readings
                "alert_cooldown": 900,  # seconds between same-type alerts
                "data_retention_days": 90
            },
            "analysis": {
                "trend_window": 24,  # hours for trend analysis
                "seasonal_patterns": True,
                "anomaly_detection": True
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
        
        return default_config
    
    def load_sensor_data(self, data: List[Dict]) -> None:
        """Load temperature sensor data"""
        if not data:
            logger.warning("No sensor data provided")
            return
        
        df = pd.DataFrame(data)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        self.sensor_data = df
        logger.info(f"Loaded {len(df)} temperature readings")
    
    def analyze_temperature_compliance(self, batch_id: str, meat_type: str) -> Dict:
        """Analyze temperature compliance for a specific batch"""
        if self.sensor_data.empty:
            return {"error": "No sensor data available"}
        
        batch_data = self.sensor_data[self.sensor_data['batch_id'] == batch_id]
        if batch_data.empty:
            return {"error": f"No data found for batch {batch_id}"}
        
        limits = self.config["temperature_limits"].get(meat_type.upper())
        if not limits:
            return {"error": f"No temperature limits defined for {meat_type}"}
        
        temperatures = batch_data['temperature'].values
        timestamps = batch_data['timestamp'].values
        
        # Calculate basic statistics
        stats = self._calculate_temperature_stats(temperatures, limits)
        
        # Detect violations
        violations = self._detect_temperature_violations(temperatures, timestamps, limits, batch_id)
        
        # Analyze trends
        trends = self._analyze_temperature_trends(temperatures, timestamps)
        
        # Predict shelf life
        shelf_life_prediction = self._predict_shelf_life(temperatures, meat_type)
        
        return {
            "batch_id": batch_id,
            "meat_type": meat_type,
            "analysis_period": {
                "start": timestamps[0].isoformat() if len(timestamps) > 0 else None,
                "end": timestamps[-1].isoformat() if len(timestamps) > 0 else None,
                "duration_hours": len(temperatures) * self.config["monitoring"]["sampling_interval"] / 3600
            },
            "statistics": {
                "mean_temperature": round(stats.mean, 2),
                "temperature_std": round(stats.std, 2),
                "min_temperature": round(stats.min, 2),
                "max_temperature": round(stats.max, 2),
                "temperature_range": round(stats.max - stats.min, 2),
                "compliance_rate": round(stats.compliance_rate, 1),
                "violation_count": stats.violations
            },
            "violations": violations,
            "trend_analysis": trends,
            "shelf_life_prediction": shelf_life_prediction,
            "risk_assessment": self._assess_temperature_risk(stats, violations, meat_type),
            "recommendations": self._generate_temperature_recommendations(stats, violations),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _calculate_temperature_stats(self, temperatures: np.ndarray, limits: Dict) -> TemperatureStats:
        """Calculate temperature statistics"""
        mean_temp = np.mean(temperatures)
        std_temp = np.std(temperatures)
        min_temp = np.min(temperatures)
        max_temp = np.max(temperatures)
        
        # Count violations
        violations = np.sum((temperatures < limits["min"]) | (temperatures > limits["max"]))
        compliance_rate = (1 - violations / len(temperatures)) * 100 if len(temperatures) > 0 else 0
        
        return TemperatureStats(
            mean=mean_temp,
            std=std_temp,
            min=min_temp,
            max=max_temp,
            violations=int(violations),
            compliance_rate=compliance_rate
        )
    
    def _detect_temperature_violations(self, temperatures: np.ndarray, timestamps: np.ndarray, 
                                    limits: Dict, batch_id: str) -> List[Dict]:
        """Detect and classify temperature violations"""
        violations = []
        violation_threshold = self.config["monitoring"]["violation_threshold"]
        
        current_violation = None
        
        for i, (temp, timestamp) in enumerate(zip(temperatures, timestamps)):
            is_violation = temp < limits["min"] or temp > limits["max"]
            is_critical = temp < limits["critical_min"] or temp > limits["critical_max"]
            
            if is_violation:
                if current_violation is None:
                    # Start new violation
                    current_violation = {
                        "start_index": i,
                        "start_time": timestamp,
                        "min_temp": temp,
                        "max_temp": temp,
                        "type": "CRITICAL" if is_critical else "WARNING",
                        "duration": 1
                    }
                else:
                    # Continue existing violation
                    current_violation["min_temp"] = min(current_violation["min_temp"], temp)
                    current_violation["max_temp"] = max(current_violation["max_temp"], temp)
                    current_violation["duration"] += 1
                    if is_critical:
                        current_violation["type"] = "CRITICAL"
            else:
                if current_violation is not None:
                    # End violation if it lasted long enough
                    if current_violation["duration"] >= violation_threshold:
                        current_violation["end_time"] = timestamp
                        current_violation["end_index"] = i
                        violations.append(current_violation)
                        
                        # Generate alert for significant violations
                        if current_violation["duration"] > violation_threshold * 2:
                            self._generate_alert(batch_id, current_violation)
                    
                    current_violation = None
        
        # Handle ongoing violation at end of data
        if current_violation is not None and current_violation["duration"] >= violation_threshold:
            current_violation["end_time"] = timestamps[-1]
            current_violation["end_index"] = len(temperatures) - 1
            violations.append(current_violation)
        
        return violations
    
    def _analyze_temperature_trends(self, temperatures: np.ndarray, timestamps: np.ndarray) -> Dict:
        """Analyze temperature trends and patterns"""
        if len(temperatures) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Convert to pandas Series for easier analysis
        temp_series = pd.Series(temperatures, index=timestamps)
        
        # Calculate rolling statistics
        window_size = self.config["analysis"]["trend_window"]
        rolling_mean = temp_series.rolling(window=window_size, center=True).mean()
        rolling_std = temp_series.rolling(window=window_size, center=True).std()
        
        # Detect trends
        z = np.polyfit(range(len(temperatures)), temperatures, 1)
        trend_slope = z[0]
        
        # Detect anomalies
        anomalies = self._detect_temperature_anomalies(temperatures)
        
        return {
            "overall_trend": "increasing" if trend_slope > 0.01 else "decreasing" if trend_slope < -0.01 else "stable",
            "trend_strength": abs(trend_slope),
            "stability_score": 1 / (rolling_std.mean() + 0.001),  # Avoid division by zero
            "anomalies_detected": len(anomalies),
            "seasonal_patterns": self._detect_seasonal_patterns(temp_series),
            "predictive_insights": self._generate_predictive_insights(temp_series)
        }
    
    def _detect_temperature_anomalies(self, temperatures: np.ndarray) -> List[int]:
        """Detect anomalous temperature readings"""
        if len(temperatures) < 10:
            return []
        
        Q1 = np.percentile(temperatures, 25)
        Q3 = np.percentile(temperatures, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = []
        for i, temp in enumerate(temperatures):
            if temp < lower_bound or temp > upper_bound:
                anomalies.append(i)
        
        return anomalies
    
    def _detect_seasonal_patterns(self, temp_series: pd.Series) -> Dict:
        """Detect seasonal patterns in temperature data"""
        if len(temp_series) < 48:  # Need at least 48 readings for pattern detection
            return {"detected": False, "patterns": []}
        
        # Simple pattern detection based on time of day
        temp_series_with_hour = temp_series.copy()
        temp_series_with_hour.index = pd.to_datetime(temp_series_with_hour.index)
        hourly_means = temp_series_with_hour.groupby(temp_series_with_hour.index.hour).mean()
        
        patterns = []
        if hourly_means.std() > 0.5:  # Significant variation by hour
            peak_hour = hourly_means.idxmax()
            low_hour = hourly_means.idxmin()
            patterns.append(f"Daily pattern: peaks at {peak_hour}:00, lows at {low_hour}:00")
        
        return {
            "detected": len(patterns) > 0,
            "patterns": patterns,
            "variation_score": hourly_means.std() if len(patterns) > 0 else 0
        }
    
    def _generate_predictive_insights(self, temp_series: pd.Series) -> Dict:
        """Generate predictive insights from temperature data"""
        if len(temp_series) < 24:
            return {"available": False, "message": "Insufficient data for predictions"}
        
        # Simple linear regression for trend prediction
        recent_data = temp_series.tail(12)  # Last 12 readings
        if len(recent_data) < 2:
            return {"available": False, "message": "Not enough recent data"}
        
        x = np.arange(len(recent_data))
        y = recent_data.values
        slope, intercept = np.polyfit(x, y, 1)
        
        # Predict next 6 readings
        future_x = np.arange(len(recent_data), len(recent_data) + 6)
        predicted = slope * future_x + intercept
        
        return {
            "available": True,
            "predicted_trend": "warming" if slope > 0.1 else "cooling" if slope < -0.1 else "stable",
            "confidence": min(0.95, abs(slope) * 10),  # Simple confidence measure
            "next_6_readings_prediction": [round(temp, 2) for temp in predicted],
            "risk_of_violation": self._assess_future_violation_risk(predicted)
        }
    
    def _assess_future_violation_risk(self, predicted_temps: np.ndarray) -> str:
        """Assess risk of future temperature violations"""
        if any(temp > -12 or temp < -22 for temp in predicted_temps):
            return "HIGH"
        elif any(temp > -14 or temp < -20 for temp in predicted_temps):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _predict_shelf_life(self, temperatures: np.ndarray, meat_type: str) -> Dict:
        """Predict shelf life based on temperature history"""
        if len(temperatures) == 0:
            return {"available": False}
        
        # Base shelf life in days at ideal temperature
        base_shelf_life = {
            "BEEF": 365,
            "LAMB": 180,
            "HORSE": 365
        }.get(meat_type.upper(), 270)
        
        # Calculate temperature acceleration factor (Q10 model)
        ideal_temp = -18
        Q10 = 2.0  # Common value for frozen foods
        
        acceleration_factors = []
        for temp in temperatures:
            if temp > ideal_temp:
                factor = Q10 ** ((temp - ideal_temp) / 10)
                acceleration_factors.append(factor)
        
        if acceleration_factors:
            avg_acceleration = np.mean(acceleration_factors)
            adjusted_shelf_life = base_shelf_life / avg_acceleration
        else:
            adjusted_shelf_life = base_shelf_life
        
        quality_loss = (1 - (adjusted_shelf_life / base_shelf_life)) * 100
        
        return {
            "available": True,
            "base_shelf_life_days": base_shelf_life,
            "predicted_shelf_life_days": round(adjusted_shelf_life, 1),
            "quality_loss_percent": round(quality_loss, 1),
            "recommendation": "Immediate consumption" if adjusted_shelf_life < 30 else "Monitor closely" if adjusted_shelf_life < 90 else "Normal storage"
        }
    
    def _assess_temperature_risk(self, stats: TemperatureStats, violations: List[Dict], meat_type: str) -> Dict:
        """Assess overall temperature risk"""
        risk_score = 0
        
        # Base risk from compliance rate
        if stats.compliance_rate < 90:
            risk_score += 3
        elif stats.compliance_rate < 95:
            risk_score += 1
        
        # Risk from violations
        critical_violations = sum(1 for v in violations if v["type"] == "CRITICAL")
        if critical_violations > 0:
            risk_score += 3
        elif len(violations) > 5:
            risk_score += 2
        elif len(violations) > 2:
            risk_score += 1
        
        # Risk from temperature stability
        if stats.std > 2.0:
            risk_score += 2
        elif stats.std > 1.0:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        elif risk_score >= 1:
            risk_level = "LOW"
        else:
            risk_level = "VERY_LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "primary_factors": self._identify_risk_factors(stats, violations)
        }
    
    def _identify_risk_factors(self, stats: TemperatureStats, violations: List[Dict]) -> List[str]:
        """Identify primary risk factors"""
        factors = []
        
        if stats.compliance_rate < 95:
            factors.append(f"Low compliance rate ({stats.compliance_rate}%)")
        
        if stats.std > 1.5:
            factors.append("High temperature variability")
        
        critical_violations = sum(1 for v in violations if v["type"] == "CRITICAL")
        if critical_violations > 0:
            factors.append(f"{critical_violations} critical temperature violations")
        
        if stats.min < -20:
            factors.append("Very low temperatures detected")
        
        if stats.max > -12:
            factors.append("Very high temperatures detected")
        
        return factors
    
    def _generate_temperature_recommendations(self, stats: TemperatureStats, violations: List[Dict]) -> List[str]:
        """Generate recommendations based on temperature analysis"""
        recommendations = []
        
        if stats.compliance_rate < 95:
            recommendations.append("Review and calibrate temperature control equipment")
        
        if stats.std > 1.5:
            recommendations.append("Improve temperature stability in storage areas")
        
        if any(v["type"] == "CRITICAL" for v in violations):
            recommendations.append("Implement immediate corrective actions for critical violations")
        
        if len(violations) > 5:
            recommendations.append("Conduct staff training on proper temperature management")
            recommendations.append("Consider upgrading refrigeration equipment")
        
        if stats.mean > -16:
            recommendations.append("Lower average storage temperature to improve shelf life")
        
        return recommendations
    
    def _generate_alert(self, batch_id: str, violation: Dict):
        """Generate temperature alert"""
        alert = {
            "batch_id": batch_id,
            "alert_id": f"TEMP_ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": violation["type"],
            "message": f"Temperature violation detected: {violation['min_temp']}°C to {violation['max_temp']}°C for {violation['duration']} readings",
            "timestamp": datetime.now().isoformat(),
            "violation_details": violation,
            "acknowledged": False
        }
        
        self.alert_history.append(alert)
        logger.warning(f"Temperature alert generated: {alert['message']}")
    
    def get_active_alerts(self) -> List[Dict]:
        """Get unacknowledged temperature alerts"""
        return [alert for alert in self.alert_history if not alert["acknowledged"]]
    
    def generate_temperature_report(self, batch_id: str, meat_type: str) -> Dict:
        """Generate comprehensive temperature analysis report"""
        analysis = self.analyze_temperature_compliance(batch_id, meat_type)
        
        if "error" in analysis:
            return analysis
        
        report = {
            "report_id": f"TEMP_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "batch_id": batch_id,
            "meat_type": meat_type,
            "executive_summary": self._generate_executive_summary(analysis),
            "detailed_analysis": analysis,
            "compliance_certification": self._generate_compliance_certification(analysis),
            "next_steps": analysis["recommendations"],
            "report_generated": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        return report
    
    def _generate_executive_summary(self, analysis: Dict) -> Dict:
        """Generate executive summary of temperature analysis"""
        stats = analysis["statistics"]
        risk = analysis["risk_assessment"]
        
        return {
            "overall_status": "COMPLIANT" if stats["compliance_rate"] >= 95 else "NON-COMPLIANT",
            "key_metric": f"{stats['compliance_rate']}% temperature compliance",
            "risk_level": risk["risk_level"],
            "primary_concern": risk["primary_factors"][0] if risk["primary_factors"] else "None",
            "recommendation_priority": "HIGH" if risk["risk_level"] == "HIGH" else "MEDIUM" if len(analysis["recommendations"]) > 0 else "LOW"
        }
    
    def _generate_compliance_certification(self, analysis: Dict) -> Dict:
        """Generate compliance certification statement"""
        stats = analysis["statistics"]
        
        if stats["compliance_rate"] >= 98:
            status = "FULLY_COMPLIANT"
            statement = "Temperature control meets all regulatory requirements"
        elif stats["compliance_rate"] >= 95:
            status = "CONDITIONALLY_COMPLIANT"
            statement = "Temperature control meets regulatory requirements with minor deviations"
        else:
            status = "NON_COMPLIANT"
            statement = "Temperature control does not meet regulatory requirements"
        
        return {
            "status": status,
            "statement": statement,
            "compliance_rate": stats["compliance_rate"],
            "violation_count": stats["violation_count"],
            "certification_date": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    # Initialize temperature analyzer
    analyzer = TemperatureAnalyzer()
    
    # Generate sample sensor data
    sample_data = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(288):  # 24 hours of 5-minute readings
        timestamp = base_time + timedelta(minutes=5*i)
        # Simulate temperature with some variation
        base_temp = -17.5
        variation = np.sin(i/12) * 0.8 + np.random.normal(0, 0.3)
        temperature = base_temp + variation
        
        sample_data.append({
            "batch_id": "BATCH-2024-001",
            "sensor_id": "SENSOR-001",
            "temperature": round(temperature, 2),
            "timestamp": timestamp.isoformat()
        })
    
    # Load and analyze data
    analyzer.load_sensor_data(sample_data)
    analysis = analyzer.analyze_temperature_compliance("BATCH-2024-001", "BEEF")
    report = analyzer.generate_temperature_report("BATCH-2024-001", "BEEF")
    
    print("Temperature Analysis:")
    print(json.dumps(analysis, indent=2))
    
    print("\nActive Alerts:")
    for alert in analyzer.get_active_alerts():
        print(f"  - {alert['message']}")
