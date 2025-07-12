// 2D Warehouse Visualization using HTML5 Canvas

class Warehouse2D {
    constructor() {
        this.canvas = document.getElementById('warehouse-2d-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 30;
        this.cellSize = 30;
        this.zoom = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        this.animationId = null;
        this.showRobots = true;
        this.showPaths = true;
        this.showLabels = true;
        this.layoutData = null;
        
        this.init();
    }
    
    init() {
        if (!this.canvas) return;
        
        this.setupCanvas();
        this.setupEventListeners();
        this.loadLayoutData();
        this.render();
        this.startAnimation();
    }
    
    setupCanvas() {
        this.canvas.width = 900;
        this.canvas.height = 900;
        this.ctx.imageSmoothingEnabled = true;
        this.ctx.imageSmoothingQuality = 'high';
    }
    
    setupEventListeners() {
        // Mouse events for panning
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.canvas.addEventListener('touchend', () => this.handleTouchEnd());
    }
    
    loadLayoutData() {
        // Try to load custom layout data
        const customLayout = localStorage.getItem('customWarehouseLayout');
        if (customLayout) {
            try {
                this.layoutData = JSON.parse(customLayout);
            } catch (error) {
                console.error('Error loading custom layout:', error);
            }
        }
        
        // If no custom layout, use default
        if (!this.layoutData) {
            this.layoutData = this.generateDefaultLayout();
        }
    }
    
    generateDefaultLayout() {
        const categories = ['mobile-phones', 'laptops-tablets', 'headphones-accessories', 'mens-clothing', 'womens-clothing', 'footwear', 'kitchen-appliances', 'packaged-food', 'beverages', 'medicines', 'books', 'stationery', 'toys-games', 'fitness-equipment', 'pet-supplies'];
        
        return {
            shelves: [
                { row: 5, col: 5, category: 'mobile-phones' }, 
                { row: 5, col: 6, category: 'laptops-tablets' }, 
                { row: 5, col: 7, category: 'headphones-accessories' },
                { row: 10, col: 5, category: 'mens-clothing' }, 
                { row: 10, col: 6, category: 'womens-clothing' }, 
                { row: 10, col: 7, category: 'footwear' },
                { row: 15, col: 5, category: 'kitchen-appliances' }, 
                { row: 15, col: 6, category: 'packaged-food' }, 
                { row: 15, col: 7, category: 'beverages' },
                { row: 20, col: 5, category: 'medicines' }, 
                { row: 20, col: 6, category: 'books' }, 
                { row: 20, col: 7, category: 'stationery' }
            ],
            packingStations: [
                { row: 8, col: 15 }, { row: 18, col: 15 }
            ],
            entryPoints: [
                { row: 0, col: 5 }, { row: 0, col: 15 }
            ],
            exitPoints: [
                { row: 29, col: 5 }, { row: 29, col: 15 }
            ],
            chargingStations: [
                { row: 5, col: 25 }, { row: 15, col: 25 }, { row: 25, col: 25 }
            ]
        };
    }
    
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Apply transformations
        this.ctx.save();
        this.ctx.translate(this.offsetX, this.offsetY);
        this.ctx.scale(this.zoom, this.zoom);
        
        // Draw grid
        this.drawGrid();
        
        // Draw layout elements
        this.drawLayout();
        
        // Draw robots
        if (this.showRobots) {
            this.drawRobots();
        }
        
        // Draw paths
        if (this.showPaths) {
            this.drawPaths();
        }
        
        // Draw labels
        if (this.showLabels) {
            this.drawLabels();
        }
        
        this.ctx.restore();
        
        // Update info
        this.updateInfo();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 1;
        
        // Draw vertical lines
        for (let x = 0; x <= this.gridSize; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.cellSize, 0);
            this.ctx.lineTo(x * this.cellSize, this.gridSize * this.cellSize);
            this.ctx.stroke();
        }
        
