from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn
import json
import asyncio
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

# Import our custom modules
from models.warehouse import WarehouseGrid, InventoryItem, Order, Robot, Analytics
from services.ai_service import AIService
from services.optimization_service import OptimizationService
from services.analytics_service import AnalyticsService
from database.database import DatabaseManager
from utils.websocket_manager import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Warehouse Simulator",
    description="AI-Powered Warehouse Management System with Real-time Analytics",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()
optimization_service = OptimizationService()
analytics_service = AnalyticsService()
db_manager = DatabaseManager()
websocket_manager = ConnectionManager()

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend/templates")

# Global warehouse state
warehouse_grid = WarehouseGrid(rows=50, cols=50)
current_orders = []
robots = []
analytics_data = Analytics()

@app.on_event("startup")
async def startup_event():
    """Initialize warehouse on startup"""
    await db_manager.initialize_database()
    await initialize_warehouse()
    logger.info("Smart Warehouse Simulator started successfully!")

async def initialize_warehouse():
    """Initialize warehouse with shelves, inventory, and robots"""
    global warehouse_grid, robots, analytics_data
    
    # Create warehouse layout with shelves
    warehouse_grid.create_shelf_layout()
    
    # Initialize inventory with realistic products
    await warehouse_grid.initialize_inventory()
    
    # Initialize robots
    robots = [
        Robot(id=1, x=5, y=5, status="idle", battery=100),
        Robot(id=2, x=15, y=5, status="idle", battery=95),
        Robot(id=3, x=25, y=5, status="idle", battery=88),
        Robot(id=4, x=35, y=5, status="idle", battery=92)
    ]
    
    # Initialize analytics
    analytics_data = Analytics()
    
    logger.info(f"Warehouse initialized with {len(robots)} robots and {len(warehouse_grid.inventory)} items")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/warehouse/status")
