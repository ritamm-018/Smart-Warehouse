import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected WebSocket clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_warehouse_update(self, warehouse_grid, robots, current_orders):
        """Broadcast warehouse status update to all clients"""
        try:
            update_data = {
                "type": "warehouse_update",
                "timestamp": datetime.now().isoformat(),
                "grid": warehouse_grid.grid.tolist(),
                "robots": [robot.to_dict() for robot in robots],
                "orders": [order.to_dict() for order in current_orders],
                "analytics": {
                    "total_orders": len(current_orders),
                    "active_robots": len([r for r in robots if r.status == "busy"]),
                    "idle_robots": len([r for r in robots if r.status == "idle"]),
                    "completion_rate": len([o for o in current_orders if o.status == "completed"]) / len(current_orders) * 100 if current_orders else 0
                }
            }
            
            await self.broadcast(json.dumps(update_data))
            
        except Exception as e:
            logger.error(f"Error broadcasting warehouse update: {e}")
    
    async def broadcast_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Broadcast alert to all clients"""
        try:
            alert_data = {
                "type": "alert",
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
    
    async def broadcast_optimization_result(self, optimization_data: Dict[str, Any]):
        """Broadcast optimization results to all clients"""
        try:
            optimization_message = {
                "type": "optimization_result",
                "data": optimization_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(optimization_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting optimization result: {e}")
    
    async def broadcast_analytics_update(self, analytics_data: Dict[str, Any]):
        """Broadcast analytics update to all clients"""
        try:
            analytics_message = {
                "type": "analytics_update",
                "data": analytics_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(analytics_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting analytics update: {e}")
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    async def send_system_status(self, websocket: WebSocket):
        """Send system status to specific client"""
        try:
            status_data = {
                "type": "system_status",
                "connections": len(self.active_connections),
                "timestamp": datetime.now().isoformat(),
                "status": "operational"
            }
            
            await self.send_personal_message(json.dumps(status_data), websocket)
            
        except Exception as e:
            logger.error(f"Error sending system status: {e}")
    
    async def broadcast_robot_status(self, robot_data: Dict[str, Any]):
        """Broadcast robot status update"""
        try:
            robot_message = {
                "type": "robot_status",
                "robot": robot_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(robot_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting robot status: {e}")
    
    async def broadcast_order_update(self, order_data: Dict[str, Any]):
        """Broadcast order status update"""
        try:
            order_message = {
                "type": "order_update",
                "order": order_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(order_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting order update: {e}")
    
    async def broadcast_inventory_update(self, inventory_data: Dict[str, Any]):
        """Broadcast inventory update"""
        try:
            inventory_message = {
                "type": "inventory_update",
                "inventory": inventory_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(inventory_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting inventory update: {e}")
    
    async def broadcast_prediction_update(self, prediction_data: Dict[str, Any]):
        """Broadcast AI prediction update"""
        try:
            prediction_message = {
                "type": "prediction_update",
                "predictions": prediction_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(json.dumps(prediction_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting prediction update: {e}")
    
    async def handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await self.send_personal_message(json.dumps({"type": "pong"}), websocket)
            
            elif message_type == "request_status":
                # Send current warehouse status
                # This would typically fetch from the main application state
                status_response = {
                    "type": "status_response",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Status request received"
                }
                await self.send_personal_message(json.dumps(status_response), websocket)
            
            elif message_type == "optimization_request":
                # Handle optimization request
                optimization_response = {
                    "type": "optimization_response",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Optimization request received"
                }
                await self.send_personal_message(json.dumps(optimization_response), websocket)
            
            else:
                logger.info(f"Received unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Received invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def cleanup_disconnected_connections(self):
        """Clean up any disconnected connections"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                # Try to send a ping to check if connection is still alive
                await connection.send_text(json.dumps({"type": "ping"}))
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
        
        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} disconnected connections") 