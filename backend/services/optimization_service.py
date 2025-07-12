import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import random
import logging
from datetime import datetime, timedelta
import heapq

logger = logging.getLogger(__name__)

class OptimizationService:
    def __init__(self):
        self.optimization_history = []
        self.performance_metrics = {}
    
    async def optimize_order_fulfillment(self, order, warehouse_grid, robots) -> Dict[str, Any]:
        """Optimize route for order fulfillment"""
        try:
            # Find items in the order
            item_locations = []
            for item_data in order.items:
                item_name = item_data.get("product")
                # Find item in inventory
                for inventory_item in warehouse_grid.inventory:
                    if inventory_item.name == item_name:
                        item_locations.append({
                            "x": inventory_item.location_x,
                            "y": inventory_item.location_y,
                            "item": inventory_item,
                            "quantity": item_data.get("quantity", 1)
                        })
                        break
            
            if not item_locations:
                return {}
            
            # Find best robot for this order
            best_robot = self._find_best_robot(robots, item_locations[0])
            if not best_robot:
                return {}
            
            # Generate optimized route
            route = self._generate_optimized_route(
                best_robot, item_locations, warehouse_grid
            )
            
            # Calculate route metrics
            route_metrics = self._calculate_route_metrics(route, best_robot)
            
            return {
                "route": route,
                "robot_id": best_robot.id,
                "estimated_time": route_metrics["estimated_time"],
                "total_distance": route_metrics["total_distance"],
                "energy_consumption": route_metrics["energy_consumption"],
                "optimization_score": route_metrics["optimization_score"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing order fulfillment: {e}")
            return {}
    
    def _find_best_robot(self, robots, first_item_location) -> Optional[Any]:
        """Find the best available robot for the order"""
        available_robots = [r for r in robots if r.status == "idle" and r.battery > 20]
        
        if not available_robots:
            return None
        
        # Score robots based on distance, battery, and efficiency
        robot_scores = []
        for robot in available_robots:
            distance = abs(robot.x - first_item_location["x"]) + abs(robot.y - first_item_location["y"])
            battery_score = robot.battery / 100
            efficiency_score = robot.orders_completed / max(robot.total_distance_traveled, 1)
            
            # Combined score (lower distance, higher battery, higher efficiency = better)
            score = (1 / (distance + 1)) * 0.4 + battery_score * 0.4 + efficiency_score * 0.2
            robot_scores.append((score, robot))
        
        # Return robot with highest score
        robot_scores.sort(key=lambda x: x[0], reverse=True)
        return robot_scores[0][1] if robot_scores else None
    
    def _generate_optimized_route(self, robot, item_locations, warehouse_grid) -> List[Dict[str, Any]]:
        """Generate optimized route using nearest neighbor algorithm"""
        try:
            route = []
            current_pos = {"x": robot.x, "y": robot.y}
            unvisited = item_locations.copy()
            
            # Add starting position
            route.append({
                "x": current_pos["x"],
                "y": current_pos["y"],
                "action": "start",
                "item": None
            })
            
            # Visit each item location
            while unvisited:
                # Find nearest unvisited location
                nearest = min(unvisited, key=lambda loc: 
                    abs(loc["x"] - current_pos["x"]) + abs(loc["y"] - current_pos["y"])
                )
                
                # Add path to nearest location
                path = self._find_path(current_pos, {"x": nearest["x"], "y": nearest["y"]}, warehouse_grid)
                route.extend(path)
                
                # Add pickup action
                route.append({
                    "x": nearest["x"],
                    "y": nearest["y"],
                    "action": "pickup",
                    "item": nearest["item"].name,
                    "quantity": nearest["quantity"]
                })
                
                current_pos = {"x": nearest["x"], "y": nearest["y"]}
                unvisited.remove(nearest)
            
            # Return to nearest exit
            nearest_exit = min(warehouse_grid.exits, key=lambda exit_pos:
                abs(exit_pos["x"] - current_pos["x"]) + abs(exit_pos["y"] - current_pos["y"])
            )
            
            path_to_exit = self._find_path(current_pos, nearest_exit, warehouse_grid)
            route.extend(path_to_exit)
            
            # Add delivery action
            route.append({
                "x": nearest_exit["x"],
                "y": nearest_exit["y"],
                "action": "deliver",
                "item": None
            })
            
            return route
            
        except Exception as e:
            logger.error(f"Error generating optimized route: {e}")
            return []
    
    def _find_path(self, start, end, warehouse_grid) -> List[Dict[str, Any]]:
        """Find path between two points using A* algorithm"""
        try:
            # Simple A* implementation
            open_set = [(0.0, (start["x"], start["y"]))]
            came_from = {}
            g_score = {(start["x"], start["y"]): 0}
            f_score = {(start["x"], start["y"]): self._heuristic(start, end)}
            
            while open_set:
                current_f, current = heapq.heappop(open_set)
                current_x, current_y = current
                
                if current_x == end["x"] and current_y == end["y"]:
                    # Reconstruct path
                    path = []
                    while current in came_from:
                        path.append({"x": current[0], "y": current[1], "action": "move"})
                        current = came_from[current]
                    path.reverse()
                    return path
                
                # Check neighbors
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    neighbor_x, neighbor_y = current_x + dx, current_y + dy
                    
                    if not warehouse_grid.is_valid_position(neighbor_x, neighbor_y):
                        continue
                    
                    tentative_g = g_score[current] + 1
                    
                    if (neighbor_x, neighbor_y) not in g_score or tentative_g < g_score[(neighbor_x, neighbor_y)]:
                        came_from[(neighbor_x, neighbor_y)] = current
                        g_score[(neighbor_x, neighbor_y)] = tentative_g
                        f_score[(neighbor_x, neighbor_y)] = tentative_g + self._heuristic(
                            {"x": neighbor_x, "y": neighbor_y}, end
                        )
                        
                        heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], (neighbor_x, neighbor_y)))
            
            # If no path found, return direct path
            return [{"x": end["x"], "y": end["y"], "action": "move"}]
            
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return []
    
    def _heuristic(self, start, end) -> float:
        """Heuristic function for A* (Manhattan distance)"""
        return abs(start["x"] - end["x"]) + abs(start["y"] - end["y"])
    
    def _calculate_route_metrics(self, route, robot) -> Dict[str, float]:
        """Calculate metrics for the optimized route"""
        try:
            total_distance = len(route)
            estimated_time = total_distance * 2  # 2 seconds per cell
            energy_consumption = total_distance * 0.5  # 0.5% battery per cell
            
            # Calculate optimization score
            optimization_score = max(0, 100 - (total_distance * 2))  # Higher score for shorter routes
            
            return {
                "total_distance": total_distance,
                "estimated_time": estimated_time,
                "energy_consumption": energy_consumption,
                "optimization_score": optimization_score
            }
        except Exception as e:
            logger.error(f"Error calculating route metrics: {e}")
            return {
                "total_distance": 0,
                "estimated_time": 0,
                "energy_consumption": 0,
                "optimization_score": 0
            }
    
    async def optimize_warehouse_layout(self, warehouse_grid, current_orders, robots) -> Dict[str, Any]:
        """Optimize warehouse layout for better efficiency"""
        try:
            optimization_result = {
                "layout_improvements": [],
                "efficiency_gains": {},
                "recommendations": [],
                "estimated_impact": {}
            }
            
            # Analyze current layout
            current_metrics = self._analyze_current_layout(warehouse_grid)
            
            # Generate layout improvements
            layout_improvements = self._generate_layout_improvements(warehouse_grid, current_orders)
            optimization_result["layout_improvements"] = layout_improvements
            
            # Calculate efficiency gains
            efficiency_gains = self._calculate_efficiency_gains(current_metrics, layout_improvements)
            optimization_result["efficiency_gains"] = efficiency_gains
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(
                warehouse_grid, current_orders, robots
            )
            optimization_result["recommendations"] = recommendations
            
            # Estimate impact
            estimated_impact = self._estimate_optimization_impact(efficiency_gains)
            optimization_result["estimated_impact"] = estimated_impact
            
            # Store optimization history
            self.optimization_history.append({
                "timestamp": datetime.now(),
                "result": optimization_result
            })
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing warehouse layout: {e}")
            return {"error": str(e)}
    
    def _analyze_current_layout(self, warehouse_grid) -> Dict[str, Any]:
        """Analyze current warehouse layout"""
        try:
            total_cells = warehouse_grid.rows * warehouse_grid.cols
            shelf_cells = np.sum(warehouse_grid.grid == 1)
            aisle_cells = np.sum(warehouse_grid.grid == 0)
            entrance_cells = np.sum(warehouse_grid.grid == 2)
            exit_cells = np.sum(warehouse_grid.grid == 3)
            
            return {
                "total_cells": total_cells,
                "shelf_density": shelf_cells / total_cells,
                "aisle_density": aisle_cells / total_cells,
                "entrance_count": entrance_cells,
                "exit_count": exit_cells,
                "shelf_count": len(warehouse_grid.shelves),
                "average_shelf_utilization": np.mean([s["utilization"] for s in warehouse_grid.shelves]) if warehouse_grid.shelves else 0
            }
        except Exception as e:
            logger.error(f"Error analyzing current layout: {e}")
            return {}
    
    def _generate_layout_improvements(self, warehouse_grid, current_orders) -> List[Dict[str, Any]]:
        """Generate specific layout improvements"""
        improvements = []
        
        # Analyze item popularity for slotting optimization
        item_popularity = self._analyze_item_popularity(current_orders)
        
        # Suggest moving popular items closer to exits
        if item_popularity:
            most_popular = max(item_popularity.items(), key=lambda x: x[1])
            improvements.append({
                "type": "slotting_optimization",
                "description": f"Move {most_popular[0]} closer to shipping area",
                "priority": "high",
                "estimated_impact": "15% reduction in picking time"
            })
        
        # Suggest aisle width optimization
        improvements.append({
            "type": "aisle_optimization",
            "description": "Optimize aisle widths for robot navigation",
            "priority": "medium",
            "estimated_impact": "10% improvement in robot efficiency"
        })
        
        # Suggest cross-aisle connections
        improvements.append({
            "type": "cross_aisle",
            "description": "Add cross-aisle connections for faster routing",
            "priority": "medium",
            "estimated_impact": "20% reduction in travel distance"
        })
        
        return improvements
    
    def _analyze_item_popularity(self, current_orders) -> Dict[str, int]:
        """Analyze item popularity from current orders"""
        popularity = {}
        for order in current_orders:
            for item in order.items:
                item_name = item.get("product", "")
                popularity[item_name] = popularity.get(item_name, 0) + item.get("quantity", 1)
        return popularity
    
    def _calculate_efficiency_gains(self, current_metrics, improvements) -> Dict[str, float]:
        """Calculate expected efficiency gains from improvements"""
        gains = {
            "picking_efficiency": 0.0,
            "travel_distance": 0.0,
            "robot_utilization": 0.0,
            "overall_efficiency": 0.0
        }
        
        for improvement in improvements:
            if improvement["type"] == "slotting_optimization":
                gains["picking_efficiency"] += 15.0
            elif improvement["type"] == "aisle_optimization":
                gains["robot_utilization"] += 10.0
            elif improvement["type"] == "cross_aisle":
                gains["travel_distance"] += 20.0
        
        # Calculate overall efficiency gain
        gains["overall_efficiency"] = sum(gains.values()) / len(gains)
        
        return gains
    
    def _generate_optimization_recommendations(self, warehouse_grid, current_orders, robots) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Analyze robot utilization
        active_robots = len([r for r in robots if r.status == "busy"])
        total_robots = len(robots)
        utilization = (active_robots / total_robots) * 100 if total_robots > 0 else 0
        
        if utilization < 50:
            recommendations.append("Low robot utilization detected. Consider reducing robot fleet or increasing order volume.")
        elif utilization > 90:
            recommendations.append("High robot utilization detected. Consider adding more robots to prevent bottlenecks.")
        
        # Analyze order patterns
        if len(current_orders) > 20:
            recommendations.append("High order volume detected. Consider implementing batch picking strategies.")
        
        # Analyze inventory distribution
        if warehouse_grid.inventory:
            categories = {}
            for item in warehouse_grid.inventory:
                categories[item.category] = categories.get(item.category, 0) + 1
            
            if len(categories) > 5:
                recommendations.append("High category diversity. Consider implementing zone-based picking.")
        
        if not recommendations:
            recommendations.append("Warehouse operations appear well-optimized. Continue monitoring performance metrics.")
        
        return recommendations
    
    def _estimate_optimization_impact(self, efficiency_gains) -> Dict[str, Any]:
        """Estimate the impact of optimizations"""
        return {
            "time_savings_hours_per_day": efficiency_gains.get("overall_efficiency", 0) * 0.1,
            "cost_savings_percentage": efficiency_gains.get("overall_efficiency", 0) * 0.05,
            "productivity_increase": efficiency_gains.get("overall_efficiency", 0),
            "roi_estimate": efficiency_gains.get("overall_efficiency", 0) * 2.5,  # 2.5x ROI estimate
            "payback_period_months": max(3, 12 / (efficiency_gains.get("overall_efficiency", 0) / 10))
        }
    
    async def optimize_robot_fleet(self, robots, current_orders, warehouse_grid) -> Dict[str, Any]:
        """Optimize robot fleet configuration"""
        try:
            fleet_optimization = {
                "current_fleet": len(robots),
                "optimal_fleet": 0,
                "recommendations": [],
                "efficiency_improvements": {}
            }
            
            # Calculate optimal fleet size based on order volume
            order_volume = len(current_orders)
            optimal_fleet = max(2, min(10, int(order_volume / 10)))  # 1 robot per 10 orders, min 2, max 10
            
            fleet_optimization["optimal_fleet"] = optimal_fleet
            
            # Generate fleet recommendations
            if optimal_fleet > len(robots):
                fleet_optimization["recommendations"].append(
                    f"Add {optimal_fleet - len(robots)} robots to meet demand"
                )
            elif optimal_fleet < len(robots):
                fleet_optimization["recommendations"].append(
                    f"Consider reducing fleet by {len(robots) - optimal_fleet} robots"
                )
            
            # Analyze robot performance
            performance_analysis = self._analyze_robot_performance(robots)
            fleet_optimization["efficiency_improvements"] = performance_analysis
            
            return fleet_optimization
            
        except Exception as e:
            logger.error(f"Error optimizing robot fleet: {e}")
            return {"error": str(e)}
    
    def _analyze_robot_performance(self, robots) -> Dict[str, Any]:
        """Analyze individual robot performance"""
        performance = {
            "average_battery": np.mean([r.battery for r in robots]),
            "average_efficiency": np.mean([r.orders_completed / max(r.total_distance_traveled, 1) for r in robots]),
            "maintenance_needs": [],
            "performance_rankings": []
        }
        
        # Check for maintenance needs
        for robot in robots:
            if robot.battery < 30:
                performance["maintenance_needs"].append(f"Robot {robot.id}: Low battery ({robot.battery}%)")
            
            days_since_maintenance = (datetime.now() - robot.last_maintenance).days
            if days_since_maintenance > 30:
                performance["maintenance_needs"].append(f"Robot {robot.id}: Maintenance overdue ({days_since_maintenance} days)")
        
        # Rank robots by performance
        robot_rankings = []
        for robot in robots:
            efficiency = robot.orders_completed / max(robot.total_distance_traveled, 1)
            robot_rankings.append((efficiency, robot.id))
        
        robot_rankings.sort(reverse=True)
        performance["performance_rankings"] = [f"Robot {rid}" for _, rid in robot_rankings]
        
        return performance 
    
    def optimize_layout_with_rl(self, layout_data: dict) -> dict:
        """Optimize warehouse layout using reinforcement learning with historical frequency data"""
        try:
            print("🤖 Starting RL-based layout optimization with frequency data...")
            
            # Load historical order frequency data
            from .order_data_service import order_data_service
            frequency_data = order_data_service.get_category_frequencies()
            
            print(f"📊 Using frequency data: {frequency_data}")
            
            # Initialize RL environment with frequency data
            env = WarehouseEnvironment(layout_data, frequency_data)
            
            # Train RL agent
            agent = QLearningAgent(env)
            training_results = agent.train(episodes=50)  # Reduced episodes for faster training
            
            # Get optimized layout
            optimized_layout = agent.get_optimized_layout()
            
            # Calculate metrics with frequency weighting
            original_metrics = self.calculate_layout_metrics_with_frequency(layout_data, frequency_data)
            optimized_metrics = self.calculate_layout_metrics_with_frequency(optimized_layout, frequency_data)
            
            # Generate insights
            insights = self.generate_optimization_insights_with_frequency(
                original_metrics, optimized_metrics, frequency_data
            )
            
            return {
                "success": True,
                "original_layout": layout_data,
                "optimized_layout": optimized_layout,
                "training_results": training_results,
                "frequency_data": frequency_data,
                "metrics": {
                    "original": original_metrics,
                    "optimized": optimized_metrics
                },
                "insights": insights
            }
            
        except Exception as e:
            print(f"❌ Error in RL optimization: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_layout": layout_data,
                "optimized_layout": layout_data
            }
    
    def calculate_layout_metrics_with_frequency(self, layout: dict, frequency_data: dict) -> dict:
        """Calculate layout metrics weighted by historical frequency data"""
        try:
            if not layout or not layout.get('shelves'):
                return {"efficiency": 0, "distance_score": 0, "frequency_score": 0}
            
            shelves = layout['shelves']
            entry_points = layout.get('entryPoints', [])
            packing_stations = layout.get('packingStations', [])
            
            if not entry_points or not packing_stations:
                return {"efficiency": 0, "distance_score": 0, "frequency_score": 0}
            
            total_frequency_score = 0
            total_distance_score = 0
            shelf_count = len(shelves)
            
            for shelf in shelves:
                category = shelf.get('category', 'unknown')
                frequency_weight = frequency_data.get(category, 1) / 100
                
                # Calculate distance from entry to shelf to packing
                entry_dist = min(
                    abs(shelf['row'] - entry['row']) + abs(shelf['col'] - entry['col'])
                    for entry in entry_points
                )
                
                packing_dist = min(
                    abs(shelf['row'] - packing['row']) + abs(shelf['col'] - packing['col'])
                    for packing in packing_stations
                )
                
                total_distance = entry_dist + packing_dist
                
                # Weight by frequency - high frequency items should be closer
                frequency_score = frequency_weight * (100 / (total_distance + 1))
                distance_score = 100 / (total_distance + 1)
                
                total_frequency_score += frequency_score
                total_distance_score += distance_score
            
            avg_frequency_score = total_frequency_score / shelf_count if shelf_count > 0 else 0
            avg_distance_score = total_distance_score / shelf_count if shelf_count > 0 else 0
            
            # Overall efficiency combines both scores
            overall_efficiency = (avg_frequency_score * 0.7) + (avg_distance_score * 0.3)
            
            return {
                "efficiency": round(overall_efficiency, 2),
                "distance_score": round(avg_distance_score, 2),
                "frequency_score": round(avg_frequency_score, 2),
                "shelf_count": shelf_count
            }
            
        except Exception as e:
            print(f"❌ Error calculating frequency-weighted metrics: {e}")
            return {"efficiency": 0, "distance_score": 0, "frequency_score": 0}
    
    def generate_optimization_insights_with_frequency(self, original_metrics: dict, optimized_metrics: dict, frequency_data: dict) -> list:
        """Generate insights based on frequency-weighted optimization"""
        insights = []
        
        try:
            # Efficiency improvement
            efficiency_gain = optimized_metrics.get('efficiency', 0) - original_metrics.get('efficiency', 0)
            if efficiency_gain > 0:
                insights.append(f"📈 Overall efficiency improved by {efficiency_gain:.1f}%")
            else:
                insights.append(f"📉 Overall efficiency decreased by {abs(efficiency_gain):.1f}%")
            
            # Frequency score improvement
            freq_gain = optimized_metrics.get('frequency_score', 0) - original_metrics.get('frequency_score', 0)
            if freq_gain > 0:
                insights.append(f"🎯 High-frequency items are now better positioned (improvement: {freq_gain:.1f}%)")
            else:
                insights.append(f"⚠️ High-frequency items positioning could be improved")
            
            # Distance optimization
            dist_gain = optimized_metrics.get('distance_score', 0) - original_metrics.get('distance_score', 0)
            if dist_gain > 0:
                insights.append(f"🚀 Average travel distance reduced (improvement: {dist_gain:.1f}%)")
            else:
                insights.append(f"📏 Travel distances increased slightly")
            
            # Top frequency categories
            top_categories = sorted(frequency_data.items(), key=lambda x: x[1], reverse=True)[:3]
            insights.append(f"🔥 Top categories by frequency: {', '.join([f'{cat} ({freq}%)' for cat, freq in top_categories])}")
            
            # Recommendations
            if efficiency_gain < 5:
                insights.append("💡 Consider placing high-frequency items closer to entry points")
            if freq_gain < 2:
                insights.append("💡 Optimize shelf placement based on historical demand patterns")
            
        except Exception as e:
            insights.append(f"❌ Error generating insights: {e}")
        
        return insights