async def get_warehouse_status():
    """Get current warehouse status"""
    return {
        "grid": warehouse_grid.grid.tolist(),
        "inventory_count": len(warehouse_grid.inventory),
        "active_orders": len(current_orders),
        "robots": [robot.to_dict() for robot in robots],
        "analytics": analytics_data.to_dict(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/warehouse/grid")
async def get_warehouse_grid():
    """Get warehouse grid layout"""
    return {
        "grid": warehouse_grid.grid.tolist(),
        "rows": warehouse_grid.rows,
        "cols": warehouse_grid.cols
    }

@app.get("/api/inventory")
async def get_inventory():
    """Get current inventory"""
    return {
        "items": [item.to_dict() for item in warehouse_grid.inventory],
        "total_items": len(warehouse_grid.inventory),
        "categories": warehouse_grid.get_category_stats()
    }

@app.post("/api/orders/create")
async def create_order(order_data: Dict[str, Any]):
    """Create a new order"""
    try:
        order = Order(
            id=len(current_orders) + 1,
            customer_name=order_data.get("customer_name", "Customer"),
            items=order_data.get("items", []),
            priority=order_data.get("priority", "normal"),
            status="pending"
        )
        
        current_orders.append(order)
        
        # Trigger AI optimization for order fulfillment
        optimized_route = await optimization_service.optimize_order_fulfillment(
            order, warehouse_grid, robots
        )
        
        # Assign robot to fulfill order
        if optimized_route:
            assigned_robot = await assign_robot_to_order(order, optimized_route)
            if assigned_robot:
                order.status = "processing"
                order.assigned_robot = assigned_robot.id
        
        return {
            "success": True,
            "order": order.to_dict(),
            "optimized_route": optimized_route
        }
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def assign_robot_to_order(order: Order, route: List[Dict]):
    """Assign the best available robot to fulfill an order"""
    available_robots = [r for r in robots if r.status == "idle" and r.battery > 20]
    
    if not available_robots:
        return None
    
    # Select robot with highest battery and closest to start point
    best_robot = max(available_robots, key=lambda r: r.battery)
    best_robot.status = "busy"
    best_robot.current_order = order.id
    best_robot.route = route
    
    return best_robot

@app.get("/api/orders")
async def get_orders():
    """Get all orders"""
    return {
        "orders": [order.to_dict() for order in current_orders],
        "total_orders": len(current_orders),
        "pending_orders": len([o for o in current_orders if o.status == "pending"]),
        "processing_orders": len([o for o in current_orders if o.status == "processing"]),
        "completed_orders": len([o for o in current_orders if o.status == "completed"])
    }

@app.get("/api/robots")
async def get_robots():
    """Get all robots status"""
    return {
        "robots": [robot.to_dict() for robot in robots],
        "active_robots": len([r for r in robots if r.status == "busy"]),
        "idle_robots": len([r for r in robots if r.status == "idle"])
    }

@app.get("/api/analytics")
async def get_analytics():
    """Get warehouse analytics"""
    analytics = await analytics_service.generate_analytics(
        warehouse_grid, current_orders, robots
    )
    return analytics

@app.get("/api/analytics/predictions")
async def get_predictions():
    """Get AI-powered predictions"""
    predictions = await ai_service.generate_predictions(
        warehouse_grid, current_orders, analytics_data
    )
    return predictions

@app.post("/api/warehouse/optimize")
async def optimize_warehouse():
    """Trigger warehouse optimization"""
    try:
        optimization_result = await optimization_service.optimize_warehouse_layout(
            warehouse_grid, current_orders, robots
        )
        return {
            "success": True,
            "optimization": optimization_result
        }
    except Exception as e:
        logger.error(f"Error optimizing warehouse: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/warehouse")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Send real-time warehouse updates
            data = {
                "type": "warehouse_update",
                "grid": warehouse_grid.grid.tolist(),
                "robots": [robot.to_dict() for robot in robots],
                "orders": [order.to_dict() for order in current_orders],
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)  # Update every second
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.post("/api/simulation/start")
async def start_simulation(background_tasks: BackgroundTasks):
    """Start the warehouse simulation"""
    background_tasks.add_task(run_simulation)
    return {"message": "Simulation started successfully"}

async def run_simulation():
    """Run the warehouse simulation"""
    while True:
        try:
            # Generate random orders
            if random.random() < 0.3:  # 30% chance to create new order
                await generate_random_order()
            
            # Update robot positions and status
            await update_robots()
            
            # Update analytics
            await update_analytics()
            
            # Broadcast updates to all connected clients
            await websocket_manager.broadcast_warehouse_update(
                warehouse_grid, robots, current_orders
            )
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
            await asyncio.sleep(5)

async def generate_random_order():
    """Generate a random order for simulation"""
    customers = ["Amazon", "Walmart", "Target", "Best Buy", "Home Depot"]
    products = ["Laptop", "Phone", "Tablet", "Headphones", "Camera", "Speaker"]
    
    order = Order(
        id=len(current_orders) + 1,
        customer_name=random.choice(customers),
        items=[{"product": random.choice(products), "quantity": random.randint(1, 5)}],
        priority=random.choice(["low", "normal", "high", "urgent"]),
        status="pending"
    )
    
    current_orders.append(order)
    logger.info(f"Generated new order: {order.id}")

async def update_robots():
    """Update robot positions and status"""
    for robot in robots:
        if robot.status == "busy" and robot.route:
            # Move robot along route
            if robot.current_position < len(robot.route) - 1:
                robot.current_position += 1
                next_pos = robot.route[robot.current_position]
                robot.x, robot.y = next_pos["x"], next_pos["y"]
                robot.battery = max(0, robot.battery - 0.1)
            else:
                # Route completed
                robot.status = "idle"
                robot.current_order = None
                robot.route = []
                robot.current_position = 0
                robot.battery = max(0, robot.battery - 5)  # Battery drain for completing task

async def update_analytics():
    """Update analytics data"""
    analytics_data.total_orders = len(current_orders)
    analytics_data.completed_orders = len([o for o in current_orders if o.status == "completed"])
    analytics_data.active_robots = len([r for r in robots if r.status == "busy"])
    analytics_data.average_battery = sum(r.battery for r in robots) / len(robots)
    analytics_data.last_updated = datetime.now()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 