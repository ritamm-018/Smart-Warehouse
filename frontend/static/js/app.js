// Smart Warehouse Simulator - Main Application

class WarehouseApp {
    constructor() {
        console.log('WarehouseApp constructor called');
        this.currentSection = 'layout-editor';
        this.websocket = null;
        this.data = {
            orders: [],
            robots: [
                { id: 1, x: 5, y: 5, status: 'idle', battery: 100, current_order: null },
                { id: 2, x: 15, y: 5, status: 'idle', battery: 95, current_order: null },
                { id: 3, x: 25, y: 5, status: 'idle', battery: 88, current_order: null },
                { id: 4, x: 35, y: 5, status: 'idle', battery: 92, current_order: null }
            ],
            inventory: [
                { id: 1, name: 'Laptop', category: 'Electronics', quantity: 50, price: 999 },
                { id: 2, name: 'Smartphone', category: 'Electronics', quantity: 100, price: 699 },
                { id: 3, name: 'Tablet', category: 'Electronics', quantity: 75, price: 399 },
                { id: 4, name: 'Headphones', category: 'Audio', quantity: 200, price: 99 },
                { id: 5, name: 'Mouse', category: 'Accessories', quantity: 150, price: 29 }
            ],
            analytics: {},
            predictions: {}
        };
        this.simulationRunning = false;
        
        this.init();
    }
    
    async init() {
        try {
            console.log('Starting app initialization...');
            // Show loading screen
            this.showLoading();
            
            // Initialize event listeners
            console.log('Initializing event listeners...');
            this.initEventListeners();
            
            // Load initial data
            console.log('Loading initial data...');
            await this.loadInitialData();
            
            // Initialize charts
            console.log('Initializing charts...');
            this.initCharts();
            
            // Hide loading screen and show app
            console.log('Hiding loading screen...');
            this.hideLoading();
            
            // Show layout-editor section by default
            console.log('Showing layout-editor section by default...');
            this.showSection('layout-editor');
            
            // Start real-time updates
            console.log('Starting real-time updates...');
            this.startRealTimeUpdates();
            
            console.log('Smart Warehouse Simulator initialized successfully!');
            
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showNotification('Error initializing application', 'error');
            // Force hide loading screen on error
            this.hideLoading();
        }
    }
    
    showLoading() {
        console.log('Showing loading screen...');
        const loadingScreen = document.getElementById('loading-screen');
        const app = document.getElementById('app');
        if (loadingScreen) loadingScreen.style.display = 'flex';
        if (app) app.style.display = 'none';
    }
    
    hideLoading() {
        console.log('Hiding loading screen...');
        const loadingScreen = document.getElementById('loading-screen');
        const app = document.getElementById('app');
        if (loadingScreen) loadingScreen.style.display = 'none';
        if (app) app.style.display = 'block';
    }
    
    async loadInitialData() {
        try {
            console.log('Loading warehouse status...');
            // Try to load from API, but use default data if it fails
            try {
                const statusResponse = await fetch('/api/warehouse/status');
                const statusData = await statusResponse.json();
                this.data.robots = statusData.robots || this.data.robots;
            } catch (e) {
                console.log('Using default robot data');
            }
            
            try {
                const inventoryResponse = await fetch('/api/inventory');
                const inventoryData = await inventoryResponse.json();
                this.data.inventory = inventoryData.items || this.data.inventory;
            } catch (e) {
                console.log('Using default inventory data');
            }
            
            try {
                const ordersResponse = await fetch('/api/orders');
                const ordersData = await ordersResponse.json();
                this.data.orders = ordersData.orders || this.data.orders;
            } catch (e) {
                console.log('Using default orders data');
            }
            
            console.log('Data loaded successfully:', this.data);
            
            // Update UI
            this.updateDashboard();
            this.updateInventoryGrid();
            this.updateOrdersList();
            this.updateRobotsGrid();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading data, using default values', 'warning');
        }
    }
    
    initCharts() {
        // Initialize order processing chart
        this.initOrderChart();
        this.initRobotChart();
    }
    