        // Draw horizontal lines
        for (let y = 0; y <= this.gridSize; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.cellSize);
            this.ctx.lineTo(this.gridSize * this.cellSize, y * this.cellSize);
            this.ctx.stroke();
        }
    }
    
    drawLayout() {
        if (!this.layoutData) return;
        
        // Shelf category colors
        const shelfColors = {
            'mobile-phones': '#3b82f6',
            'laptops-tablets': '#8b5cf6',
            'headphones-accessories': '#06b6d4',
            'mens-clothing': '#059669',
            'womens-clothing': '#ec4899',
            'footwear': '#f59e0b',
            'kitchen-appliances': '#dc2626',
            'packaged-food': '#16a34a',
            'beverages': '#7c2d12',
            'medicines': '#dc2626',
            'books': '#1e40af',
            'stationery': '#059669',
            'toys-games': '#f59e0b',
            'fitness-equipment': '#7c3aed',
            'pet-supplies': '#16a34a'
        };
        
        // Shelf category emojis
        const shelfEmojis = {
            'mobile-phones': '📱',
            'laptops-tablets': '💻',
            'headphones-accessories': '🎧',
            'mens-clothing': '👔',
            'womens-clothing': '👗',
            'footwear': '👟',
            'kitchen-appliances': '🍳',
            'packaged-food': '🍪',
            'beverages': '☕',
            'medicines': '💊',
            'books': '📚',
            'stationery': '✏️',
            'toys-games': '🎮',
            'fitness-equipment': '🏋️',
            'pet-supplies': '🐕'
        };
        
        // Draw shelves with categories
        this.layoutData.shelves.forEach(pos => {
            const category = pos.category || 'mobile-phones';
            const color = shelfColors[category] || '#6b7280';
            const emoji = shelfEmojis[category] || '📦';
            this.drawCell(pos.row, pos.col, color, emoji);
        });
        
        // Draw packing stations
        this.layoutData.packingStations.forEach(pos => {
            this.drawCell(pos.row, pos.col, '#059669', '📦');
        });
        
        // Draw entry points
        this.layoutData.entryPoints.forEach(pos => {
            this.drawCell(pos.row, pos.col, '#2563eb', '➡️');
        });
        
        // Draw exit points
        this.layoutData.exitPoints.forEach(pos => {
            this.drawCell(pos.row, pos.col, '#dc2626', '⬅️');
        });
        
        // Draw charging stations
        this.layoutData.chargingStations.forEach(pos => {
            this.drawCell(pos.row, pos.col, '#d97706', '⚡');
        });
    }
    
    drawCell(row, col, color, emoji) {
        const x = col * this.cellSize;
        const y = row * this.cellSize;
        
        // Draw background
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x + 1, y + 1, this.cellSize - 2, this.cellSize - 2);
        
        // Draw emoji
        if (emoji) {
            this.ctx.font = `${this.cellSize * 0.6}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(emoji, x + this.cellSize / 2, y + this.cellSize / 2);
        }
    }
    
    drawRobots() {
        const robots = [
            { id: 1, x: 5, y: 5, status: 'idle' },
            { id: 2, x: 15, y: 5, status: 'busy' },
            { id: 3, x: 25, y: 5, status: 'charging' },
            { id: 4, x: 35, y: 5, status: 'idle' }
        ];
        
        robots.forEach(robot => {
            const x = robot.x * this.cellSize;
            const y = robot.y * this.cellSize;
            
            // Draw robot circle
            this.ctx.fillStyle = '#7c3aed';
            this.ctx.beginPath();
            this.ctx.arc(x + this.cellSize / 2, y + this.cellSize / 2, this.cellSize / 3, 0, 2 * Math.PI);
            this.ctx.fill();
            
            // Draw robot ID
            this.ctx.fillStyle = 'white';
            this.ctx.font = `${this.cellSize * 0.4}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(`R${robot.id}`, x + this.cellSize / 2, y + this.cellSize / 2);
            
            // Draw status indicator
            const statusColors = {
                'idle': '#10b981',
                'busy': '#f59e0b',
                'charging': '#ef4444'
            };
            
            this.ctx.fillStyle = statusColors[robot.status] || '#6b7280';
            this.ctx.beginPath();
            this.ctx.arc(x + this.cellSize * 0.8, y + this.cellSize * 0.2, this.cellSize / 8, 0, 2 * Math.PI);
            this.ctx.fill();
        });
    }
    
    drawPaths() {
        // Draw sample robot paths
        const paths = [
            { robotId: 1, path: [[5, 5], [10, 10], [15, 15], [20, 20]] },
            { robotId: 2, path: [[15, 5], [15, 10], [15, 15], [15, 20]] }
        ];
        
        paths.forEach(pathData => {
            this.ctx.strokeStyle = '#f59e0b';
            this.ctx.lineWidth = 3;
            this.ctx.lineCap = 'round';
            this.ctx.lineJoin = 'round';
            
            this.ctx.beginPath();
            pathData.path.forEach((point, index) => {
                const x = point[1] * this.cellSize + this.cellSize / 2;
                const y = point[0] * this.cellSize + this.cellSize / 2;
                
                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            });
            this.ctx.stroke();
            
            // Draw path points
            pathData.path.forEach(point => {
                const x = point[1] * this.cellSize + this.cellSize / 2;
                const y = point[0] * this.cellSize + this.cellSize / 2;
                
                this.ctx.fillStyle = '#f59e0b';
                this.ctx.beginPath();
                this.ctx.arc(x, y, 3, 0, 2 * Math.PI);
                this.ctx.fill();
            });
        });
    }
    
    drawLabels() {
        // Draw grid coordinates
        this.ctx.fillStyle = '#6b7280';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        for (let i = 0; i < this.gridSize; i += 5) {
            // Row labels
            this.ctx.fillText(i.toString(), 15, i * this.cellSize + this.cellSize / 2);
            // Column labels
            this.ctx.fillText(i.toString(), i * this.cellSize + this.cellSize / 2, 15);
        }
    }
    
    updateInfo() {
        const gridSizeEl = document.getElementById('2d-grid-size');
        const elementCountEl = document.getElementById('2d-element-count');
        
        if (gridSizeEl) {
            gridSizeEl.textContent = `${this.gridSize}x${this.gridSize} Grid`;
        }
        
        if (elementCountEl) {
            const totalElements = (this.layoutData?.shelves?.length || 0) +
                                (this.layoutData?.packingStations?.length || 0) +
                                (this.layoutData?.entryPoints?.length || 0) +
                                (this.layoutData?.exitPoints?.length || 0) +
                                (this.layoutData?.chargingStations?.length || 0);
            elementCountEl.textContent = `${totalElements} Elements`;
        }
    }
    
    startAnimation() {
        const animate = () => {
            this.render();
            this.animationId = requestAnimationFrame(animate);
        };
        animate();
    }
    
    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    // Mouse event handlers
    handleMouseDown(e) {
        this.isDragging = true;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
        this.canvas.style.cursor = 'grabbing';
    }
    
    handleMouseMove(e) {
        if (this.isDragging) {
            const deltaX = e.clientX - this.lastMouseX;
            const deltaY = e.clientY - this.lastMouseY;
            
            this.offsetX += deltaX;
            this.offsetY += deltaY;
            
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
        }
    }
    
    handleMouseUp() {
        this.isDragging = false;
        this.canvas.style.cursor = 'crosshair';
    }
    
    handleWheel(e) {
        e.preventDefault();
        
        const zoomFactor = 0.1;
        const newZoom = this.zoom + (e.deltaY > 0 ? -zoomFactor : zoomFactor);
        
        if (newZoom >= 0.5 && newZoom <= 3) {
            this.zoom = newZoom;
            this.updateZoomDisplay();
        }
    }
    
    // Touch event handlers
    handleTouchStart(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            this.isDragging = true;
            this.lastMouseX = e.touches[0].clientX;
            this.lastMouseY = e.touches[0].clientY;
        }
    }
    
    handleTouchMove(e) {
        e.preventDefault();
        if (this.isDragging && e.touches.length === 1) {
            const deltaX = e.touches[0].clientX - this.lastMouseX;
            const deltaY = e.touches[0].clientY - this.lastMouseY;
            
            this.offsetX += deltaX;
            this.offsetY += deltaY;
            
            this.lastMouseX = e.touches[0].clientX;
            this.lastMouseY = e.touches[0].clientY;
        }
    }
    
    handleTouchEnd() {
        this.isDragging = false;
    }
    
    updateZoomDisplay() {
        const zoomValue = document.getElementById('zoom-value');
        if (zoomValue) {
            zoomValue.textContent = `${Math.round(this.zoom * 100)}%`;
        }
    }
    
    // Public methods for external control
    refresh() {
        this.loadLayoutData();
        this.render();
    }
    
    exportImage() {
        const link = document.createElement('a');
        link.download = `warehouse-2d-${new Date().toISOString().split('T')[0]}.png`;
        link.href = this.canvas.toDataURL();
        link.click();
    }
    
    toggleAnimation() {
        if (this.animationId) {
            this.stopAnimation();
        } else {
            this.startAnimation();
        }
    }
    
    updateZoom(zoomLevel) {
        this.zoom = zoomLevel;
        this.updateZoomDisplay();
    }
    
    toggleRobots(show) {
        this.showRobots = show;
    }
    
    togglePaths(show) {
        this.showPaths = show;
    }
    
    toggleLabels(show) {
        this.showLabels = show;
    }
}

