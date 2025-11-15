#!/usr/bin/env python3
"""
Production Schedule Generator Prototype
AI-powered optimization for fish processing plant
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductionOrder:
    product_type: str
    quantity: float
    priority: int
    processing_time: float  # hours
    equipment_requirements: List[str]

@dataclass
class Equipment:
    equipment_id: str
    equipment_type: str
    capacity: float
    status: str  # AVAILABLE, MAINTENANCE, BROKEN
    utilization: float

@dataclass
class RawMaterial:
    material_id: str
    fish_type: str
    quantity: float
    quality_grade: str
    shelf_life_days: int

class ProductionScheduleGenerator:
    def __init__(self):
        self.equipment_list = self._load_equipment()
        self.processing_times = self._load_processing_times()
        
    def _load_equipment(self) -> List[Equipment]:
        """Load available equipment"""
        return [
            Equipment("SMOKER-01", "SMOKER", 200.0, "AVAILABLE", 0.0),
            Equipment("SMOKER-02", "SMOKER", 200.0, "AVAILABLE", 0.0),
            Equipment("FREEZER-01", "FREEZER", 500.0, "AVAILABLE", 0.0),
            Equipment("PACKAGING-01", "PACKAGING", 300.0, "AVAILABLE", 0.0),
            Equipment("PACKAGING-02", "PACKAGING", 300.0, "MAINTENANCE", 0.0)
        ]
    
    def _load_processing_times(self) -> Dict[str, float]:
        """Load standard processing times by product type"""
        return {
            "SMOKED_OMUL": 8.0,
            "FROZEN_OMUL": 2.0,
            "SMOKED_SIG": 7.0,
            "FROZEN_SIG": 2.0,
            "DRIED_GRAYLING": 24.0
        }
    
    def generate_schedule(self, production_orders: List[ProductionOrder], 
                         raw_materials: List[RawMaterial], 
                         planning_horizon: int = 7) -> Dict:
        """Generate optimized production schedule"""
        
        # Validate raw material availability
        material_validation = self._validate_raw_materials(production_orders, raw_materials)
        if not material_validation["sufficient"]:
            return {
                "success": False,
                "error": f"Insufficient raw materials: {material_validation['missing']}",
                "schedule": None
            }
        
        # Validate equipment availability
        equipment_validation = self._validate_equipment_capacity(production_orders)
        if not equipment_validation["sufficient"]:
            return {
                "success": False,
                "error": f"Insufficient equipment capacity: {equipment_validation['bottlenecks']}",
                "schedule": None
            }
        
        # Generate optimized schedule
        optimized_schedule = self._optimize_schedule(production_orders, planning_horizon)
        
        return {
            "success": True,
            "schedule": optimized_schedule,
            "summary": self._generate_schedule_summary(optimized_schedule),
            "equipment_utilization": self._calculate_equipment_utilization(optimized_schedule),
            "generated_at": datetime.now().isoformat()
        }
    
    def _validate_raw_materials(self, orders: List[ProductionOrder], 
                              materials: List[RawMaterial]) -> Dict:
        """Validate raw material availability against production orders"""
        required_materials = {}
        
        # Calculate required materials by fish type
        for order in orders:
            fish_type = order.product_type.split('_')[1]  # Extract fish type from product
            if fish_type not in required_materials:
                required_materials[fish_type] = 0
            required_materials[fish_type] += order.quantity
        
        # Check availability
        available_materials = {}
        for material in materials:
            if material.fish_type not in available_materials:
                available_materials[material.fish_type] = 0
            available_materials[material.fish_type] += material.quantity
        
        missing_materials = {}
        for fish_type, required in required_materials.items():
            available = available_materials.get(fish_type, 0)
            if required > available:
                missing_materials[fish_type] = required - available
        
        return {
            "sufficient": len(missing_materials) == 0,
            "missing": missing_materials,
            "required": required_materials,
            "available": available_materials
        }
    
    def _validate_equipment_capacity(self, orders: List[ProductionOrder]) -> Dict:
        """Validate equipment capacity against production requirements"""
        equipment_requirements = {}
        
        # Calculate equipment requirements
        for order in orders:
            for equipment_type in order.equipment_requirements:
                if equipment_type not in equipment_requirements:
                    equipment_requirements[equipment_type] = 0
                equipment_requirements[equipment_type] += order.processing_time
        
        # Check available capacity
        available_equipment = {}
        for equipment in self.equipment_list:
            if equipment.status == "AVAILABLE":
                if equipment.equipment_type not in available_equipment:
                    available_equipment[equipment.equipment_type] = 0
                # Assume 16 hours operational day
                available_equipment[equipment.equipment_type] += 16.0
        
        bottlenecks = {}
        for eq_type, required_time in equipment_requirements.items():
            available_time = available_equipment.get(eq_type, 0)
            if required_time > available_time:
                bottlenecks[eq_type] = {
                    "required_hours": required_time,
                    "available_hours": available_time,
                    "deficit_hours": required_time - available_time
                }
        
        return {
            "sufficient": len(bottlenecks) == 0,
            "bottlenecks": bottlenecks,
            "requirements": equipment_requirements,
            "available": available_equipment
        }
    
    def _optimize_schedule(self, orders: List[ProductionOrder], horizon: int) -> List[Dict]:
        """Generate optimized production schedule using priority-based algorithm"""
        # Sort orders by priority (1 = highest) and processing time
        sorted_orders = sorted(orders, key=lambda x: (x.priority, x.processing_time))
        
        schedule = []
        current_date = datetime.now()
        equipment_schedule = {eq.equipment_id: [] for eq in self.equipment_list if eq.status == "AVAILABLE"}
        
        for order in sorted_orders:
            # Find available equipment and time slot
            scheduled = self._schedule_order(order, equipment_schedule, current_date, horizon)
            if scheduled:
                schedule.append(scheduled)
        
        return schedule
    
    def _schedule_order(self, order: ProductionOrder, equipment_schedule: Dict, 
                       start_date: datetime, horizon: int) -> Optional[Dict]:
        """Schedule a single production order"""
        for day in range(horizon):
            current_date = start_date + timedelta(days=day)
            
            # Find available equipment for this order
            suitable_equipment = []
            for eq_id, bookings in equipment_schedule.items():
                equipment = next((e for e in self.equipment_list if e.equipment_id == eq_id), None)
                if equipment and equipment.equipment_type in order.equipment_requirements:
                    # Check if equipment has capacity on this day
                    daily_bookings = [b for b in bookings if b["date"].date() == current_date.date()]
                    booked_hours = sum(b["duration"] for b in daily_bookings)
                    if booked_hours + order.processing_time <= 16:  # 16-hour operational day
                        suitable_equipment.append(equipment)
            
            if suitable_equipment:
                # Use first available suitable equipment
                equipment = suitable_equipment[0]
                start_time = current_date.replace(hour=8, minute=0)  # Start at 8 AM
                
                # Calculate end time based on processing time
                end_time = start_time + timedelta(hours=order.processing_time)
                
                # Add to equipment schedule
                booking = {
                    "order_id": f"ORDER-{len(equipment_schedule[equipment.equipment_id]) + 1}",
                    "product_type": order.product_type,
                    "quantity": order.quantity,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": order.processing_time,
                    "date": current_date
                }
                equipment_schedule[equipment.equipment_id].append(booking)
                
                return {
                    "order_reference": f"PROD-{datetime.now().strftime('%Y%m%d')}-{len(equipment_schedule[equipment.equipment_id])}",
                    "product_type": order.product_type,
                    "quantity": order.quantity,
                    "scheduled_date": current_date.strftime('%Y-%m-%d'),
                    "start_time": start_time.strftime('%H:%M'),
                    "end_time": end_time.strftime('%H:%M'),
                    "assigned_equipment": equipment.equipment_id,
                    "processing_time_hours": order.processing_time,
                    "priority": order.priority
                }
        
        return None
    
    def _generate_schedule_summary(self, schedule: List[Dict]) -> Dict:
        """Generate summary of production schedule"""
        total_quantity = sum(order["quantity"] for order in schedule)
        total_processing_time = sum(order["processing_time_hours"] for order in schedule)
        
        by_product = {}
        for order in schedule:
            product = order["product_type"]
            if product not in by_product:
                by_product[product] = {"quantity": 0, "orders": 0}
            by_product[product]["quantity"] += order["quantity"]
            by_product[product]["orders"] += 1
        
        return {
            "total_orders": len(schedule),
            "total_quantity_kg": total_quantity,
            "total_processing_hours": total_processing_time,
            "products_summary": by_product,
            "schedule_days": len(set(order["scheduled_date"] for order in schedule))
        }
    
    def _calculate_equipment_utilization(self, schedule: List[Dict]) -> Dict:
        """Calculate equipment utilization from schedule"""
        equipment_usage = {}
        
        for order in schedule:
            equipment = order["assigned_equipment"]
            if equipment not in equipment_usage:
                equipment_usage[equipment] = 0
            equipment_usage[equipment] += order["processing_time_hours"]
        
        utilization = {}
        for equipment in self.equipment_list:
            if equipment.status == "AVAILABLE":
                total_capacity = 16.0  # 16 hours per day
                used_capacity = equipment_usage.get(equipment.equipment_id, 0)
                utilization_rate = (used_capacity / total_capacity) * 100
                
                utilization[equipment.equipment_id] = {
                    "used_hours": used_capacity,
                    "available_hours": total_capacity,
                    "utilization_rate": round(utilization_rate, 1),
                    "status": equipment.status
                }
        
        return utilization

# Example usage
if __name__ == "__main__":
    # Initialize schedule generator
    generator = ProductionScheduleGenerator()
    
    # Sample production orders
    production_orders = [
        ProductionOrder(
            product_type="SMOKED_OMUL",
            quantity=200.0,
            priority=1,
            processing_time=8.0,
            equipment_requirements=["SMOKER", "PACKAGING"]
        ),
        ProductionOrder(
            product_type="FROZEN_SIG", 
            quantity=300.0,
            priority=2,
            processing_time=2.0,
            equipment_requirements=["FREEZER", "PACKAGING"]
        ),
        ProductionOrder(
            product_type="DRIED_GRAYLING",
            quantity=150.0,
            priority=3, 
            processing_time=24.0,
            equipment_requirements=["SMOKER"]  # Using smoker for drying
        )
    ]
    
    # Sample raw materials
    raw_materials = [
        RawMaterial("RAW-OMUL-001", "OMUL", 250.0, "EXCELLENT", 3),
        RawMaterial("RAW-SIG-001", "SIG", 350.0, "GOOD", 2),
        RawMaterial("RAW-GRAYLING-001", "GRAYLING", 200.0, "EXCELLENT", 4)
    ]
    
    # Generate schedule
    result = generator.generate_schedule(production_orders, raw_materials)
    
    print("Production Schedule Generation Result:")
    print(json.dumps(result, indent=2, default=str))
