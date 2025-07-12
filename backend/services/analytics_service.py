import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.analytics_history = []
        self.performance_metrics = {}
        self.real_time_data = {}
    
    async def generate_analytics(self, warehouse_grid, current_orders, robots) -> Dict[str, Any]:
        """Generate comprehensive warehouse analytics"""
        try:
            analytics = {
                "operational_metrics": await self._calculate_operational_metrics(warehouse_grid, current_orders, robots),
                "inventory_analytics": await self._analyze_inventory(warehouse_grid),
                "order_analytics": await self._analyze_orders(current_orders),
                "robot_analytics": await self._analyze_robots(robots),
                "efficiency_metrics": await self._calculate_efficiency_metrics(warehouse_grid, current_orders, robots),
                "trends": await self._analyze_trends(),
                "predictions": await self._generate_predictions(warehouse_grid, current_orders, robots),
                "alerts": await self._generate_alerts(warehouse_grid, current_orders, robots),
                "generated_at": datetime.now().isoformat()
            }
            
            # Store analytics history
            self.analytics_history.append({
                "timestamp": datetime.now(),
                "data": analytics
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_operational_metrics(self, warehouse_grid, current_orders, robots) -> Dict[str, Any]:
        """Calculate key operational metrics"""
        try:
            total_orders = len(current_orders)
            completed_orders = len([o for o in current_orders if o.status == "completed"])
            pending_orders = len([o for o in current_orders if o.status == "pending"])
            processing_orders = len([o for o in current_orders if o.status == "processing"])
            
            active_robots = len([r for r in robots if r.status == "busy"])
            idle_robots = len([r for r in robots if r.status == "idle"])
            total_robots = len(robots)
            
            # Calculate completion rate
            completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            
            # Calculate robot utilization
            robot_utilization = (active_robots / total_robots * 100) if total_robots > 0 else 0
            
            # Calculate average order value
            total_order_value = sum(o.total_value for o in current_orders)
            average_order_value = total_order_value / total_orders if total_orders > 0 else 0
            
            # Calculate inventory value
            total_inventory_value = sum(item.quantity * item.price for item in warehouse_grid.inventory)
            
            return {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "pending_orders": pending_orders,
                "processing_orders": processing_orders,
                "completion_rate": round(completion_rate, 2),
                "active_robots": active_robots,
                "idle_robots": idle_robots,
                "total_robots": total_robots,
                "robot_utilization": round(robot_utilization, 2),
                "average_order_value": round(average_order_value, 2),
                "total_order_value": round(total_order_value, 2),
                "total_inventory_value": round(total_inventory_value, 2),
                "orders_per_hour": self._calculate_orders_per_hour(current_orders),
                "average_processing_time": self._calculate_average_processing_time(current_orders)
            }
        except Exception as e:
            logger.error(f"Error calculating operational metrics: {e}")
            return {}
    
    async def _analyze_inventory(self, warehouse_grid) -> Dict[str, Any]:
        """Analyze inventory performance and trends"""
        try:
            inventory_data = {
                "total_items": len(warehouse_grid.inventory),
                "categories": {},
                "stock_levels": {},
                "value_distribution": {},
                "restock_needs": []
            }
            
            # Analyze by category
            category_stats = defaultdict(lambda: {
                "count": 0,
                "total_quantity": 0,
                "total_value": 0.0,
                "avg_price": 0.0
            })
            
            for item in warehouse_grid.inventory:
                category_stats[item.category]["count"] += 1
                category_stats[item.category]["total_quantity"] += item.quantity
                category_stats[item.category]["total_value"] += item.quantity * item.price
            
            # Calculate averages
            for category, stats in category_stats.items():
                if stats["total_quantity"] > 0:
                    stats["avg_price"] = stats["total_value"] / stats["total_quantity"]
            
            inventory_data["categories"] = dict(category_stats)
            
            # Analyze stock levels
            low_stock = []
            high_stock = []
            normal_stock = []
            
            for item in warehouse_grid.inventory:
                stock_percentage = (item.quantity / item.max_stock_level) * 100
                
                if stock_percentage <= 20:
                    low_stock.append({
                        "id": item.id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "percentage": round(stock_percentage, 2)
                    })
                elif stock_percentage >= 80:
                    high_stock.append({
                        "id": item.id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "percentage": round(stock_percentage, 2)
                    })
                else:
                    normal_stock.append({
                        "id": item.id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "percentage": round(stock_percentage, 2)
                    })
            
            inventory_data["stock_levels"] = {
                "low_stock": low_stock,
                "high_stock": high_stock,
                "normal_stock": normal_stock,
                "low_stock_count": len(low_stock),
                "high_stock_count": len(high_stock),
                "normal_stock_count": len(normal_stock)
            }
            
            # Value distribution
            value_ranges = {
                "low_value": [],
                "medium_value": [],
                "high_value": []
            }
            
            for item in warehouse_grid.inventory:
                item_value = item.quantity * item.price
                if item_value < 1000:
                    value_ranges["low_value"].append(item.name)
                elif item_value < 10000:
                    value_ranges["medium_value"].append(item.name)
                else:
                    value_ranges["high_value"].append(item.name)
            
            inventory_data["value_distribution"] = value_ranges
            
            # Restock needs
            for item in warehouse_grid.inventory:
                if item.quantity <= item.min_stock_level:
                    inventory_data["restock_needs"].append({
                        "id": item.id,
                        "name": item.name,
                        "current_quantity": item.quantity,
                        "min_stock_level": item.min_stock_level,
                        "recommended_quantity": item.max_stock_level - item.quantity,
                        "urgency": "high" if item.quantity == 0 else "medium"
                    })
            
            return inventory_data
            
        except Exception as e:
            logger.error(f"Error analyzing inventory: {e}")
            return {}
    
    async def _analyze_orders(self, current_orders) -> Dict[str, Any]:
        """Analyze order patterns and performance"""
        try:
            order_analytics = {
                "order_patterns": {},
                "priority_distribution": {},
                "customer_analysis": {},
                "product_popularity": {},
                "time_analysis": {}
            }
            
            if not current_orders:
                return order_analytics
            
            # Priority distribution
            priority_counts = Counter(order.priority for order in current_orders)
            order_analytics["priority_distribution"] = dict(priority_counts)
            
            # Customer analysis
            customer_orders = defaultdict(list)
            for order in current_orders:
                customer_orders[order.customer_name].append(order)
            
            customer_stats = {}
            for customer, orders in customer_orders.items():
                customer_stats[customer] = {
                    "total_orders": len(orders),
                    "total_value": sum(o.total_value for o in orders),
                    "average_order_value": sum(o.total_value for o in orders) / len(orders),
                    "order_frequency": len(orders) / max(1, (datetime.now() - min(o.created_at for o in orders)).days)
                }
            
            order_analytics["customer_analysis"] = customer_stats
            
            # Product popularity
            product_counts = Counter()
            for order in current_orders:
                for item in order.items:
                    product_counts[item.get("product", "Unknown")] += item.get("quantity", 1)
            
            order_analytics["product_popularity"] = dict(product_counts.most_common(10))
            
            # Time analysis
            order_times = [order.created_at for order in current_orders]
            if order_times:
                order_analytics["time_analysis"] = {
                    "earliest_order": min(order_times).isoformat(),
                    "latest_order": max(order_times).isoformat(),
                    "average_orders_per_day": len(current_orders) / max(1, (max(order_times) - min(order_times)).days),
                    "peak_hours": self._analyze_peak_hours(order_times)
                }
            
            return order_analytics
            
        except Exception as e:
            logger.error(f"Error analyzing orders: {e}")
            return {}
    
    async def _analyze_robots(self, robots) -> Dict[str, Any]:
        """Analyze robot performance and efficiency"""
        try:
            robot_analytics = {
                "performance_metrics": {},
                "battery_analysis": {},
                "efficiency_ranking": [],
                "maintenance_needs": []
            }
            
            if not robots:
                return robot_analytics
            
            # Performance metrics
            total_distance = sum(r.total_distance_traveled for r in robots)
            total_orders = sum(r.orders_completed for r in robots)
            average_battery = np.mean([r.battery for r in robots])
            
            robot_analytics["performance_metrics"] = {
                "total_distance_traveled": total_distance,
                "total_orders_completed": total_orders,
                "average_battery": round(average_battery, 2),
                "average_efficiency": total_orders / max(total_distance, 1),
                "active_robots": len([r for r in robots if r.status == "busy"]),
                "idle_robots": len([r for r in robots if r.status == "idle"])
            }
            
            # Battery analysis
            battery_levels = [r.battery for r in robots]
            robot_analytics["battery_analysis"] = {
                "average_battery": round(np.mean(battery_levels), 2),
                "min_battery": round(min(battery_levels), 2),
                "max_battery": round(max(battery_levels), 2),
                "low_battery_robots": len([r for r in robots if r.battery < 30]),
                "critical_battery_robots": len([r for r in robots if r.battery < 10])
            }
            
            # Efficiency ranking
            robot_efficiency = []
            for robot in robots:
                efficiency = robot.orders_completed / max(robot.total_distance_traveled, 1)
                robot_efficiency.append({
                    "robot_id": robot.id,
                    "efficiency": round(efficiency, 4),
                    "orders_completed": robot.orders_completed,
                    "distance_traveled": robot.total_distance_traveled,
                    "battery": robot.battery
                })
            
            robot_efficiency.sort(key=lambda x: x["efficiency"], reverse=True)
            robot_analytics["efficiency_ranking"] = robot_efficiency
            
            # Maintenance needs
            for robot in robots:
                if robot.battery < 20:
                    robot_analytics["maintenance_needs"].append({
                        "robot_id": robot.id,
                        "issue": "Low battery",
                        "severity": "high" if robot.battery < 10 else "medium",
                        "battery_level": robot.battery
                    })
                
                days_since_maintenance = (datetime.now() - robot.last_maintenance).days
                if days_since_maintenance > 30:
                    robot_analytics["maintenance_needs"].append({
                        "robot_id": robot.id,
                        "issue": "Maintenance overdue",
                        "severity": "medium",
                        "days_overdue": days_since_maintenance - 30
                    })
            
            return robot_analytics
            
        except Exception as e:
            logger.error(f"Error analyzing robots: {e}")
            return {}
    
    async def _calculate_efficiency_metrics(self, warehouse_grid, current_orders, robots) -> Dict[str, Any]:
        """Calculate overall efficiency metrics"""
        try:
            efficiency_metrics = {
                "warehouse_efficiency": 0.0,
                "picking_efficiency": 0.0,
                "robot_efficiency": 0.0,
                "inventory_efficiency": 0.0,
                "order_fulfillment_efficiency": 0.0
            }
            
            # Warehouse efficiency (overall)
            total_orders = len(current_orders)
            completed_orders = len([o for o in current_orders if o.status == "completed"])
            efficiency_metrics["warehouse_efficiency"] = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            
            # Robot efficiency
            active_robots = len([r for r in robots if r.status == "busy"])
            total_robots = len(robots)
            efficiency_metrics["robot_efficiency"] = (active_robots / total_robots * 100) if total_robots > 0 else 0
            
            # Inventory efficiency
            if warehouse_grid.inventory:
                low_stock_items = len([item for item in warehouse_grid.inventory if item.quantity <= item.min_stock_level])
                total_items = len(warehouse_grid.inventory)
                efficiency_metrics["inventory_efficiency"] = ((total_items - low_stock_items) / total_items * 100) if total_items > 0 else 0
            
            # Order fulfillment efficiency
            processing_orders = len([o for o in current_orders if o.status == "processing"])
            pending_orders = len([o for o in current_orders if o.status == "pending"])
            total_active_orders = processing_orders + pending_orders
            efficiency_metrics["order_fulfillment_efficiency"] = (processing_orders / total_active_orders * 100) if total_active_orders > 0 else 0
            
            # Picking efficiency (simplified)
            efficiency_metrics["picking_efficiency"] = min(95, efficiency_metrics["warehouse_efficiency"] + 10)
            
            return efficiency_metrics
            
        except Exception as e:
            logger.error(f"Error calculating efficiency metrics: {e}")
            return {}
    
    async def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze historical trends"""
        try:
            # This would typically analyze historical data
            # For now, return simulated trend data
            trends = {
                "order_volume_trend": "increasing",
                "efficiency_trend": "stable",
                "inventory_turnover_trend": "improving",
                "robot_utilization_trend": "stable",
                "peak_hours": ["09:00-11:00", "14:00-16:00"],
                "seasonal_patterns": {
                    "q1": "high",
                    "q2": "medium",
                    "q3": "low",
                    "q4": "very_high"
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}
    
    async def _generate_predictions(self, warehouse_grid, current_orders, robots) -> Dict[str, Any]:
        """Generate predictions for future operations"""
        try:
            predictions = {
                "demand_forecast": {},
                "capacity_planning": {},
                "resource_requirements": {}
            }
            
            # Demand forecast (simplified)
            current_demand = len(current_orders)
            predictions["demand_forecast"] = {
                "next_hour": int(current_demand * 1.1),
                "next_day": int(current_demand * 24 * 1.05),
                "next_week": int(current_demand * 24 * 7 * 1.02),
                "trend": "increasing" if current_demand > 10 else "stable"
            }
            
            # Capacity planning
            predictions["capacity_planning"] = {
                "current_capacity": len([r for r in robots if r.status == "idle"]),
                "required_capacity": max(2, int(current_demand / 5)),
                "capacity_gap": max(0, int(current_demand / 5) - len([r for r in robots if r.status == "idle"])),
                "recommendation": "add_robots" if current_demand > 20 else "maintain"
            }
            
            # Resource requirements
            predictions["resource_requirements"] = {
                "additional_robots_needed": max(0, int(current_demand / 10) - len(robots)),
                "inventory_restock_needed": len([item for item in warehouse_grid.inventory if item.quantity <= item.min_stock_level]),
                "peak_hours_approaching": True if datetime.now().hour in [9, 10, 14, 15] else False
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {}
    
    async def _generate_alerts(self, warehouse_grid, current_orders, robots) -> List[Dict[str, Any]]:
        """Generate alerts for critical issues"""
        try:
            alerts = []
            
            # Low stock alerts
            low_stock_items = [item for item in warehouse_grid.inventory if item.quantity <= item.min_stock_level]
            if low_stock_items:
                alerts.append({
                    "type": "low_stock",
                    "severity": "high" if len(low_stock_items) > 5 else "medium",
                    "message": f"{len(low_stock_items)} items need restocking",
                    "items": [item.name for item in low_stock_items[:3]]
                })
            
            # Robot battery alerts
            low_battery_robots = [r for r in robots if r.battery < 20]
            if low_battery_robots:
                alerts.append({
                    "type": "low_battery",
                    "severity": "high" if any(r.battery < 10 for r in low_battery_robots) else "medium",
                    "message": f"{len(low_battery_robots)} robots have low battery",
                    "robots": [r.id for r in low_battery_robots]
                })
            
            # High order volume alerts
            if len(current_orders) > 25:
                alerts.append({
                    "type": "high_volume",
                    "severity": "medium",
                    "message": "High order volume detected",
                    "orders": len(current_orders)
                })
            
            # Efficiency alerts
            completion_rate = len([o for o in current_orders if o.status == "completed"]) / len(current_orders) if current_orders else 0
            if completion_rate < 0.7:
                alerts.append({
                    "type": "low_efficiency",
                    "severity": "high",
                    "message": "Low order completion rate detected",
                    "completion_rate": round(completion_rate * 100, 2)
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return []
    
    def _calculate_orders_per_hour(self, current_orders) -> float:
        """Calculate orders per hour"""
        try:
            if not current_orders:
                return 0.0
            
            order_times = [order.created_at for order in current_orders]
            time_span = max(order_times) - min(order_times)
            hours = time_span.total_seconds() / 3600
            
            return len(current_orders) / max(hours, 1)
        except Exception:
            return 0.0
    
    def _calculate_average_processing_time(self, current_orders) -> float:
        """Calculate average order processing time"""
        try:
            completed_orders = [o for o in current_orders if o.status == "completed" and o.actual_completion]
            
            if not completed_orders:
                return 0.0
            
            total_time = sum((o.actual_completion - o.created_at).total_seconds() for o in completed_orders)
            return total_time / len(completed_orders) / 60  # Return in minutes
        except Exception:
            return 0.0
    
    def _analyze_peak_hours(self, order_times) -> List[str]:
        """Analyze peak order hours"""
        try:
            hour_counts = Counter(order_time.hour for order_time in order_times)
            peak_hours = hour_counts.most_common(3)
            return [f"{hour:02d}:00-{(hour+1):02d}:00" for hour, _ in peak_hours]
        except Exception:
            return ["09:00-10:00", "14:00-15:00"] 