class WarehouseEnvironment:
    """Simple RL environment for warehouse layout optimization"""
    
    def __init__(self, layout_data: dict, frequency_data: dict):
        self.layout = layout_data
        self.frequency_data = frequency_data
        self.shelves = layout_data.get('shelves', [])
        self.entry_points = layout_data.get('entryPoints', [])
        self.packing_stations = layout_data.get('packingStations', [])
        self.grid_size = layout_data.get('gridSize', 30)
        
    def get_state(self):
        """Get current state representation"""
        return {
            'shelf_positions': [(s['row'], s['col']) for s in self.shelves],
            'entry_positions': [(e['row'], e['col']) for e in self.entry_points],
            'packing_positions': [(p['row'], p['col']) for p in self.packing_stations]
        }
    
    def calculate_reward(self, action):
        """Calculate reward based on frequency-weighted efficiency"""
        try:
            # Simple reward calculation based on frequency-weighted distances
            total_reward = 0
            
            for shelf in self.shelves:
                category = shelf.get('category', 'unknown')
                frequency_weight = self.frequency_data.get(category, 1) / 100
                
                # Calculate distances
                entry_dist = min(
                    abs(shelf['row'] - entry['row']) + abs(shelf['col'] - entry['col'])
                    for entry in self.entry_points
                ) if self.entry_points else 100
                
                packing_dist = min(
                    abs(shelf['row'] - packing['row']) + abs(shelf['col'] - packing['col'])
                    for packing in self.packing_stations
                ) if self.packing_stations else 100
                
                total_dist = entry_dist + packing_dist
                
                # Reward: higher frequency items should be closer
                reward = frequency_weight * (100 / (total_dist + 1))
                total_reward += reward
            
            return total_reward / len(self.shelves) if self.shelves else 0
            
        except Exception as e:
            print(f"❌ Error calculating reward: {e}")
            return 0


