#!/usr/bin/env python3
"""
Quality Tracker Prototype
Real-time quality monitoring and compliance tracking for fish processing
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    CONDITIONAL = "CONDITIONAL"
    PENDING = "PENDING"

class CheckType(Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    IN_PROCESS = "IN_PROCESS"
    FINAL_PRODUCT = "FINAL_PRODUCT"

@dataclass
class QualityCheck:
    check_id: str
    batch_id: str
    check_type: CheckType
    inspector_id: str
    check_time: datetime
    parameters: Dict[str, float]
    overall_score: float
    status: QualityStatus
    comments: str

@dataclass
class QualityStandard:
    product_type: str
    parameter_limits: Dict[str, Dict[str, float]]  # min, max, target
    required_checks: List[CheckType]
    compliance_threshold: float

class QualityTracker:
    def __init__(self):
        self.quality_standards = self._load_quality_standards()
        self.quality_history = []
        
    def _load_quality_standards(self) -> Dict[str, QualityStandard]:
        """Load quality standards for different product types"""
        return {
            "SMOKED_OMUL": QualityStandard(
                product_type="SMOKED_OMUL",
                parameter_limits={
                    "appearance_score": {"min": 8.0, "max": 10.0, "target": 9.0},
                    "texture_score": {"min": 7.0, "max": 10.0, "target": 8.5},
                    "smell_score": {"min": 9.0, "max": 10.0, "target": 9.5},
                    "salt_content": {"min": 2.0, "max": 3.5, "target": 2.8},
                    "bacterial_count": {"min": 0, "max": 1000, "target": 100}
                },
                required_checks=[CheckType.RAW_MATERIAL, CheckType.IN_PROCESS, CheckType.FINAL_PRODUCT],
                compliance_threshold=90.0
            ),
            "FROZEN_SIG": QualityStandard(
                product_type="FROZEN_SIG",
                parameter_limits={
                    "appearance_score": {"min": 7.0, "max": 10.0, "target": 8.0},
                    "texture_score": {"min": 8.0, "max": 10.0, "target": 9.0},
                    "temperature": {"min": -25.0, "max": -18.0, "target": -20.0},
                    "ice_crystal_size": {"min": 0, "max": 0.5, "target": 0.1}
                },
                required_checks=[CheckType.RAW_MATERIAL, CheckType.FINAL_PRODUCT],
                compliance_threshold=85.0
            ),
            "DRIED_GRAYLING": QualityStandard(
                product_type="DRIED_GRAYLING",
                parameter_limits={
                    "appearance_score": {"min": 7.0, "max": 10.0, "target": 8.0},
                    "texture_score": {"min": 8.0, "max": 10.0, "target": 8.5},
                    "moisture_content": {"min": 15.0, "max": 25.0, "target": 20.0},
                    "salt_content": {"min": 3.0, "max": 5.0, "target": 4.0}
                },
                required_checks=[CheckType.RAW_MATERIAL, CheckType.IN_PROCESS, CheckType.FINAL_PRODUCT],
                compliance_threshold=88.0
            )
        }
    
    def record_quality_check(self, batch_id: str, product_type: str, 
                           check_type: CheckType, parameters: Dict[str, float],
                           inspector_id: str, comments: str = "") -> Dict:
        """Record a quality check and evaluate against standards"""
        
        if product_type not in self.quality_standards:
            return {
                "success": False,
                "error": f"No quality standards defined for {product_type}",
                "check_id": None
            }
        
        # Validate parameters against standard
        validation_result = self._validate_parameters(product_type, parameters)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": f"Invalid parameters: {validation_result['errors']}",
                "check_id": None
            }
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(product_type, parameters)
        
        # Determine status
        status = self._determine_quality_status(product_type, overall_score, parameters)
        
        # Create quality check record
        check_id = f"QC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        quality_check = QualityCheck(
            check_id=check_id,
            batch_id=batch_id,
            check_type=check_type,
            inspector_id=inspector_id,
            check_time=datetime.now(),
            parameters=parameters,
            overall_score=overall_score,
            status=status,
            comments=comments
        )
        
        # Store in history
        self.quality_history.append(quality_check)
        
        # Generate alerts if needed
        if status == QualityStatus.FAILED:
            self._generate_quality_alert(quality_check)
        
        return {
            "success": True,
            "check_id": check_id,
            "quality_check": self._format_quality_check(quality_check),
            "compliance_report": self._generate_compliance_report(quality_check, product_type),
            "recommendations": self._generate_quality_recommendations(quality_check, product_type)
        }
    
    def _validate_parameters(self, product_type: str, parameters: Dict[str, float]) -> Dict:
        """Validate quality parameters against defined standards"""
        standard = self.quality_standards[product_type]
        errors = []
        
        for param_name, param_value in parameters.items():
            if param_name not in standard.parameter_limits:
                errors.append(f"Unknown parameter: {param_name}")
                continue
            
            limits = standard.parameter_limits[param_name]
            if param_value < limits["min"] or param_value > limits["max"]:
                errors.append(
                    f"Parameter {param_name} value {param_value} outside limits "
                    f"[{limits['min']}, {limits['max']}]"
                )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _calculate_overall_score(self, product_type: str, parameters: Dict[str, float]) -> float:
        """Calculate overall quality score based on parameters"""
        standard = self.quality_standards[product_type]
        total_score = 0.0
        parameter_count = 0
        
        for param_name, param_value in parameters.items():
            if param_name in standard.parameter_limits:
                limits = standard.parameter_limits[param_name]
                target = limits["target"]
                
                # Calculate score based on deviation from target
                if limits["min"] == limits["max"]:
                    # Boolean parameter (pass/fail)
                    score = 10.0 if param_value == target else 0.0
                else:
                    # Continuous parameter
                    deviation = abs(param_value - target)
                    range_size = limits["max"] - limits["min"]
                    normalized_deviation = deviation / (range_size / 2)
                    score = max(0, 10 - (normalized_deviation * 10))
                
                total_score += score
                parameter_count += 1
        
        return round(total_score / parameter_count, 1) if parameter_count > 0 else 0.0
    
    def _determine_quality_status(self, product_type: str, overall_score: float, 
                                parameters: Dict[str, float]) -> QualityStatus:
        """Determine quality status based on score and critical parameters"""
        standard = self.quality_standards[product_type]
        
        # Check for critical failures
        critical_parameters = ["bacterial_count", "temperature"]
        for param in critical_parameters:
            if param in parameters:
                limits = standard.parameter_limits.get(param, {})
                if (param in limits and 
                    (parameters[param] < limits.get("min", 0) or 
                     parameters[param] > limits.get("max", float('inf')))):
                    return QualityStatus.FAILED
        
        # Determine based on overall score
        if overall_score >= standard.compliance_threshold:
            return QualityStatus.PASSED
        elif overall_score >= standard.compliance_threshold - 10:
            return QualityStatus.CONDITIONAL
        else:
            return QualityStatus.FAILED
    
    def _generate_quality_alert(self, quality_check: QualityCheck):
        """Generate quality alert for failed checks"""
        alert = {
            "alert_id": f"QUALITY-ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "batch_id": quality_check.batch_id,
            "check_id": quality_check.check_id,
            "severity": "HIGH" if quality_check.status == QualityStatus.FAILED else "MEDIUM",
            "message": f"Quality check {quality_check.check_id} failed for batch {quality_check.batch_id}",
            "parameters": quality_check.parameters,
            "overall_score": quality_check.overall_score,
            "generated_at": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        logger.warning(f"Quality alert generated: {alert['message']}")
        # In production, this would send notifications to relevant staff
    
    def _format_quality_check(self, quality_check: QualityCheck) -> Dict:
        """Format quality check for response"""
        return {
            "check_id": quality_check.check_id,
            "batch_id": quality_check.batch_id,
            "check_type": quality_check.check_type.value,
            "inspector_id": quality_check.inspector_id,
            "check_time": quality_check.check_time.isoformat(),
            "parameters": quality_check.parameters,
            "overall_score": quality_check.overall_score,
            "status": quality_check.status.value,
            "comments": quality_check.comments
        }
    
    def _generate_compliance_report(self, quality_check: QualityCheck, product_type: str) -> Dict:
        """Generate compliance report for quality check"""
        standard = self.quality_standards[product_type]
        
        parameter_compliance = {}
        for param_name, param_value in quality_check.parameters.items():
            if param_name in standard.parameter_limits:
                limits = standard.parameter_limits[param_name]
                within_limits = limits["min"] <= param_value <= limits["max"]
                parameter_compliance[param_name] = {
                    "value": param_value,
                    "within_limits": within_limits,
                    "limits": limits
                }
        
        return {
            "product_type": product_type,
            "overall_compliance_score": quality_check.overall_score,
            "compliance_threshold": standard.compliance_threshold,
            "meets_standard": quality_check.overall_score >= standard.compliance_threshold,
            "parameter_compliance": parameter_compliance,
            "required_checks_completed": self._get_completed_checks(quality_check.batch_id, product_type)
        }
    
    def _get_completed_checks(self, batch_id: str, product_type: str) -> List[str]:
        """Get list of completed quality checks for a batch"""
        standard = self.quality_standards[product_type]
        batch_checks = [qc for qc in self.quality_history if qc.batch_id == batch_id]
        
        completed_types = [qc.check_type.value for qc in batch_checks]
        missing_types = [ct.value for ct in standard.required_checks if ct.value not in completed_types]
        
        return {
            "completed": completed_types,
            "missing": missing_types,
            "all_required_completed": len(missing_types) == 0
        }
    
    def _generate_quality_recommendations(self, quality_check: QualityCheck, product_type: str) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        standard = self.quality_standards[product_type]
        
        for param_name, param_value in quality_check.parameters.items():
            if param_name in standard.parameter_limits:
                limits = standard.parameter_limits[param_name]
                target = limits["target"]
                
                if param_value < limits["min"] or param_value > limits["max"]:
                    recommendations.append(
                        f"Adjust {param_name}: current {param_value}, target {target}"
                    )
                elif abs(param_value - target) > (limits["max"] - limits["min"]) * 0.1:
                    recommendations.append(
                        f"Optimize {param_name}: current {param_value}, closer to target {target}"
                    )
        
        if quality_check.overall_score < standard.compliance_threshold:
            recommendations.append(
                f"Overall quality score {quality_check.overall_score} below threshold {standard.compliance_threshold}"
            )
        
        return recommendations
    
    def get_batch_quality_summary(self, batch_id: str) -> Dict:
        """Get comprehensive quality summary for a batch"""
        batch_checks = [qc for qc in self.quality_history if qc.batch_id == batch_id]
        
        if not batch_checks:
            return {
                "success": False,
                "error": f"No quality checks found for batch {batch_id}",
                "summary": None
            }
        
        # Determine batch quality status
        failed_checks = [qc for qc in batch_checks if qc.status == QualityStatus.FAILED]
        conditional_checks = [qc for qc in batch_checks if qc.status == QualityStatus.CONDITIONAL]
        
        if failed_checks:
            batch_status = "FAILED"
        elif conditional_checks:
            batch_status = "CONDITIONAL"
        else:
            batch_status = "PASSED"
        
        # Calculate average scores by check type
        scores_by_type = {}
        for check_type in CheckType:
            type_checks = [qc for qc in batch_checks if qc.check_type == check_type]
            if type_checks:
                avg_score = sum(qc.overall_score for qc in type_checks) / len(type_checks)
                scores_by_type[check_type.value] = round(avg_score, 1)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "batch_quality_status": batch_status,
            "total_checks": len(batch_checks),
            "passed_checks": len([qc for qc in batch_checks if qc.status == QualityStatus.PASSED]),
            "failed_checks": len(failed_checks),
            "conditional_checks": len(conditional_checks),
            "average_scores_by_type": scores_by_type,
            "quality_timeline": [
                {
                    "check_id": qc.check_id,
                    "check_type": qc.check_type.value,
                    "check_time": qc.check_time.isoformat(),
                    "score": qc.overall_score,
                    "status": qc.status.value
                }
                for qc in sorted(batch_checks, key=lambda x: x.check_time)
            ],
            "recommendations": self._generate_batch_recommendations(batch_checks)
        }
    
    def _generate_batch_recommendations(self, batch_checks: List[QualityCheck]) -> List[str]:
        """Generate batch-level quality recommendations"""
        recommendations = []
        
        # Check for consistent issues
        parameter_issues = {}
        for check in batch_checks:
            for param_name, param_value in check.parameters.items():
                if param_name not in parameter_issues:
                    parameter_issues[param_name] = []
                parameter_issues[param_name].append(param_value)
        
        for param_name, values in parameter_issues.items():
            if len(values) > 2:  # Multiple checks
                avg_value = sum(values) / len(values)
                variance = max(values) - min(values)
                
                if variance > avg_value * 0.2:  # High variance
                    recommendations.append(f"High variance in {param_name}: improve process consistency")
        
        # Check for declining quality
        sorted_checks = sorted(batch_checks, key=lambda x: x.check_time)
        if len(sorted_checks) >= 3:
            recent_scores = [qc.overall_score for qc in sorted_checks[-3:]]
            if recent_scores[0] > recent_scores[1] > recent_scores[2]:
                recommendations.append("Declining quality scores detected - review process parameters")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize quality tracker
    tracker = QualityTracker()
    
    # Sample quality checks
    sample_checks = [
        {
            "batch_id": "BATCH-2024-001",
            "product_type": "SMOKED_OMUL",
            "check_type": CheckType.RAW_MATERIAL,
            "parameters": {
                "appearance_score": 9.0,
                "texture_score": 8.5,
                "smell_score": 9.5,
                "bacterial_count": 800
            },
            "inspector_id": "QC-001",
            "comments": "Excellent raw material quality"
        },
        {
            "batch_id": "BATCH-2024-001",
            "product_type": "SMOKED_OMUL",
            "check_type": CheckType.FINAL_PRODUCT,
            "parameters": {
                "appearance_score": 8.0,
                "texture_score": 7.5,
                "smell_score": 9.0,
                "salt_content": 2.9
            },
            "inspector_id": "QC-002",
            "comments": "Good final product, slight texture variation"
        }
    ]
    
    # Record quality checks
    for check_data in sample_checks:
        result = tracker.record_quality_check(**check_data)
        print("Quality Check Result:")
        print(json.dumps(result, indent=2, default=str))
        print()
    
    # Get batch quality summary
    summary = tracker.get_batch_quality_summary("BATCH-2024-001")
    print("Batch Quality Summary:")
    print(json.dumps(summary, indent=2, default=str))
