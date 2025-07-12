#!/usr/bin/env python3
"""
Smart Warehouse Simulator - FastAPI Backend
Simple server to serve the frontend application
"""

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# Import order data service
from services.order_data_service import order_data_service

# Create FastAPI app
app = FastAPI(
    title="Smart Warehouse Optimizer",
    description="AI-Powered Warehouse Management System - Hackathon Winner",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# WebSocket connection for real-time updates
@app.websocket("/ws/warehouse")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
            await websocket.send_text("Connected to Smart Warehouse Optimizer")
    except:
        pass

# Serve the main HTML file
@app.get("/")
async def read_root():
    return FileResponse("../frontend/templates/index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Smart Warehouse Optimizer is running!"}

# API documentation endpoint
@app.get("/api/docs")
async def api_docs():
    return {"message": "API documentation available at /docs"}

# Get order frequency data
@app.get("/api/order-frequency")
async def get_order_frequency():
    """Get historical order frequency data for warehouse categories"""
    try:
        frequency_data = order_data_service.get_category_frequencies()
        warehouse_analytics = order_data_service.get_warehouse_analytics()
        
        return {
            "success": True,
            "frequency_data": frequency_data,
            "warehouse_analytics": warehouse_analytics,
            "message": "Historical order frequency data loaded successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to load order frequency data"
        }

# Get category analytics
@app.get("/api/category-analytics/{category}")
async def get_category_analytics(category: str):
    """Get detailed analytics for a specific category"""
    try:
        analytics = order_data_service.get_category_analytics(category)
        peak_hours = order_data_service.get_peak_hours(category)
        correlated_categories = order_data_service.get_correlated_categories(category)
        
        return {
            "success": True,
            "category": category,
            "analytics": analytics,
            "peak_hours": peak_hours,
            "correlated_categories": correlated_categories
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "category": category
        }

if __name__ == "__main__":
    print("🚀 Starting Smart Warehouse Optimizer...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📊 API docs at: http://localhost:8000/docs")
    print("🔗 WebSocket at: ws://localhost:8000/ws/warehouse")
    print()
    print("🎯 Features:")
    print("   • Custom Layout Editor")
    print("   • Realistic Simulation")
    print("   • AI-Powered Optimization")
    print("   • Performance Analytics")
    print("   • Heatmap Visualization")
    print()
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 