    initOrderChart() {
        const ctx = document.getElementById('orderChart');
        if (!ctx) return;
        
        this.charts = this.charts || {};
        this.charts.orderChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['9:00', '9:15', '9:30', '9:45', '10:00', '10:15', '10:30', '10:45'],
                datasets: [{
                    label: 'Orders Processed',
                    data: [5, 8, 12, 15, 18, 22, 25, 28],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    initRobotChart() {
        const ctx = document.getElementById('robotChart');
        if (!ctx) return;
        
        this.charts.robotChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Idle', 'Charging'],
                datasets: [{
                    data: [2, 1, 1],
                    backgroundColor: ['#059669', '#6b7280', '#d97706']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    initEventListeners() {
        // Navigation dropdown
        document.querySelectorAll('.navigation-dropdown .dropdown-item').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('href').substring(1);
                this.showSection(section);
                
                // Update active state in dropdown
                document.querySelectorAll('.navigation-dropdown .dropdown-item').forEach(item => {
                    item.classList.remove('active');
                });
                e.target.classList.add('active');
            });
        });
    }
    
    updateDashboard() {
        // Update KPI cards
        const totalOrdersEl = document.getElementById('total-orders');
        const activeRobotsEl = document.getElementById('active-robots');
        const completionRateEl = document.getElementById('completion-rate');
        const totalValueEl = document.getElementById('total-value');
        
        if (totalOrdersEl) totalOrdersEl.textContent = this.data.orders.length;
        if (activeRobotsEl) activeRobotsEl.textContent = this.data.robots.filter(r => r.status === 'busy').length;
        
        const completedOrders = this.data.orders.filter(o => o.status === 'completed').length;
        const completionRate = this.data.orders.length > 0 ? (completedOrders / this.data.orders.length * 100).toFixed(1) : 0;
        if (completionRateEl) completionRateEl.textContent = `${completionRate}%`;
        
        const totalValue = this.data.orders.reduce((sum, order) => sum + (order.total_value || 0), 0);
        if (totalValueEl) totalValueEl.textContent = `$${totalValue.toLocaleString()}`;
        
        // Update charts
        this.updateOrderChart();
        this.updateRobotChart();
    }
    
    updateOrderChart() {
        if (!this.charts || !this.charts.orderChart) return;
        
        const now = new Date();
        const labels = [];
        const data = [];
        
        // Generate last 8 time points
        for (let i = 7; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 900000); // Every 15 minutes
            labels.push(time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
            data.push(Math.floor(Math.random() * 10) + 5); // Random data for demo
        }
        
        this.charts.orderChart.data.labels = labels;
        this.charts.orderChart.data.datasets[0].data = data;
        this.charts.orderChart.update();
    }
    
    updateRobotChart() {
        if (!this.charts || !this.charts.robotChart) return;
        
        const active = this.data.robots.filter(r => r.status === 'busy').length;
        const idle = this.data.robots.filter(r => r.status === 'idle').length;
        const charging = this.data.robots.filter(r => r.status === 'charging').length;
        
        this.charts.robotChart.data.datasets[0].data = [active, idle, charging];
        this.charts.robotChart.update();
    }
    
    updateInventoryGrid() {
        const grid = document.getElementById('inventory-grid');
        if (!grid) return;
        
        grid.innerHTML = this.data.inventory.map(item => `
            <div class="inventory-item">
                <div class="inventory-header">
                    <span class="inventory-name">${item.name}</span>
                    <span class="inventory-category">${item.category}</span>
                </div>
                <div class="inventory-stats">
                    <div class="stat-item">
                        <div class="stat-value">${item.quantity}</div>
                        <div class="stat-label">In Stock</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">$${item.price}</div>
                        <div class="stat-label">Price</div>
                    </div>
                </div>
                <div class="inventory-actions">
                    <button class="btn btn-sm btn-primary" onclick="restockItem(${item.id})">
                        <i class="fas fa-plus me-1"></i>Restock
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="viewItemDetails(${item.id})">
                        <i class="fas fa-eye me-1"></i>Details
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    updateOrdersList() {
        const list = document.getElementById('orders-list');
        if (!list) return;
        
        if (this.data.orders.length === 0) {
            list.innerHTML = '<div class="text-center text-muted p-4">No orders yet. Create your first order!</div>';
            return;
        }
        
        list.innerHTML = this.data.orders.map(order => `
            <div class="order-item">
                <div class="order-status ${order.status}"></div>
                <div class="order-content">
                    <div class="order-customer">${order.customer_name}</div>
                    <div class="order-items">
                        ${order.items ? order.items.map(item => `${item.product} (${item.quantity})`).join(', ') : 'No items'}
                    </div>
                </div>
                <div class="order-actions">
                    <span class="badge bg-${this.getStatusColor(order.status)}">${order.status}</span>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewOrderDetails(${order.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    updateRobotsGrid() {
        const grid = document.getElementById('robots-grid');
        if (!grid) return;
        
        grid.innerHTML = this.data.robots.map(robot => `
            <div class="robot-card">
                <div class="robot-header">
                    <div class="robot-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="robot-info">
                        <h5>Robot ${robot.id}</h5>
                        <span class="robot-status ${robot.status}">${robot.status}</span>
                    </div>
                </div>
                <div class="robot-battery">
                    <div class="battery-level" style="width: ${robot.battery}%"></div>
                    <span>${robot.battery}%</span>
                </div>
                <div class="robot-details">
                    <div>Position: (${robot.x}, ${robot.y})</div>
                    <div>Order: ${robot.current_order || 'None'}</div>
                </div>
            </div>
        `).join('');
    }
    
    getStatusColor(status) {
        switch (status) {
            case 'pending': return 'warning';
            case 'processing': return 'primary';
            case 'completed': return 'success';
            case 'cancelled': return 'danger';
            default: return 'secondary';
        }
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show selected section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Update navigation dropdown
        document.querySelectorAll('.navigation-dropdown .dropdown-item').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[href="#${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        this.currentSection = sectionName;
        

        
        // Initialize 2D warehouse when warehouse-2d section is shown
        if (sectionName === 'warehouse-2d') {
            setTimeout(() => {
                if (typeof initWarehouse2D === 'function') {
                    initWarehouse2D();
                }
            }, 100);
        }
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-message">${message}</div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    startRealTimeUpdates() {
        // Update charts every 5 seconds
        setInterval(() => {
            this.updateOrderChart();
            this.updateRobotChart();
        }, 5000);
        
        // Update dashboard every 10 seconds
        setInterval(() => {
            this.updateDashboard();
        }, 10000);
    }
}

// Global functions for HTML onclick handlers
function showSection(sectionName) {
    if (window.warehouseApp) {
        window.warehouseApp.showSection(sectionName);
    }
}

function startSimulation() {
    if (window.warehouseApp) {
        window.warehouseApp.simulationRunning = true;
        window.warehouseApp.showNotification('Simulation started successfully', 'success');
    }
}

function optimizeWarehouse() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Optimization completed', 'success');
    }
}

function createOrder() {
    const modal = new bootstrap.Modal(document.getElementById('orderModal'));
    modal.show();
    
    // Populate product options in the first order item
    setTimeout(() => {
        const firstProductSelect = document.querySelector('#orderItems .order-item:first-child select[name="product"]');
        if (firstProductSelect && window.warehouseApp && window.warehouseApp.data.inventory) {
            const products = window.warehouseApp.data.inventory.map(item => item.name);
            const productOptions = products.map(product => `<option value="${product}">${product}</option>`).join('');
            firstProductSelect.innerHTML = '<option value="">Select Product</option>' + productOptions;
        }
    }, 100);
}

function submitOrder() {
    const customerName = document.getElementById('customerName').value;
    const priority = document.getElementById('orderPriority').value;
    
    if (!customerName) {
        window.warehouseApp.showNotification('Please enter a customer name', 'error');
        return;
    }
    
    const items = [];
    document.querySelectorAll('.order-item').forEach(item => {
        const product = item.querySelector('select[name="product"]').value;
        const quantity = parseInt(item.querySelector('input[name="quantity"]').value);
        if (product && quantity) {
            items.push({ product, quantity });
        }
    });
    
    if (items.length === 0) {
        window.warehouseApp.showNotification('Please add at least one item', 'error');
        return;
    }
    
    const newOrder = {
        id: window.warehouseApp.data.orders.length + 1,
        customer_name: customerName,
        priority: priority,
        items: items,
        status: 'pending',
        total_value: items.reduce((sum, item) => {
            const inventoryItem = window.warehouseApp.data.inventory.find(i => i.name === item.product);
            return sum + (inventoryItem ? inventoryItem.price * item.quantity : 0);
        }, 0)
    };
    
    window.warehouseApp.data.orders.push(newOrder);
    window.warehouseApp.updateDashboard();
    window.warehouseApp.updateOrdersList();
    
    window.warehouseApp.showNotification('Order created successfully', 'success');
    bootstrap.Modal.getInstance(document.getElementById('orderModal')).hide();
    
    // Reset form
    document.getElementById('orderForm').reset();
    document.getElementById('orderItems').innerHTML = `
        <div class="order-item">
            <div class="row">
                <div class="col-md-6">
                    <select class="form-select" name="product">
                        <option value="">Select Product</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <input type="number" class="form-control" name="quantity" placeholder="Qty" min="1">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger btn-sm" onclick="removeOrderItem(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function addOrderItem() {
    const container = document.getElementById('orderItems');
    const itemDiv = document.createElement('div');
    itemDiv.className = 'order-item';
    
    // Get available products from inventory
    const products = window.warehouseApp.data.inventory.map(item => item.name);
    const productOptions = products.map(product => `<option value="${product}">${product}</option>`).join('');
    
    itemDiv.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <select class="form-select" name="product">
                    <option value="">Select Product</option>
                    ${productOptions}
                </select>
            </div>
            <div class="col-md-4">
                <input type="number" class="form-control" name="quantity" placeholder="Qty" min="1">
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-danger btn-sm" onclick="removeOrderItem(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    container.appendChild(itemDiv);
}

function removeOrderItem(button) {
    button.closest('.order-item').remove();
}

// Additional functions for HTML buttons
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Theme toggled', 'info');
    }
}

function exportData() {
    const data = {
        orders: window.warehouseApp.data.orders,
        inventory: window.warehouseApp.data.inventory,
        robots: window.warehouseApp.data.robots,
        analytics: window.warehouseApp.data.analytics,
        timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `warehouse-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Data exported successfully', 'success');
    }
}

function showHelp() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Help documentation coming soon!', 'info');
    }
}

function addRobot() {
    const robotId = window.warehouseApp.data.robots.length + 1;
    const newRobot = {
        id: robotId,
        x: Math.floor(Math.random() * 50),
        y: Math.floor(Math.random() * 50),
        status: 'idle',
        battery: 100,
        current_order: null,
        route: []
    };
    
    window.warehouseApp.data.robots.push(newRobot);
    window.warehouseApp.updateRobotsGrid();
    window.warehouseApp.showNotification(`Robot ${robotId} added successfully`, 'success');
}

function maintenanceMode() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Maintenance mode activated', 'warning');
    }
}