// Global functions for HTML onclick handlers
let warehouse2D = null;

function initWarehouse2D() {
    if (!warehouse2D) {
        warehouse2D = new Warehouse2D();
    }
}

function refresh2DView() {
    if (warehouse2D) {
        warehouse2D.refresh();
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('2D view refreshed', 'success');
        }
    }
}

function export2DImage() {
    if (warehouse2D) {
        warehouse2D.exportImage();
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('2D image exported', 'success');
        }
    }
}

function toggle2DAnimation() {
    if (warehouse2D) {
        warehouse2D.toggleAnimation();
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('2D animation toggled', 'info');
        }
    }
}

function update2DZoom() {
    const zoomSlider = document.getElementById('2d-zoom');
    if (warehouse2D && zoomSlider) {
        warehouse2D.updateZoom(parseFloat(zoomSlider.value));
    }
}

function toggle2DRobots() {
    const checkbox = document.getElementById('show-robots-2d');
    if (warehouse2D && checkbox) {
        warehouse2D.toggleRobots(checkbox.checked);
    }
}

function toggle2DPaths() {
    const checkbox = document.getElementById('show-paths-2d');
    if (warehouse2D && checkbox) {
        warehouse2D.togglePaths(checkbox.checked);
    }
}

function toggle2DLabels() {
    const checkbox = document.getElementById('show-labels-2d');
    if (warehouse2D && checkbox) {
        warehouse2D.toggleLabels(checkbox.checked);
    }
}

// Initialize 2D warehouse when section is shown
document.addEventListener('DOMContentLoaded', () => {
    // Initialize after a short delay to ensure other components are loaded
    setTimeout(() => {
        if (document.getElementById('warehouse-2d-canvas')) {
            initWarehouse2D();
        }
    }, 100);
}); 