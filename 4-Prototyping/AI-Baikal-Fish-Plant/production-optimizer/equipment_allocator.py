#!/usr/bin/env python3
"""
Equipment Allocator Prototype
Optimal equipment assignment and utilization tracking
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EquipmentStatus(Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    BROKEN = "BROKEN"

class EquipmentType(Enum):
    SMOKER = "SMOKER"
    FREEZER = "FREEZER"
    PACKAGING = "PACKAGING"
    CUTTING = "CUTTING"
    DRYING = "DRYING"

@dataclass
class Equipment:
    equipment_id: str
    equipment_type: EquipmentType
    capacity_kg: float
    status: EquipmentStatus
    current_utilization: float
    location: str
    last_maintenance: datetime
    next_maintenance: datetime

@dataclass
class ProductionTask:
    task_id: str
    product_type: str
    quantity_kg: float
    required_equipment: List[EquipmentType]
    estimated_duration: float  # hours
    priority: int
    deadline: datetime

class EquipmentAllocator:
    def __init__(self):
        self.equipment_db = self._initialize_equipment()
        self.maintenance_schedule = {}
        
    def _initialize_equipment(self) -> List[Equipment]:
        """Initialize equipment database"""
        current_time = datetime.now()
        return [
            Equipment(
                equipment_id="SMOKER-01",
                equipment_type=EquipmentType.SMOKER,
                capacity_kg=200.0,
                status=EquipmentStatus.AVAILABLE,
                current_utilization=0.0,
                location="PROCESSING_AREA_A",
                last_maintenance=current_time - timedelta(days=15),
                next_maintenance=current_time + timedelta(days=15)
            ),
            Equipment(
                equipment_id="SMOKER-02",
                equipment_type=EquipmentType.SMOKER,
                capacity_kg=200.0,
                status=EquipmentStatus.AVAILABLE,
                current_utilization=0.0,
                location="PROCESSING_AREA_A",
                last_maintenance=current_time - timedelta(days=10),
                next_maintenance=current_time + timedelta(days=20)
            ),
            Equipment(
                equipment_id="FREEZER-01",
                equipment_type=EquipmentType.FREEZER,
                capacity_kg=500.0,
                status=EquipmentStatus.AVAILABLE,
                current_utilization=0.0,
                location="COLD_STORAGE",
                last_maintenance=current_time - timedelta(days=30),
                next_maintenance=current_time + timedelta(days=60)
            ),
            Equipment(
                equipment_id="PACKAGING-01",
                equipment_type=EquipmentType.PACKAGING,
                capacity_kg=300.0,
                status=EquipmentStatus.IN_USE,
                current_utilization=75.0,
                location="PACKAGING_LINE",
                last_maintenance=current_time - timedelta(days=5),
                next_maintenance=current_time + timedelta(days=25)
            ),
            Equipment(
                equipment_id="PACKAGING-02",
                equipment_type=EquipmentType.PACKAGING,
                capacity_kg=300.0,
                status=EquipmentStatus.MAINTENANCE,
                current_utilization=0.0,
                location="MAINTENANCE_BAY",
                last_maintenance=current_time - timedelta(days=1),
                next_maintenance=current_time + timedelta(days=1)
            )
        ]
    
    def allocate_equipment(self, task: ProductionTask) -> Dict:
        """Allocate optimal equipment for production task"""
        # Find suitable equipment
        suitable_equipment = self._find_suitable_equipment(task)
        
        if not suitable_equipment:
            return {
                "success": False,
                "error": f"No suitable equipment available for {task.product_type}",
                "allocation": None
            }
        
        # Select optimal equipment based on utilization and efficiency
        optimal_equipment = self._select_optimal_equipment(suitable_equipment, task)
        
        if not optimal_equipment:
            return {
                "success": False,
                "error": "No equipment available within capacity constraints",
                "allocation": None
            }
        
        # Create allocation
        allocation = self._create_allocation(task, optimal_equipment)
        
        # Update equipment status
        self._update_equipment_status(optimal_equipment, task)
        
        return {
            "success": True,
            "allocation": allocation,
            "equipment_utilization": self._calculate_utilization_metrics(),
            "recommendations": self._generate_allocation_recommendations(task, optimal_equipment)
        }
    
    def _find_suitable_equipment(self, task: ProductionTask) -> List[Equipment]:
        """Find equipment suitable for the production task"""
        suitable = []
        
        for equipment in self.equipment_db:
            # Check if equipment type matches requirements
            if equipment.equipment_type not in task.required_equipment:
                continue
            
            # Check if equipment is available
            if equipment.status != EquipmentStatus.AVAILABLE:
                continue
            
            # Check capacity
            if equipment.capacity_kg < task.quantity_kg:
                continue
            
            # Check if equipment can complete task before maintenance
            if equipment.next_maintenance < datetime.now() + timedelta(hours=task.estimated_duration):
                continue
            
            suitable.append(equipment)
        
        return suitable
    
    def _select_optimal_equipment(self, suitable_equipment: List[Equipment], task: ProductionTask) -> Optional[Equipment]:
        """Select optimal equipment from suitable options"""
        if not suitable_equipment:
            return None
        
        # Score equipment based on multiple factors
        scored_equipment = []
        
        for equipment in suitable_equipment:
            score = self._calculate_equipment_score(equipment, task)
            scored_equipment.append((equipment, score))
        
        # Select equipment with highest score
        scored_equipment.sort(key=lambda x: x[1], reverse=True)
        return scored_equipment[0][0] if scored_equipment else None
    
    def _calculate_equipment_score(self, equipment: Equipment, task: ProductionTask) -> float:
        """Calculate equipment selection score"""
        score = 0.0
        
        # Utilization factor (prefer less utilized equipment)
        utilization_factor = (100 - equipment.current_utilization) / 100
        score += utilization_factor * 40  # 40% weight
        
        # Capacity efficiency (prefer equipment with capacity close to task quantity)
        capacity_ratio = task.quantity_kg / equipment.capacity_kg
        capacity_efficiency = 1 - abs(capacity_ratio - 0.8)  # Ideal at 80% capacity
        score += capacity_efficiency * 30  # 30% weight
        
        # Maintenance factor (prefer equipment with recent maintenance)
        days_since_maintenance = (datetime.now() - equipment.last_maintenance).days
        maintenance_factor = max(0, 1 - (days_since_maintenance / 30))  # 30-day scale
        score += maintenance_factor * 20  # 20% weight
        
        # Location factor (simplified - prefer same location for sequential tasks)
        location_factor = 1.0  # Could be enhanced with actual layout data
        score += location_factor * 10  # 10% weight
        
        return round(score, 2)
    
    def _create_allocation(self, task: ProductionTask, equipment: Equipment) -> Dict:
        """Create equipment allocation record"""
        allocation_id = f"ALLOC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        return {
            "allocation_id": allocation_id,
            "task_id": task.task_id,
            "product_type": task.product_type,
            "quantity_kg": task.quantity_kg,
            "allocated_equipment": {
                "equipment_id": equipment.equipment_id,
                "equipment_type": equipment.equipment_type.value,
                "capacity_kg": equipment.capacity_kg,
                "location": equipment.location
            },
            "scheduled_duration_hours": task.estimated_duration,
            "expected_completion": (datetime.now() + timedelta(hours=task.estimated_duration)).isoformat(),
            "utilization_percentage": round((task.quantity_kg / equipment.capacity_kg) * 100, 1),
            "allocation_time": datetime.now().isoformat(),
            "priority": task.priority
        }
    
    def _update_equipment_status(self, equipment: Equipment, task: ProductionTask):
        """Update equipment status after allocation"""
        # Find equipment in database
        for eq in self.equipment_db:
            if eq.equipment_id == equipment.equipment_id:
                eq.status = EquipmentStatus.IN_USE
                eq.current_utilization = (task.quantity_kg / eq.capacity_kg) * 100
                break
    
    def _calculate_utilization_metrics(self) -> Dict:
        """Calculate overall equipment utilization metrics"""
        total_equipment = len(self.equipment_db)
        available_equipment = len([e for e in self.equipment_db if e.status == EquipmentStatus.AVAILABLE])
        in_use_equipment = len([e for e in self.equipment_db if e.status == EquipmentStatus.IN_USE])
        
        avg_utilization = sum(e.current_utilization for e in self.equipment_db) / total_equipment
        
        utilization_by_type = {}
        for equipment in self.equipment_db:
            eq_type = equipment.equipment_type.value
            if eq_type not in utilization_by_type:
                utilization_by_type[eq_type] = []
            utilization_by_type[eq_type].append(equipment.current_utilization)
        
        # Calculate average by type
        avg_by_type = {}
        for eq_type, utilizations in utilization_by_type.items():
            avg_by_type[eq_type] = round(sum(utilizations) / len(utilizations), 1)
        
        return {
            "total_equipment": total_equipment,
            "available_equipment": available_equipment,
            "in_use_equipment": in_use_equipment,
            "under_maintenance": len([e for e in self.equipment_db if e.status == EquipmentStatus.MAINTENANCE]),
            "overall_utilization_rate": round(avg_utilization, 1),
            "utilization_by_type": avg_by_type,
            "bottleneck_equipment": self._identify_bottlenecks()
        }
    
    def _identify_bottlenecks(self) -> List[Dict]:
        """Identify equipment bottlenecks"""
        bottlenecks = []
        
        for equipment in self.equipment_db:
            if equipment.status == EquipmentStatus.IN_USE and equipment.current_utilization > 90:
                bottlenecks.append({
                    "equipment_id": equipment.equipment_id,
                    "equipment_type": equipment.equipment_type.value,
                    "utilization": equipment.current_utilization,
                    "status": "HIGH_UTILIZATION"
                })
            elif equipment.status == EquipmentStatus.MAINTENANCE:
                bottlenecks.append({
                    "equipment_id": equipment.equipment_id,
                    "equipment_type": equipment.equipment_type.value,
                    "utilization": equipment.current_utilization,
                    "status": "UNDER_MAINTENANCE"
                })
        
        return bottlenecks
    
    def _generate_allocation_recommendations(self, task: ProductionTask, equipment: Equipment) -> List[str]:
        """Generate recommendations for equipment allocation"""
        recommendations = []
        
        # Capacity recommendations
        utilization = (task.quantity_kg / equipment.capacity_kg) * 100
        if utilization > 90:
            recommendations.append(f"High utilization ({utilization}%) - consider splitting batch")
        elif utilization < 50:
            recommendations.append(f"Low utilization ({utilization}%) - consider combining with other tasks")
        
        # Maintenance recommendations
        days_until_maintenance = (equipment.next_maintenance - datetime.now()).days
        if days_until_maintenance < 7:
            recommendations.append(f"Maintenance scheduled in {days_until_maintenance} days - plan accordingly")
        
        # Efficiency recommendations
        if task.estimated_duration > 8:
            recommendations.append("Long processing time - monitor equipment performance closely")
        
        return recommendations
    
    def get_equipment_status_report(self) -> Dict:
        """Generate comprehensive equipment status report"""
        return {
            "report_id": f"EQUIP-REPORT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "equipment_summary": self._calculate_utilization_metrics(),
            "detailed_equipment_status": [
                {
                    "equipment_id": eq.equipment_id,
                    "equipment_type": eq.equipment_type.value,
                    "status": eq.status.value,
                    "utilization": eq.current_utilization,
                    "capacity_kg": eq.capacity_kg,
                    "location": eq.location,
                    "last_maintenance": eq.last_maintenance.isoformat(),
                    "next_maintenance": eq.next_maintenance.isoformat(),
                    "maintenance_due_days": (eq.next_maintenance - datetime.now()).days
                }
                for eq in self.equipment_db
            ],
            "recommendations": self._generate_maintenance_recommendations()
        }
    
    def _generate_maintenance_recommendations(self) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []
        
        for equipment in self.equipment_db:
            days_until_maintenance = (equipment.next_maintenance - datetime.now()).days
            
            if days_until_maintenance <= 3:
                recommendations.append(
                    f"URGENT: {equipment.equipment_id} maintenance due in {days_until_maintenance} days"
                )
            elif days_until_maintenance <= 7:
                recommendations.append(
                    f"Schedule maintenance for {equipment.equipment_id} in {days_until_maintenance} days"
                )
            
            # High utilization equipment
            if equipment.current_utilization > 80 and equipment.status == EquipmentStatus.IN_USE:
                recommendations.append(
                    f"High utilization on {equipment.equipment_id} ({equipment.current_utilization}%) - monitor for wear"
                )
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize equipment allocator
    allocator = EquipmentAllocator()
    
    # Sample production task
    sample_task = ProductionTask(
        task_id="TASK-2024-001",
        product_type="SMOKED_OMUL",
        quantity_kg=180.0,
        required_equipment=[EquipmentType.SMOKER, EquipmentType.PACKAGING],
        estimated_duration=8.0,
        priority=1,
        deadline=datetime.now() + timedelta(hours=24)
    )
    
    # Allocate equipment
    allocation_result = allocator.allocate_equipment(sample_task)
    
    print("Equipment Allocation Result:")
    print(json.dumps(allocation_result, indent=2, default=str))
    
    # Generate equipment status report
    print("\nEquipment Status Report:")
    status_report = allocator.get_equipment_status_report()
    print(json.dumps(status_report, indent=2, default=str))