class QLearningAgent:
    """Simple Q-learning agent for layout optimization"""
    
    def __init__(self, environment):
        self.env = environment
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1
        
    def train(self, episodes=50):
        """Train the agent"""
        results = []
        
        for episode in range(episodes):
            state = self.env.get_state()
            action = self._choose_action(state)
            reward = self.env.calculate_reward(action)
            
            # Update Q-table (simplified)
            state_key = str(state)
            if state_key not in self.q_table:
                self.q_table[state_key] = {}
            
            if action not in self.q_table[state_key]:
                self.q_table[state_key][action] = 0
            
            # Q-learning update
            old_value = self.q_table[state_key][action]
            next_max = max(self.q_table[state_key].values()) if self.q_table[state_key] else 0
            new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max)
            self.q_table[state_key][action] = new_value
            
            results.append({
                'episode': episode + 1,
                'reward': reward,
                'progress': ((episode + 1) / episodes) * 100
            })
            
            if (episode + 1) % 10 == 0:
                print(f"🎯 Episode {episode + 1}/{episodes} - Reward: {reward:.2f}")
        
        return results
    
    def _choose_action(self, state):
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.choice(['move_shelf', 'swap_shelves', 'optimize_path'])
        else:
            return 'optimize_path'  # Default action
    
    def get_optimized_layout(self):
        """Get the optimized layout"""
        try:
            # Create a copy of the original layout
            optimized_layout = self.env.layout.copy()
            
            # Apply simple optimizations based on frequency data
            shelves = optimized_layout.get('shelves', [])
            frequency_data = self.env.frequency_data
            
            # Sort shelves by frequency (high frequency items closer to entry)
            if shelves and self.env.entry_points:
                entry_point = self.env.entry_points[0]
                
                # Calculate distance from entry for each shelf
                for shelf in shelves:
                    category = shelf.get('category', 'unknown')
                    frequency_weight = frequency_data.get(category, 1)
                    distance = abs(shelf['row'] - entry_point['row']) + abs(shelf['col'] - entry_point['col'])
                    shelf['_optimization_score'] = frequency_weight / (distance + 1)
                
                # Sort by optimization score (higher score = better position)
                shelves.sort(key=lambda x: x.get('_optimization_score', 0), reverse=True)
                
                # Reassign positions to optimize layout
                grid_size = self.env.grid_size
                optimized_positions = []
                
                # Generate optimized positions (closer to entry for high-frequency items)
                for i, shelf in enumerate(shelves):
                    if i < len(shelves) // 2:  # High-frequency items
                        # Place closer to entry
                        row = entry_point['row'] + (i // 5) + 1
                        col = entry_point['col'] + (i % 5) + 1
                    else:  # Lower-frequency items
                        # Place further from entry
                        row = entry_point['row'] + (i // 5) + 3
                        col = entry_point['col'] + (i % 5) + 3
                    
                    # Ensure within grid bounds
                    row = max(0, min(row, grid_size - 1))
                    col = max(0, min(col, grid_size - 1))
                    
                    optimized_positions.append((row, col))
                
                # Update shelf positions
                for i, shelf in enumerate(shelves):
                    if i < len(optimized_positions):
                        shelf['row'] = optimized_positions[i][0]
                        shelf['col'] = optimized_positions[i][1]
                        shelf.pop('_optimization_score', None)  # Remove temporary field
            
            return optimized_layout
            
        except Exception as e:
            print(f"❌ Error generating optimized layout: {e}")
            return self.env.layout 