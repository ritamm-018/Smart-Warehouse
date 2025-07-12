#!/usr/bin/env python3
"""
Order Data Service - Manages historical order frequency data
Provides realistic order generation based on historical patterns
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

class OrderDataService:
    def __init__(self):
        self.order_data = None
        self.load_order_data()
    
    def load_order_data(self):
        """Load historical order frequency data from JSON file"""
        try:
            data_path = Path(__file__).parent.parent.parent / "data" / "orders.json"
            with open(data_path, 'r') as f:
                self.order_data = json.load(f)
            print(f"✅ Loaded order frequency data for {len(self.order_data['order_frequency'])} categories")
        except Exception as e:
            print(f"❌ Error loading order data: {e}")
            self.order_data = self.get_default_order_data()
    
    def get_default_order_data(self):
        """Fallback order data if JSON file is not available"""
        return {
            "order_frequency": {
                "mobile-phones": {"frequency": 35, "popular_products": ["iPhone", "Samsung", "OnePlus"]},
                "laptops-tablets": {"frequency": 25, "popular_products": ["MacBook", "Dell", "iPad"]},
                "packaged-food": {"frequency": 50, "popular_products": ["Chips", "Biscuits", "Snacks"]},
                "headphones-accessories": {"frequency": 20, "popular_products": ["AirPods", "Sony", "Cases"]},
                "mens-clothing": {"frequency": 15, "popular_products": ["T-shirts", "Jeans", "Shirts"]},
                "toys-games": {"frequency": 12, "popular_products": ["Toys", "Games", "Puzzles"]},
                "pet-supplies": {"frequency": 8, "popular_products": ["Pet Food", "Toys", "Beds"]},
                "kitchen-appliances": {"frequency": 5, "popular_products": ["Microwave", "Blender", "Toaster"]}
            }
        }
    
    def get_category_frequencies(self) -> Dict[str, int]:
        """Get order frequency percentages for each category"""
        frequencies = {}
        if not self.order_data or "order_frequency" not in self.order_data:
            return frequencies
            
        total_frequency = sum(cat["frequency"] for cat in self.order_data["order_frequency"].values())
        
        for category, data in self.order_data["order_frequency"].items():
            frequencies[category] = (data["frequency"] / total_frequency) * 100
        
        return frequencies
    
    def generate_realistic_orders(self, num_orders: int, available_categories: List[str]) -> List[Dict]:
        """Generate orders based on historical frequency data"""
        orders = []
        
        if not self.order_data or "order_frequency" not in self.order_data:
            return self.generate_default_orders(num_orders, available_categories)
        
        # Filter available categories
        available_data = {
            cat: data for cat, data in self.order_data["order_frequency"].items() 
            if cat in available_categories
        }
        
        if not available_data:
            print("⚠️ No matching categories found, using default order generation")
            return self.generate_default_orders(num_orders, available_categories)
        
        # Calculate frequencies for available categories
        total_frequency = sum(data["frequency"] for data in available_data.values())
        category_weights = [available_data[cat]["frequency"] / total_frequency for cat in available_categories]
        
        # Generate orders based on frequency weights
        for i in range(num_orders):
            # Choose category based on frequency weights
            category = random.choices(available_categories, weights=category_weights)[0]
            
            # Get popular products for this category
            popular_products = available_data[category].get("popular_products", [f"Product {i + 1}"])
            product = random.choice(popular_products)
            
            orders.append({
                "id": i + 1,
                "product": product,
                "category": category,
                "frequency_weight": available_data[category]["frequency"],
                "generated_at": datetime.now().isoformat()
            })
        
        return orders
    
    def generate_default_orders(self, num_orders: int, available_categories: List[str]) -> List[Dict]:
        """Generate orders with equal probability when no frequency data is available"""
        orders = []
        
        for i in range(num_orders):
            category = random.choice(available_categories)
            product = f"Product {i + 1}"
            
            orders.append({
                "id": i + 1,
                "product": product,
                "category": category,
                "frequency_weight": 1,
                "generated_at": datetime.now().isoformat()
            })
        
        return orders
    
    def get_category_analytics(self, category: str) -> Dict:
        """Get analytics for a specific category"""
        if not self.order_data or "order_frequency" not in self.order_data:
            return {}
        if category in self.order_data["order_frequency"]:
            return self.order_data["order_frequency"][category]
        return {}
    
    def get_warehouse_analytics(self) -> Dict:
        """Get overall warehouse analytics"""
        if not self.order_data:
            return {}
        return self.order_data.get("warehouse_analytics", {})
    
    def get_seasonal_multiplier(self, current_date: datetime | None = None) -> float:
        """Get seasonal multiplier for current date"""
        if current_date is None:
            current_date = datetime.now()
        
        if not self.order_data or "warehouse_analytics" not in self.order_data:
            return 1.0
        
        month = current_date.month
        seasonal_multipliers = self.order_data["warehouse_analytics"].get("seasonal_multipliers", {})
        
        # Determine season
        if month in [12, 1, 2]:  # Winter/Holiday
            return seasonal_multipliers.get("holiday_season", 1.0)
        elif month in [8, 9]:  # Back to School
            return seasonal_multipliers.get("back_to_school", 1.0)
        elif month in [6, 7]:  # Summer Sales
            return seasonal_multipliers.get("summer_sales", 1.0)
        else:
            return seasonal_multipliers.get("regular_season", 1.0)
    
    def get_correlated_categories(self, category: str) -> List[str]:
        """Get categories that are frequently ordered together"""
        if not self.order_data or "warehouse_analytics" not in self.order_data:
            return []
        correlations = self.order_data["warehouse_analytics"].get("category_correlations", {})
        return correlations.get(category, [])
    
    def get_peak_hours(self, category: str) -> List[str]:
        """Get peak ordering hours for a category"""
        if not self.order_data or "order_frequency" not in self.order_data:
            return []
        if category in self.order_data["order_frequency"]:
            return self.order_data["order_frequency"][category].get("peak_hours", [])
        return []
    
    def calculate_demand_score(self, category: str, current_hour: int | None = None) -> float:
        """Calculate demand score for a category based on time and season"""
        if not self.order_data or "order_frequency" not in self.order_data:
            return 1.0
        if category not in self.order_data["order_frequency"]:
            return 1.0
        
        base_frequency = self.order_data["order_frequency"][category]["frequency"]
        seasonal_multiplier = self.get_seasonal_multiplier()
        
        # Time-based multiplier
        time_multiplier = 1.0
        if current_hour is not None:
            peak_hours = self.get_peak_hours(category)
            if peak_hours:
                # Check if current hour is near peak hours
                for peak_hour in peak_hours:
                    peak_hour_int = int(peak_hour.split(":")[0])
                    if abs(current_hour - peak_hour_int) <= 2:
                        time_multiplier = 1.3
                        break
        
        return base_frequency * seasonal_multiplier * time_multiplier

# Global instance
order_data_service = OrderDataService() 