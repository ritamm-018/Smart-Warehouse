import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.demand_model = None
        self.optimization_model = None
        self.scaler = StandardScaler()
        self.model_path = "models/"
        self._ensure_model_directory()
        self._load_or_train_models()
    
    def _ensure_model_directory(self):
        """Ensure model directory exists"""
        os.makedirs(self.model_path, exist_ok=True)
    
    def _load_or_train_models(self):
        """Load existing models or train new ones"""
        try:
            self.demand_model = joblib.load(f"{self.model_path}demand_forecast_model.pkl")
            self.optimization_model = joblib.load(f"{self.model_path}optimization_model.pkl")
            logger.info("Loaded existing AI models")
        except FileNotFoundError:
            logger.info("Training new AI models...")
            self._train_demand_model()
            self._train_optimization_model()
    
    def _train_demand_model(self):
        """Train demand forecasting model"""
        # Generate synthetic historical data
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera']
        
        data = []
        for date in dates:
            for product in products:
                # Add seasonal patterns and trends
                base_demand = 50
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.dayofyear / 365)
                trend_factor = 1 + 0.001 * (date - pd.Timestamp('2023-01-01')).days
                random_factor = random.uniform(0.8, 1.2)
                
                demand = int(base_demand * seasonal_factor * trend_factor * random_factor)
                
                data.append({
                    'date': date,
                    'product': product,
                    'demand': demand,
                    'day_of_week': date.dayofweek,
                    'month': date.month,
                    'quarter': date.quarter,
                    'is_weekend': 1 if date.dayofweek >= 5 else 0
                })
        
        df = pd.DataFrame(data)
        
        # Prepare features
        X = df[['day_of_week', 'month', 'quarter', 'is_weekend']].values
        y = df['demand'].values
        
        # Train model
        self.demand_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.demand_model.fit(X, y)
        
        # Save model
        joblib.dump(self.demand_model, f"{self.model_path}demand_forecast_model.pkl")
        logger.info("Demand forecasting model trained and saved")
    
    def _train_optimization_model(self):
        """Train warehouse optimization model"""
        # Generate synthetic optimization data
        data = []
        for _ in range(1000):
            # Simulate different warehouse configurations
            shelf_density = random.uniform(0.3, 0.8)
            aisle_width = random.uniform(1, 3)
            robot_count = random.randint(2, 8)
            order_volume = random.randint(50, 500)
            
            # Calculate efficiency score (simplified)
            efficiency = (
                shelf_density * 0.3 +
                (1 / aisle_width) * 0.2 +
                min(robot_count / 5, 1) * 0.3 +
                min(order_volume / 300, 1) * 0.2
            ) + random.uniform(-0.1, 0.1)
            
            data.append({
                'shelf_density': shelf_density,
                'aisle_width': aisle_width,
                'robot_count': robot_count,
                'order_volume': order_volume,
                'efficiency': efficiency
            })
        
        df = pd.DataFrame(data)
        
        # Train model
        X = df[['shelf_density', 'aisle_width', 'robot_count', 'order_volume']].values
        y = df['efficiency'].values
        
        self.optimization_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.optimization_model.fit(X, y)
        
        # Save model
        joblib.dump(self.optimization_model, f"{self.model_path}optimization_model.pkl")
        logger.info("Optimization model trained and saved")
    
    async def generate_predictions(self, warehouse_grid, current_orders, analytics_data) -> Dict[str, Any]:
        """Generate AI-powered predictions for warehouse operations"""
        try:
            predictions = {
                "demand_forecast": await self._predict_demand(),
                "inventory_optimization": await self._predict_inventory_needs(warehouse_grid),
                "robot_optimization": await self._predict_robot_needs(analytics_data),
                "efficiency_improvements": await self._predict_efficiency_gains(warehouse_grid),
                "risk_assessment": await self._assess_risks(warehouse_grid, current_orders),
                "cost_savings": await self._predict_cost_savings(analytics_data),
                "generated_at": datetime.now().isoformat()
            }
            
            return predictions
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {"error": str(e)}
    
    async def _predict_demand(self) -> Dict[str, Any]:
        """Predict demand for next 30 days"""
        try:
            future_dates = pd.date_range(
                start=datetime.now(),
                periods=30,
                freq='D'
            )
            
            predictions = {}
            products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera']
            
            for product in products:
                product_predictions = []
                for date in future_dates:
                    features = np.array([[
                        date.dayofweek,
                        date.month,
                        date.quarter,
                        1 if date.dayofweek >= 5 else 0
                    ]])
                    
                    prediction = self.demand_model.predict(features)[0]
                    product_predictions.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "predicted_demand": int(max(0, prediction))
                    })
                
                predictions[product] = product_predictions
            
            return {
                "period": "30_days",
                "predictions": predictions,
                "total_predicted_demand": sum(
                    sum(p["predicted_demand"] for p in product_preds)
                    for product_preds in predictions.values()
                )
            }
        except Exception as e:
            logger.error(f"Error predicting demand: {e}")
            return {"error": str(e)}
    
    async def _predict_inventory_needs(self, warehouse_grid) -> Dict[str, Any]:
        """Predict inventory needs and restocking requirements"""
        try:
            inventory_needs = []
            
            for item in warehouse_grid.inventory:
                # Calculate days until stockout
                daily_usage = random.uniform(2, 8)  # Simulated daily usage
                days_until_stockout = item.quantity / daily_usage if daily_usage > 0 else float('inf')
                
                # Predict restock need
                restock_need = "immediate" if days_until_stockout < 7 else \
                              "soon" if days_until_stockout < 14 else \
                              "normal" if days_until_stockout < 30 else "none"
                
                inventory_needs.append({
                    "item_id": item.id,
                    "item_name": item.name,
                    "current_stock": item.quantity,
                    "days_until_stockout": round(days_until_stockout, 1),
                    "restock_need": restock_need,
                    "recommended_quantity": min(item.max_stock_level, int(daily_usage * 30))
                })
            
            return {
                "inventory_needs": inventory_needs,
                "urgent_restocks": len([n for n in inventory_needs if n["restock_need"] == "immediate"]),
                "total_restock_value": sum(
                    n["recommended_quantity"] * next(
                        (item.price for item in warehouse_grid.inventory if item.id == n["item_id"]), 0
                    )
                    for n in inventory_needs if n["restock_need"] != "none"
                )
            }
        except Exception as e:
            logger.error(f"Error predicting inventory needs: {e}")
            return {"error": str(e)}
    
    async def _predict_robot_needs(self, analytics_data) -> Dict[str, Any]:
        """Predict optimal robot fleet size and utilization"""
        try:
            current_utilization = analytics_data.get_robot_utilization()
            order_volume = analytics_data.total_orders
            
            # Predict optimal robot count based on order volume
            optimal_robots = max(2, int(order_volume / 50))  # 1 robot per 50 orders
            current_robots = analytics_data.active_robots + analytics_data.idle_robots
            
            return {
                "current_robots": current_robots,
                "optimal_robots": optimal_robots,
                "robot_deficit": max(0, optimal_robots - current_robots),
                "current_utilization": current_utilization,
                "optimal_utilization": 85.0,  # Target utilization
                "efficiency_gap": 85.0 - current_utilization,
                "recommendations": self._generate_robot_recommendations(current_utilization, optimal_robots, current_robots)
            }
        except Exception as e:
            logger.error(f"Error predicting robot needs: {e}")
            return {"error": str(e)}
    
    def _generate_robot_recommendations(self, utilization, optimal_robots, current_robots) -> List[str]:
        """Generate recommendations for robot fleet optimization"""
        recommendations = []
        
        if utilization > 90:
            recommendations.append("High utilization detected. Consider adding more robots to prevent bottlenecks.")
        
        if optimal_robots > current_robots:
            recommendations.append(f"Order volume suggests {optimal_robots} robots optimal. Consider adding {optimal_robots - current_robots} robots.")
        
        if utilization < 50:
            recommendations.append("Low utilization detected. Consider reducing robot fleet or increasing order volume.")
        
        if not recommendations:
            recommendations.append("Robot fleet is well-optimized for current operations.")
        
        return recommendations
    
    async def _predict_efficiency_gains(self, warehouse_grid) -> Dict[str, Any]:
        """Predict potential efficiency improvements"""
        try:
            # Analyze current layout
            shelf_count = len(warehouse_grid.shelves)
            total_cells = warehouse_grid.rows * warehouse_grid.cols
            shelf_density = shelf_count / total_cells
            
            # Predict efficiency improvements
            current_efficiency = 75.0  # Simulated current efficiency
            potential_efficiency = min(95.0, current_efficiency + (1 - shelf_density) * 20)
            
            return {
                "current_efficiency": current_efficiency,
                "potential_efficiency": potential_efficiency,
                "efficiency_gain": potential_efficiency - current_efficiency,
                "layout_score": shelf_density * 100,
                "optimization_opportunities": [
                    "Reorganize high-demand items closer to shipping area",
                    "Optimize aisle widths for robot navigation",
                    "Implement dynamic slotting based on demand patterns",
                    "Add cross-aisle connections for faster routing"
                ]
            }
        except Exception as e:
            logger.error(f"Error predicting efficiency gains: {e}")
            return {"error": str(e)}
    
    async def _assess_risks(self, warehouse_grid, current_orders) -> Dict[str, Any]:
        """Assess operational risks"""
        try:
            risks = []
            
            # Check for low stock items
            low_stock_items = [item for item in warehouse_grid.inventory if item.quantity <= item.min_stock_level]
            if low_stock_items:
                risks.append({
                    "type": "stockout_risk",
                    "severity": "high" if len(low_stock_items) > 5 else "medium",
                    "description": f"{len(low_stock_items)} items at risk of stockout",
                    "items": [item.name for item in low_stock_items[:5]]
                })
            
            # Check for high order volume
            if len(current_orders) > 20:
                risks.append({
                    "type": "capacity_risk",
                    "severity": "medium",
                    "description": "High order volume may exceed processing capacity",
                    "recommendation": "Consider adding temporary workers or extending shifts"
                })
            
            # Check for aging inventory
            aging_items = [
                item for item in warehouse_grid.inventory
                if (datetime.now() - item.last_restocked).days > 60
            ]
            if aging_items:
                risks.append({
                    "type": "aging_inventory",
                    "severity": "low",
                    "description": f"{len(aging_items)} items haven't been restocked in 60+ days",
                    "recommendation": "Review demand patterns and adjust stock levels"
                })
            
            return {
                "total_risks": len(risks),
                "high_risk_count": len([r for r in risks if r["severity"] == "high"]),
                "medium_risk_count": len([r for r in risks if r["severity"] == "medium"]),
                "low_risk_count": len([r for r in risks if r["severity"] == "low"]),
                "risks": risks
            }
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {"error": str(e)}
    
    async def _predict_cost_savings(self, analytics_data) -> Dict[str, Any]:
        """Predict potential cost savings from optimizations"""
        try:
            # Simulate cost savings calculations
            current_operating_cost = 10000  # Simulated monthly cost
            potential_savings = {
                "inventory_optimization": current_operating_cost * 0.05,  # 5% savings
                "robot_efficiency": current_operating_cost * 0.03,  # 3% savings
                "layout_optimization": current_operating_cost * 0.02,  # 2% savings
                "predictive_maintenance": current_operating_cost * 0.01,  # 1% savings
            }
            
            total_potential_savings = sum(potential_savings.values())
            
            return {
                "current_monthly_cost": current_operating_cost,
                "potential_monthly_savings": total_potential_savings,
                "savings_breakdown": potential_savings,
                "roi_percentage": (total_potential_savings / current_operating_cost) * 100,
                "payback_period_months": 6  # Simulated payback period
            }
        except Exception as e:
            logger.error(f"Error predicting cost savings: {e}")
            return {"error": str(e)}
    
    async def optimize_order_sequence(self, orders: List[Dict]) -> List[Dict]:
        """Optimize order processing sequence using AI"""
        try:
            if not orders:
                return orders
            
            # Score orders based on priority, value, and complexity
            scored_orders = []
            for order in orders:
                score = 0
                
                # Priority scoring
                priority_scores = {"urgent": 100, "high": 80, "normal": 60, "low": 40}
                score += priority_scores.get(order.get("priority", "normal"), 60)
                
                # Value scoring
                score += min(order.get("total_value", 0) / 100, 50)
                
                # Complexity scoring (inverse - simpler orders get higher score)
                item_count = len(order.get("items", []))
                score += max(0, 50 - item_count * 5)
                
                scored_orders.append((score, order))
            
            # Sort by score (highest first)
            scored_orders.sort(key=lambda x: x[0], reverse=True)
            
            return [order for score, order in scored_orders]
        except Exception as e:
            logger.error(f"Error optimizing order sequence: {e}")
            return orders 