function generateReport() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Report generation started', 'info');
        setTimeout(() => {
            window.warehouseApp.showNotification('Report generated successfully', 'success');
        }, 2000);
    }
}

function exportAnalytics() {
    const analyticsData = window.warehouseApp.data.analytics;
    const blob = new Blob([JSON.stringify(analyticsData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Analytics exported successfully', 'success');
    }
}

function generatePredictions() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('AI predictions generated', 'success');
    }
}

function trainModels() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('AI models training started', 'info');
        setTimeout(() => {
            window.warehouseApp.showNotification('AI models trained successfully', 'success');
        }, 3000);
    }
}

function runOptimization() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Warehouse optimization completed', 'success');
    }
}

function showOptimizationHistory() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Optimization history loaded', 'info');
    }
}

function batchProcess() {
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Batch processing started', 'info');
        setTimeout(() => {
            window.warehouseApp.showNotification('Batch processing completed', 'success');
        }, 2000);
    }
}

function restockItem(itemId) {
    if (window.warehouseApp) {
        const item = window.warehouseApp.data.inventory.find(i => i.id === itemId);
        if (item) {
            item.quantity += 10;
            window.warehouseApp.updateInventoryGrid();
            window.warehouseApp.showNotification(`${item.name} restocked (+10)`, 'success');
        }
    }
}

function viewItemDetails(itemId) {
    if (window.warehouseApp) {
        const item = window.warehouseApp.data.inventory.find(i => i.id === itemId);
        if (item) {
            window.warehouseApp.showNotification(`Viewing details for ${item.name}`, 'info');
        }
    }
}

function viewOrderDetails(orderId) {
    if (window.warehouseApp) {
        const order = window.warehouseApp.data.orders.find(o => o.id === orderId);
        if (order) {
            window.warehouseApp.showNotification(`Viewing order ${orderId} details`, 'info');
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.warehouseApp = new WarehouseApp();
}); 