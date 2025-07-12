import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "warehouse.db"):
        self.db_path = db_path
        self.connection = None
    
    async def initialize_database(self):
        """Initialize database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _create_tables(self):
        """Create all necessary database tables"""
        if not self.connection:
            raise Exception("Database connection not initialized")
        cursor = self.connection.cursor()
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                items TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_robot INTEGER,
                estimated_completion TIMESTAMP,
                actual_completion TIMESTAMP,
                total_value REAL DEFAULT 0.0
            )
        ''')
        
        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                location_x INTEGER NOT NULL,
                location_y INTEGER NOT NULL,
                price REAL NOT NULL,
                weight REAL NOT NULL,
                supplier TEXT NOT NULL,
                last_restocked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                min_stock_level INTEGER DEFAULT 10,
                max_stock_level INTEGER DEFAULT 100
            )
        ''')
        
        # Robots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                status TEXT NOT NULL,
                battery REAL NOT NULL,
                speed REAL DEFAULT 1.0,
                capacity REAL DEFAULT 50.0,
                current_order INTEGER,
                route TEXT,
                current_position INTEGER DEFAULT 0,
                total_distance_traveled REAL DEFAULT 0.0,
                orders_completed INTEGER DEFAULT 0,
                last_maintenance TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_orders INTEGER DEFAULT 0,
                completed_orders INTEGER DEFAULT 0,
                pending_orders INTEGER DEFAULT 0,
                processing_orders INTEGER DEFAULT 0,
                active_robots INTEGER DEFAULT 0,
                idle_robots INTEGER DEFAULT 0,
                average_battery REAL DEFAULT 0.0,
                total_inventory_value REAL DEFAULT 0.0,
                orders_per_hour REAL DEFAULT 0.0,
                average_order_value REAL DEFAULT 0.0,
                efficiency_score REAL DEFAULT 0.0
            )
        ''')
        
        # Optimization history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                optimization_type TEXT NOT NULL,
                result TEXT NOT NULL,
                performance_improvement REAL DEFAULT 0.0
            )
        ''')
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    async def save_order(self, order_data: Dict[str, Any]) -> int:
        """Save order to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO orders (customer_name, items, priority, status, total_value)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                order_data["customer_name"],
                json.dumps(order_data["items"]),
                order_data["priority"],
                order_data["status"],
                order_data.get("total_value", 0.0)
            ))
            
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving order: {e}")
            raise
    
    async def update_order(self, order_id: int, updates: Dict[str, Any]):
        """Update order in database"""
        try:
            cursor = self.connection.cursor()
            
            # Build update query dynamically
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == "items":
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            values.append(order_id)
            
            query = f"UPDATE orders SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating order: {e}")
            raise
    
    async def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders from database"""
        try:
            cursor = self.connection.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT * FROM orders ORDER BY created_at DESC
                ''')
            
            rows = cursor.fetchall()
            orders = []
            
            for row in rows:
                order = dict(row)
                order["items"] = json.loads(order["items"])
                orders.append(order)
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    async def save_inventory_item(self, item_data: Dict[str, Any]) -> int:
        """Save inventory item to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO inventory (name, category, quantity, location_x, location_y, 
                                     price, weight, supplier, min_stock_level, max_stock_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_data["name"],
                item_data["category"],
                item_data["quantity"],
                item_data["location_x"],
                item_data["location_y"],
                item_data["price"],
                item_data["weight"],
                item_data["supplier"],
                item_data.get("min_stock_level", 10),
                item_data.get("max_stock_level", 100)
            ))
            
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving inventory item: {e}")
            raise
    
    async def update_inventory_item(self, item_id: int, updates: Dict[str, Any]):
        """Update inventory item in database"""
        try:
            cursor = self.connection.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(item_id)
            
            query = f"UPDATE inventory SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating inventory item: {e}")
            raise
    
    async def get_inventory(self) -> List[Dict[str, Any]]:
        """Get all inventory items from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM inventory ORDER BY category, name')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting inventory: {e}")
            return []
    
    async def save_robot(self, robot_data: Dict[str, Any]) -> int:
        """Save robot to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO robots (x, y, status, battery, speed, capacity, route)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                robot_data["x"],
                robot_data["y"],
                robot_data["status"],
                robot_data["battery"],
                robot_data.get("speed", 1.0),
                robot_data.get("capacity", 50.0),
                json.dumps(robot_data.get("route", []))
            ))
            
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving robot: {e}")
            raise
    
    async def update_robot(self, robot_id: int, updates: Dict[str, Any]):
        """Update robot in database"""
        try:
            cursor = self.connection.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == "route":
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            values.append(robot_id)
            
            query = f"UPDATE robots SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating robot: {e}")
            raise
    
    async def get_robots(self) -> List[Dict[str, Any]]:
        """Get all robots from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM robots ORDER BY id')
            
            rows = cursor.fetchall()
            robots = []
            
            for row in rows:
                robot = dict(row)
                robot["route"] = json.loads(robot["route"]) if robot["route"] else []
                robots.append(robot)
            
            return robots
            
        except Exception as e:
            logger.error(f"Error getting robots: {e}")
            return []
    
    async def save_analytics(self, analytics_data: Dict[str, Any]):
        """Save analytics data to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO analytics (total_orders, completed_orders, pending_orders, 
                                     processing_orders, active_robots, idle_robots,
                                     average_battery, total_inventory_value, orders_per_hour,
                                     average_order_value, efficiency_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analytics_data.get("total_orders", 0),
                analytics_data.get("completed_orders", 0),
                analytics_data.get("pending_orders", 0),
                analytics_data.get("processing_orders", 0),
                analytics_data.get("active_robots", 0),
                analytics_data.get("idle_robots", 0),
                analytics_data.get("average_battery", 0.0),
                analytics_data.get("total_inventory_value", 0.0),
                analytics_data.get("orders_per_hour", 0.0),
                analytics_data.get("average_order_value", 0.0),
                analytics_data.get("efficiency_score", 0.0)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
            raise
    
    async def get_analytics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get analytics history from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM analytics 
                WHERE timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            '''.format(hours))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting analytics history: {e}")
            return []
    
    async def save_optimization_result(self, optimization_type: str, result: Dict[str, Any], performance_improvement: float):
        """Save optimization result to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO optimization_history (optimization_type, result, performance_improvement)
                VALUES (?, ?, ?)
            ''', (
                optimization_type,
                json.dumps(result),
                performance_improvement
            ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving optimization result: {e}")
            raise
    
    async def get_optimization_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get optimization history from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM optimization_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            history = []
            
            for row in rows:
                item = dict(row)
                item["result"] = json.loads(item["result"])
                history.append(item)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting optimization history: {e}")
            return []
    
    async def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            raise
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data from database"""
        try:
            cursor = self.connection.cursor()
            
            # Clean up old analytics data
            cursor.execute('''
                DELETE FROM analytics 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            # Clean up old optimization history
            cursor.execute('''
                DELETE FROM optimization_history 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            self.connection.commit()
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed") 