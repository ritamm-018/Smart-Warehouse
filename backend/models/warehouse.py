import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class OrderPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RobotStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"

@dataclass
class InventoryItem:
    id: int
    name: str
    category: str
    quantity: int
    location_x: int
    location_y: int
    price: float
    weight: float
    supplier: str
    last_restocked: datetime
    expiry_date: Optional[datetime] = None
    min_stock_level: int = 10
    max_stock_level: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "location_x": self.location_x,
            "location_y": self.location_y,
            "price": self.price,
            "weight": self.weight,
            "supplier": self.supplier,
            "last_restocked": self.last_restocked.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "min_stock_level": self.min_stock_level,
            "max_stock_level": self.max_stock_level,
            "stock_status": self.get_stock_status()
        }
    
    def get_stock_status(self) -> str:
        if self.quantity <= self.min_stock_level:
            return "low"
        elif self.quantity >= self.max_stock_level * 0.8:
            return "high"
        else:
            return "normal"

@dataclass
class Order:
    id: int
    customer_name: str
    items: List[Dict[str, Any]]
    priority: str
    status: str
    created_at: datetime = field(default_factory=datetime.now)
    assigned_robot: Optional[int] = None
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    total_value: float = 0.0
    
    def __post_init__(self):
        if not self.total_value:
            self.total_value = sum(item.get("price", 0) * item.get("quantity", 1) for item in self.items)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "items": self.items,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "assigned_robot": self.assigned_robot,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "actual_completion": self.actual_completion.isoformat() if self.actual_completion else None,
            "total_value": self.total_value
        }

@dataclass
class Robot:
    id: int
    x: int
    y: int
    status: str
    battery: float
    speed: float = 1.0
    capacity: float = 50.0
    current_order: Optional[int] = None
    route: List[Dict[str, Any]] = field(default_factory=list)
    current_position: int = 0
    total_distance_traveled: float = 0.0
    orders_completed: int = 0
    last_maintenance: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "status": self.status,
            "battery": self.battery,
            "speed": self.speed,
            "capacity": self.capacity,
            "current_order": self.current_order,
            "route": self.route,
            "current_position": self.current_position,
            "total_distance_traveled": self.total_distance_traveled,
            "orders_completed": self.orders_completed,
            "last_maintenance": self.last_maintenance.isoformat(),
            "battery_status": self.get_battery_status()
        }
    
    def get_battery_status(self) -> str:
        if self.battery > 80:
            return "excellent"
        elif self.battery > 50:
            return "good"
        elif self.battery > 20:
            return "low"
        else:
            return "critical"

@dataclass
class Analytics:
    total_orders: int = 0
    completed_orders: int = 0
    pending_orders: int = 0
    processing_orders: int = 0
    active_robots: int = 0
    idle_robots: int = 0
    average_battery: float = 0.0
    total_inventory_value: float = 0.0
    orders_per_hour: float = 0.0
    average_order_value: float = 0.0
    efficiency_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_orders": self.total_orders,
            "completed_orders": self.completed_orders,
            "pending_orders": self.pending_orders,
            "processing_orders": self.processing_orders,
            "active_robots": self.active_robots,
            "idle_robots": self.idle_robots,
            "average_battery": self.average_battery,
            "total_inventory_value": self.total_inventory_value,
            "orders_per_hour": self.orders_per_hour,
            "average_order_value": self.average_order_value,
            "efficiency_score": self.efficiency_score,
            "last_updated": self.last_updated.isoformat(),
            "completion_rate": self.get_completion_rate(),
            "robot_utilization": self.get_robot_utilization()
        }
    
    def get_completion_rate(self) -> float:
        if self.total_orders == 0:
            return 0.0
        return (self.completed_orders / self.total_orders) * 100
    
    def get_robot_utilization(self) -> float:
        total_robots = self.active_robots + self.idle_robots
        if total_robots == 0:
            return 0.0
        return (self.active_robots / total_robots) * 100

