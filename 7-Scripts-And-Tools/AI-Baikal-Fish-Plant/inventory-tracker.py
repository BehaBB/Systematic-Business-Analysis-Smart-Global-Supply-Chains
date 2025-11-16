"""
Inventory Tracking System
AI Baikal Fish Plant
"""

class InventoryTracker:
    def __init__(self):
        self.inventory = {}
        self.reorder_points = {
            'fresh_omul': 500,  # kg
            'frozen_sig': 300,  # kg
            'packaging': 1000   # units
        }
    
    def update_inventory(self, item, quantity):
        self.inventory[item] = self.inventory.get(item, 0) + quantity
    
    def check_reorder(self, item):
        current_stock = self.inventory.get(item, 0)
        reorder_point = self.reorder_points.get(item, 0)
        return current_stock <= reorder_point
    
    def get_inventory_report(self):
        low_stock = []
        for item, stock in self.inventory.items():
            if self.check_reorder(item):
                low_stock.append(item)
        
        return {
            'total_items': len(self.inventory),
            'low_stock_items': low_stock,
            'inventory_value': sum(self.inventory.values())
        }
