// WebSocket Communication for Smart Warehouse Simulator

class WebSocketManager {
    constructor() {
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.messageHandlers = new Map();
        
        this.init();
    }
    
    init() {
        this.setupMessageHandlers();
        this.connect();
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/warehouse`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('🔗 WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.showConnectionStatus('Connected', 'success');
                
                // Send initial status request
                this.sendMessage({
                    type: 'request_status',
                    timestamp: new Date().toISOString()
                });
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.showConnectionStatus('Disconnected', 'error');
                
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.showConnectionStatus('Connection Error', 'error');
            };
            
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.showConnectionStatus('Connection Failed', 'error');
        }
    }
    
    setupMessageHandlers() {
        // Warehouse updates
        this.messageHandlers.set('warehouse_update', (data) => {
            this.handleWarehouseUpdate(data);
        });
        
        // Order updates
        this.messageHandlers.set('order_update', (data) => {
            this.handleOrderUpdate(data);
        });
        
        // Robot status updates
        this.messageHandlers.set('robot_status', (data) => {
            this.handleRobotUpdate(data);
        });
        
        // Analytics updates
        this.messageHandlers.set('analytics_update', (data) => {
            this.handleAnalyticsUpdate(data);
        });
        
        // Optimization results
        this.messageHandlers.set('optimization_result', (data) => {
            this.handleOptimizationResult(data);
        });
        
        // Alerts
        this.messageHandlers.set('alert', (data) => {
            this.handleAlert(data);
        });
        
        // System status
        this.messageHandlers.set('system_status', (data) => {
            this.handleSystemStatus(data);
        });
        
        // Pong response
        this.messageHandlers.set('pong', (data) => {
            this.handlePong(data);
        });
    }
    
    handleMessage(data) {
        const handler = this.messageHandlers.get(data.type);
        if (handler) {
            handler(data);
        } else {
            console.log('Unknown message type:', data.type);
        }
    }
    
    handleWarehouseUpdate(data) {
        // Update main app data
        if (window.warehouseApp) {
            window.warehouseApp.handleWarehouseUpdate(data);
        }
        
        // Update charts
        if (window.chartManager && data.analytics) {
            window.chartManager.updatePerformanceChart(data.analytics);
        }
    }
    
    handleOrderUpdate(data) {
        if (window.warehouseApp) {
            window.warehouseApp.handleOrderUpdate(data);
        }
        
        // Show notification
        this.showNotification(`Order ${data.order.id} ${data.order.status}`, 'info');
    }
    
    handleRobotUpdate(data) {
        if (window.warehouseApp) {
            window.warehouseApp.handleRobotUpdate(data);
        }
        
        // Show notification for status changes
        if (data.robot.status === 'low_battery') {
            this.showNotification(`Robot ${data.robot.id} has low battery`, 'warning');
        }
    }
    
    handleAnalyticsUpdate(data) {
        if (window.warehouseApp) {
            window.warehouseApp.handleAnalyticsUpdate(data);
        }
        
        // Update charts
        if (window.chartManager) {
            window.chartManager.updatePerformanceChart(data.data);
        }
    }
    
    handleOptimizationResult(data) {
        if (window.warehouseApp) {
            window.warehouseApp.handleOptimizationResult(data);
        }
        
        this.showNotification('Optimization completed successfully', 'success');
    }
    
    handleAlert(data) {
        this.showNotification(data.message, data.severity || 'info');
    }
    
    handleSystemStatus(data) {
        console.log('System status:', data);
    }
    
    handlePong(data) {
        // Connection is alive
        console.log('Pong received');
    }
    
    sendMessage(message) {
        if (this.websocket && this.isConnected) {
            try {
                this.websocket.send(JSON.stringify(message));
            } catch (error) {
                console.error('Error sending WebSocket message:', error);
            }
        } else {
            console.warn('WebSocket not connected, message not sent:', message);
        }
    }
    
    sendPing() {
        this.sendMessage({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }
    
    requestOptimization() {
        this.sendMessage({
            type: 'optimization_request',
            timestamp: new Date().toISOString()
        });
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }
    
    showConnectionStatus(message, type) {
        // Update connection status in UI
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `connection-status ${type}`;
        }
        
        // Show notification for connection changes
        if (type === 'error' || type === 'success') {
            this.showNotification(`WebSocket: ${message}`, type);
        }
    }
    
    showNotification(message, type = 'info') {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification(message, type);
        } else {
            // Fallback notification
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
        }
    }
    
    // Public methods for external use
    sendWarehouseCommand(command, data = {}) {
        this.sendMessage({
            type: 'warehouse_command',
            command: command,
            data: data,
            timestamp: new Date().toISOString()
        });
    }
    
    requestAnalytics() {
        this.sendMessage({
            type: 'request_analytics',
            timestamp: new Date().toISOString()
        });
    }
    
    requestPredictions() {
        this.sendMessage({
            type: 'request_predictions',
            timestamp: new Date().toISOString()
        });
    }
}

// Global WebSocket manager instance
window.websocketManager = new WebSocketManager();

// Start ping/pong to keep connection alive
setInterval(() => {
    if (window.websocketManager && window.websocketManager.isConnected) {
        window.websocketManager.sendPing();
    }
}, 30000); // Send ping every 30 seconds

// Global functions for HTML onclick handlers
function requestOptimization() {
    if (window.websocketManager) {
        window.websocketManager.requestOptimization();
    }
}

function requestAnalytics() {
    if (window.websocketManager) {
        window.websocketManager.requestAnalytics();
    }
}

function requestPredictions() {
    if (window.websocketManager) {
        window.websocketManager.requestPredictions();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketManager;
} 