class WarehouseGrid:
    def __init__(self, rows: int = 50, cols: int = 50):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)
        self.inventory: List[InventoryItem] = []
        self.shelves: List[Dict[str, Any]] = []
        self.entrances: List[Dict[str, int]] = []
        self.exits: List[Dict[str, int]] = []
        
    def create_shelf_layout(self):
        """Create a realistic warehouse shelf layout"""
        # Clear grid
        self.grid.fill(0)
        
        # Create main aisles (horizontal)
        for row in range(5, self.rows, 8):
            self.grid[row:row+2, :] = 0  # Aisle
            self.grid[row+2:row+6, :] = 1  # Shelf
        
        # Create vertical aisles
        for col in range(5, self.cols, 10):
            self.grid[:, col:col+2] = 0  # Aisle
            self.grid[:, col+2:col+6] = 1  # Shelf
        
        # Add entrance and exit
        self.entrances = [{"x": 0, "y": 5}, {"x": 0, "y": 15}, {"x": 0, "y": 25}]
        self.exits = [{"x": self.cols-1, "y": 5}, {"x": self.cols-1, "y": 15}, {"x": self.cols-1, "y": 25}]
        
        # Mark entrances and exits
        for entrance in self.entrances:
            self.grid[entrance["y"], entrance["x"]] = 2  # Entrance
        for exit_pos in self.exits:
            self.grid[exit_pos["y"], exit_pos["x"]] = 3  # Exit
        
        # Create shelf locations
        self._create_shelf_locations()
    
    def _create_shelf_locations(self):
        """Create shelf location mappings"""
        self.shelves = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row, col] == 1:
                    self.shelves.append({
                        "x": col,
                        "y": row,
                        "capacity": random.randint(50, 200),
                        "utilization": random.uniform(0.3, 0.9)
                    })
    
    async def initialize_inventory(self):
        """Initialize warehouse with realistic inventory"""
        products = [
            {"name": "Laptop", "category": "Electronics", "price": 899.99, "weight": 2.5},
            {"name": "Smartphone", "category": "Electronics", "price": 699.99, "weight": 0.2},
            {"name": "Tablet", "category": "Electronics", "price": 399.99, "weight": 0.5},
            {"name": "Headphones", "category": "Electronics", "price": 199.99, "weight": 0.3},
            {"name": "Camera", "category": "Electronics", "price": 599.99, "weight": 1.2},
            {"name": "Speaker", "category": "Electronics", "price": 149.99, "weight": 0.8},
            {"name": "T-Shirt", "category": "Clothing", "price": 24.99, "weight": 0.2},
            {"name": "Jeans", "category": "Clothing", "price": 59.99, "weight": 0.5},
            {"name": "Shoes", "category": "Clothing", "price": 89.99, "weight": 0.8},
            {"name": "Jacket", "category": "Clothing", "price": 129.99, "weight": 0.6},
            {"name": "Book", "category": "Books", "price": 19.99, "weight": 0.4},
            {"name": "Notebook", "category": "Office", "price": 9.99, "weight": 0.1},
            {"name": "Pen", "category": "Office", "price": 2.99, "weight": 0.01},
            {"name": "Coffee Mug", "category": "Kitchen", "price": 14.99, "weight": 0.3},
            {"name": "Water Bottle", "category": "Kitchen", "price": 19.99, "weight": 0.2}
        ]
        
        suppliers = ["Amazon", "Walmart", "Target", "Best Buy", "Home Depot", "Costco"]
        
        for i, product in enumerate(products):
            # Find available shelf location
            if i < len(self.shelves):
                shelf = self.shelves[i]
                item = InventoryItem(
                    id=i+1,
                    name=product["name"],
                    category=product["category"],
                    quantity=random.randint(20, 100),
                    location_x=shelf["x"],
                    location_y=shelf["y"],
                    price=product["price"],
                    weight=product["weight"],
                    supplier=random.choice(suppliers),
                    last_restocked=datetime.now() - timedelta(days=random.randint(1, 30)),
                    min_stock_level=10,
                    max_stock_level=random.randint(100, 200)
                )
                self.inventory.append(item)
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by category"""
        stats = {}
        for item in self.inventory:
            if item.category not in stats:
                stats[item.category] = {
                    "count": 0,
                    "total_quantity": 0,
                    "total_value": 0.0,
                    "avg_price": 0.0
                }
            
            stats[item.category]["count"] += 1
            stats[item.category]["total_quantity"] += item.quantity
            stats[item.category]["total_value"] += item.quantity * item.price
        
        # Calculate averages
        for category in stats:
            if stats[category]["count"] > 0:
                stats[category]["avg_price"] = stats[category]["total_value"] / stats[category]["total_quantity"]
        
        return stats
    
    def find_path(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Dict[str, int]]:
        """Simple A* pathfinding algorithm"""
        # For now, return a simple direct path
        # In a real implementation, this would use A* algorithm
        path = []
        current_x, current_y = start_x, start_y
        
        while current_x != end_x or current_y != end_y:
            if current_x < end_x:
                current_x += 1
            elif current_x > end_x:
                current_x -= 1
            
            if current_y < end_y:
                current_y += 1
            elif current_y > end_y:
                current_y -= 1
            
            path.append({"x": current_x, "y": current_y})
        
        return path
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is valid and walkable"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y, x] == 0  # 0 = walkable
        return False
    
    def get_nearest_shelf(self, x: int, y: int) -> Optional[Dict[str, int]]:
        """Find nearest shelf to given position"""
        if not self.shelves:
            return None
        
        nearest = min(self.shelves, key=lambda s: abs(s["x"] - x) + abs(s["y"] - y))
        return {"x": nearest["x"], "y": nearest["y"]} 