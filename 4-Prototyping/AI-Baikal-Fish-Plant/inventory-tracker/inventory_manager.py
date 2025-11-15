#!/usr/bin/env python3
"""
Inventory Manager Prototype
Real-time tracking of raw materials and finished goods with yield calculation
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InventoryType(Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    FINISHED_GOOD = "FINISHED_GOOD"
    PACKAGING = "PACKAGING"

class MovementType(Enum):
    RECEIPT = "RECEIPT"
    CONSUMPTION = "CONSUMPTION"
    PRODUCTION = "PRODUCTION"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"

@dataclass
class InventoryItem:
    item_id: str
    item_type: InventoryType
    description: str
    quantity: float
    unit: str
    location: str
    batch_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    quality_grade: Optional[str] = None

@dataclass
class InventoryMovement:
    movement_id: str
    item_id: str
    movement_type: MovementType
    quantity: float
    reference_id: str  # batch_id, order_id, etc.
    location: str
    movement_time: datetime
    notes: str

class InventoryManager:
    def __init__(self):
        self.inventory_db = self._initialize_inventory()
        self.movement_history = []
        
    def _initialize_inventory(self) -> Dict[str, InventoryItem]:
        """Initialize inventory database"""
        current_time = datetime.now()
        return {
            "RAW-OMUL-001": InventoryItem(
                item_id="RAW-OMUL-001",
                item_type=InventoryType.RAW_MATERIAL,
                description="Fresh Omul Fish",
                quantity=300.0,
                unit="kg",
                location="COLD_ROOM_A",
                expiry_date=current_time + timedelta(days=3),
                quality_grade="EXCELLENT"
            ),
            "RAW-SIG-001": InventoryItem(
                item_id="RAW-SIG-001", 
                item_type=InventoryType.RAW_MATERIAL,
                description="Fresh Sig Fish",
                quantity=400.0,
                unit="kg", 
                location="COLD_ROOM_B",
                expiry_date=current_time + timedelta(days=2),
                quality_grade="GOOD"
            ),
            "FIN-SMOKED-OMUL-001": InventoryItem(
                item_id="FIN-SMOKED-OMUL-001",
                item_type=InventoryType.FINISHED_GOOD, 
                description="Smoked Omul",
                quantity=150.0,
                unit="kg",
                location="FINISHED_GOODS",
                batch_id="BATCH-2024-001"
            )
        }
    
    def record_movement(self, movement_data: Dict) -> Dict:
        """Record inventory movement and update quantities"""
        try:
            # Validate movement
            validation = self._validate_movement(movement_data)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Movement validation failed: {validation['errors']}",
                    "movement_id": None
                }
            
            # Create movement record
            movement_id = f"MOV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            movement = InventoryMovement(
                movement_id=movement_id,
                item_id=movement_data["item_id"],
                movement_type=MovementType(movement_data["movement_type"]),
                quantity=movement_data["quantity"],
                reference_id=movement_data["reference_id"],
                location=movement_data["location"],
                movement_time=datetime.now(),
                notes=movement_data.get("notes", "")
            )
            
            # Update inventory quantity
            update_success = self._update_inventory_quantity(movement)
            if not update_success:
                return {
                    "success": False,
                    "error": "Inventory update failed - insufficient quantity",
                    "movement_id": None
                }
            
            # Record movement
            self.movement_history.append(movement)
            
            return {
                "success": True,
                "movement_id": movement_id,
                "movement_details": self._format_movement(movement),
                "inventory_snapshot": self._get_item_status(movement.item_id)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Movement recording failed: {str(e)}",
                "movement_id": None
            }
    
    def _validate_movement(self, movement_data: Dict) -> Dict:
        """Validate inventory movement"""
        errors = []
        
        # Check if item exists
        if movement_data["item_id"] not in self.inventory_db:
            errors.append(f"Item {movement_data['item_id']} not found")
        
        # Validate quantity
        if movement_data["quantity"] <= 0:
            errors.append("Quantity must be positive")
        
        # Check for sufficient quantity for consumption
        if movement_data["movement_type"] == "CONSUMPTION":
            current_qty = self.inventory_db[movement_data["item_id"]].quantity
            if movement_data["quantity"] > current_qty:
                errors.append(f"Insufficient quantity. Available: {current_qty}, Requested: {movement_data['quantity']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _update_inventory_quantity(self, movement: InventoryMovement) -> bool:
        """Update inventory quantity based on movement"""
        item = self.inventory_db[movement.item_id]
        
        if movement.movement_type == MovementType.RECEIPT:
            item.quantity += movement.quantity
        elif movement.movement_type == MovementType.CONSUMPTION:
            if movement.quantity > item.quantity:
                return False
            item.quantity -= movement.quantity
        elif movement.movement_type == MovementType.PRODUCTION:
            item.quantity += movement.quantity
        
        # Update location if changed
        if movement.location != item.location:
            item.location = movement.location
        
        return True
    
    def calculate_yield(self, batch_id: str, raw_material_id: str, finished_product_id: str) -> Dict:
        """Calculate production yield for a batch"""
        # Find consumption movements for raw material
        raw_material_consumed = 0
        for movement in self.movement_history:
            if (movement.reference_id == batch_id and 
                movement.item_id == raw_material_id and
                movement.movement_type == MovementType.CONSUMPTION):
                raw_material_consumed += movement.quantity
        
        # Find production movements for finished product
        finished_product_produced = 0
        for movement in self.movement_history:
            if (movement.reference_id == batch_id and
                movement.item_id == finished_product_id and
                movement.movement_type == MovementType.PRODUCTION):
                finished_product_produced += movement.quantity
        
        if raw_material_consumed == 0:
            return {
                "success": False,
                "error": "No raw material consumption found for batch",
                "yield_data": None
            }
        
        yield_percentage = (finished_product_produced / raw_material_consumed) * 100
        loss_percentage = 100 - yield_percentage
        
        return {
            "success": True,
            "yield_data": {
                "batch_id": batch_id,
                "raw_material_consumed_kg": raw_material_consumed,
                "finished_product_produced_kg": finished_product_produced,
                "yield_percentage": round(yield_percentage, 1),
                "loss_percentage": round(loss_percentage, 1),
                "loss_kg": raw_material_consumed - finished_product_produced
            },
            "comparison": self._compare_to_expected_yield(batch_id, yield_percentage)
        }
    
    def _compare_to_expected_yield(self, batch_id: str, actual_yield: float) -> Dict:
        """Compare actual yield to expected yield"""
        # Expected yields by product type (would come from standards database)
        expected_yields = {
            "SMOKED_OMUL": 80.0,
            "FROZEN_SIG": 91.0,
            "DRIED_GRAYLING": 83.0
        }
        
        # Extract product type from batch_id or use a mapping
        product_type = "SMOKED_OMUL"  # Simplified - would come from batch data
        
        expected_yield = expected_yields.get(product_type, 85.0)
        variance = actual_yield - expected_yield
        variance_percentage = (variance / expected_yield) * 100
        
        return {
            "expected_yield": expected_yield,
            "actual_yield": actual_yield,
            "variance": round(variance, 1),
            "variance_percentage": round(variance_percentage, 1),
            "performance": "ABOVE_EXPECTED" if variance > 0 else "BELOW_EXPECTED"
        }
    
    def get_inventory_report(self) -> Dict:
        """Generate comprehensive inventory report"""
        total_items = len(self.inventory_db)
        total_value_kg = sum(item.quantity for item in self.inventory_db.values())
        
        # Categorize by type
        by_type = {}
        for item in self.inventory_db.values():
            if item.item_type.value not in by_type:
                by_type[item.item_type.value] = []
            by_type[item.item_type.value].append({
                "item_id": item.item_id,
                "description": item.description,
                "quantity": item.quantity,
                "location": item.location
            })
        
        # Identify low stock items
        low_stock = []
        for item in self.inventory_db.values():
            if item.quantity < 50:  # Threshold for low stock
                low_stock.append({
                    "item_id": item.item_id,
                    "description": item.description,
                    "current_quantity": item.quantity,
                    "location": item.location
                })
        
        # Recent movements
        recent_movements = sorted(self.movement_history, key=lambda x: x.movement_time, reverse=True)[:10]
        
        return {
            "report_id": f"INV-REPORT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_items": total_items,
                "total_quantity_kg": round(total_value_kg, 1),
                "low_stock_items": len(low_stock),
                "recent_movements": len(recent_movements)
            },
            "inventory_by_type": by_type,
            "low_stock_alerts": low_stock,
            "recent_movements": [self._format_movement(mov) for mov in recent_movements]
        }
    
    def _format_movement(self, movement: InventoryMovement) -> Dict:
        """Format movement for response"""
        return {
            "movement_id": movement.movement_id,
            "item_id": movement.item_id,
            "movement_type": movement.movement_type.value,
            "quantity": movement.quantity,
            "reference_id": movement.reference_id,
            "location": movement.location,
            "movement_time": movement.movement_time.isoformat(),
            "notes": movement.notes
        }
    
    def _get_item_status(self, item_id: str) -> Dict:
        """Get current status of an inventory item"""
        if item_id not in self.inventory_db:
            return {"error": "Item not found"}
        
        item = self.inventory_db[item_id]
        return {
            "item_id": item.item_id,
            "description": item.description,
            "current_quantity": item.quantity,
            "unit": item.unit,
            "location": item.location,
            "batch_id": item.batch_id,
            "quality_grade": item.quality_grade
        }

# Example usage
if __name__ == "__main__":
    # Initialize inventory manager
    inventory_mgr = InventoryManager()
    
    # Sample movements
    sample_movements = [
        {
            "item_id": "RAW-OMUL-001",
            "movement_type": "CONSUMPTION",
            "quantity": 250.0,
            "reference_id": "BATCH-2024-001",
            "location": "PROCESSING_LINE",
            "notes": "Raw material for smoked omul production"
        },
        {
            "item_id": "FIN-SMOKED-OMUL-001", 
            "movement_type": "PRODUCTION",
            "quantity": 200.0,
            "reference_id": "BATCH-2024-001",
            "location": "FINISHED_GOODS",
            "notes": "Finished smoked omul from batch 2024-001"
        }
    ]
    
    # Record movements
    for movement_data in sample_movements:
        result = inventory_mgr.record_movement(movement_data)
        print("Inventory Movement Result:")
        print(json.dumps(result, indent=2, default=str))
        print()
    
    # Calculate yield
    yield_result = inventory_mgr.calculate_yield(
        "BATCH-2024-001", 
        "RAW-OMUL-001", 
        "FIN-SMOKED-OMUL-001"
    )
    print("Yield Calculation Result:")
    print(json.dumps(yield_result, indent=2, default=str))
    print()
    
    # Generate inventory report
    report = inventory_mgr.get_inventory_report()
    print("Inventory Report:")
    print(json.dumps(report, indent=2, default=str))
