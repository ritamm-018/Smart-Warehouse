// Layout Editor for Smart Warehouse Simulator

class LayoutEditor {
    constructor() {
        this.currentTool = 'shelf';
        this.currentShelfCategory = 'mobile-phones';
        this.gridSize = 30;
        this.cellSize = 20;
        this.grid = [];
        this.isDrawing = false;
        this.layoutData = {
            shelves: [],
            packingStations: [],
            entryPoints: [],
            exitPoints: [],
            chargingStations: [],
            walkways: []
        };
        
        this.shelfCategories = {
            'mobile-phones': '📱 Mobile Phones',
            'laptops-tablets': '💻 Laptops & Tablets',
            'headphones-accessories': '🎧 Headphones & Accessories',
            'mens-clothing': '👔 Men\'s Clothing',
            'womens-clothing': '👗 Women\'s Clothing',
            'footwear': '👟 Footwear',
            'kitchen-appliances': '🍳 Kitchen Appliances',
            'packaged-food': '🍪 Packaged Food & Snacks',
            'beverages': '☕ Beverages',
            'medicines': '💊 Medicines & First Aid',
            'books': '📚 Books',
            'stationery': '✏️ Stationery & Office Supplies',
            'toys-games': '🎮 Toys & Games',
            'fitness-equipment': '🏋️ Fitness Equipment',
            'pet-supplies': '🐕 Pet Food & Supplies'
        };
        
        // Product catalog for each category
        this.productCatalog = {
            'mobile-phones': [
                'Apple iPhone 15 Pro', 'Samsung Galaxy S24 Ultra', 'OnePlus 12', 
                'Xiaomi Redmi Note 13', 'Motorola Edge 50', 'Google Pixel 8', 
                'Realme Narzo 70', 'Infinix Zero 5G'
            ],
            'laptops-tablets': [
                'MacBook Air M3', 'Dell XPS 15', 'HP Pavilion x360', 
                'Lenovo ThinkPad X1 Carbon', 'Microsoft Surface Pro 9', 
                'ASUS ROG Zephyrus G14', 'iPad Pro (M4 chip)', 
                'Samsung Galaxy Tab S9', 'Lenovo Tab M10'
            ],
            'headphones-accessories': [
                'Sony WH-1000XM5', 'Apple AirPods Pro 2', 'JBL Tune 760NC', 
                'boAt Rockerz 255 Pro+', 'Logitech G435 Gaming Headset', 
                'Samsung Galaxy Buds2', 'Charging cables (USB-C, Lightning)', 
                'Bluetooth transmitters', 'Phone mounts and stands'
            ],
            'mens-clothing': [
                'Formal shirts and trousers', 'Casual T-shirts and jeans', 
                'Jackets and hoodies', 'Ethnic wear (kurtas, sherwanis)', 
                'Gym wear and shorts', 'Innerwear and socks', 
                'Suits and blazers', 'Swimwear'
            ],
            'womens-clothing': [
                'Kurtis and leggings', 'Sarees and blouses', 
                'Western dresses and tops', 'Jeans and skirts', 
                'Activewear and yoga pants', 'Ethnic suits and lehengas', 
                'Maternity wear', 'Nightwear and lingerie'
            ],
            'footwear': [
                'Sports shoes (Nike, Adidas)', 'Formal shoes', 
                'Casual sneakers', 'Flip-flops and sandals', 
                'High heels and pumps', 'Boots (leather, ankle)', 
                'Running shoes', 'Kids\' shoes'
            ],
            'kitchen-appliances': [
                'Mixer grinders', 'Induction cooktops', 'Air fryers', 
                'Microwave ovens', 'Electric kettles', 
                'Toasters & sandwich makers', 'Coffee machines', 'Hand blenders', 'Dishwashers'
            ],
            'packaged-food': [
                'Chips and namkeen', 'Biscuits and cookies', 'Instant noodles', 
                'Chocolates and candy', 'Dry fruits and trail mixes', 
                'Ready-to-eat meals', 'Breakfast cereals', 'Energy bars'
            ],
            'beverages': [
                'Green tea, black tea, herbal teas', 'Instant coffee and ground coffee', 
                'Energy drinks (Red Bull, Monster)', 'Juices (Tropicana, Real)', 
                'Soft drinks (Coke, Pepsi)', 'Protein shakes', 
                'Coconut water', 'Flavored milk'
            ],
            'medicines': [
                'Pain relievers (Paracetamol, Ibuprofen)', 'Antiseptics (Dettol, Savlon)', 
                'Cough syrup and cold medicine', 'First aid kits', 
                'Bandages and cotton rolls', 'Thermometers and oximeters', 
                'Vitamins and supplements', 'Allergy medication'
            ],
            'books': [
                'Fiction (novels, thrillers)', 'Non-fiction (biographies, self-help)', 
                'Academic textbooks', 'Children\'s books', 'Cookbooks', 
                'Comics and graphic novels', 'Religious/spiritual books', 
                'Language learning books'
            ],
            'stationery': [
                'Notebooks and journals', 'Pens, pencils, and markers', 
                'Files and folders', 'Sticky notes and index tabs', 
                'Staplers and punches', 'Desk organizers', 
                'Calculators', 'Printer paper'
            ],
            'toys-games': [
                'Board games (Monopoly, Ludo)', 'Action figures', 'Puzzle sets', 
                'Soft toys', 'Remote control cars', 'LEGO sets', 
                'Educational toys', 'Dolls and dollhouses'
            ],
            'fitness-equipment': [
                'Dumbbells and kettlebells', 'Resistance bands', 'Yoga mats', 
                'Treadmills', 'Exercise bikes', 'Jump ropes', 
                'Pull-up bars', 'Foam rollers'
            ],
            'pet-supplies': [
                'Dry and wet dog food', 'Cat food and treats', 'Pet grooming kits', 
                'Pet beds and mats', 'Leashes and collars', 'Litter boxes', 
                'Pet toys', 'Flea & tick treatments'
            ]
        };
        
        this.init();
    }
    
    init() {
        this.generateGrid();
        this.updateStats();
        this.setupEventListeners();
        this.createOrderPopup();
    }
    
    generateGrid() {
        const gridContainer = document.getElementById('layout-grid');
        if (!gridContainer) return;
        
        // Clear existing grid
        gridContainer.innerHTML = '';
        
        // Create grid wrapper
        const gridWrapper = document.createElement('div');
        gridWrapper.className = 'grid-wrapper';
        gridWrapper.style.gridTemplateColumns = `repeat(${this.gridSize}, ${this.cellSize}px)`;
        gridWrapper.style.gridTemplateRows = `repeat(${this.gridSize}, ${this.cellSize}px)`;
        
        // Initialize grid array
        this.grid = [];
        
        // Create grid cells
        for (let row = 0; row < this.gridSize; row++) {
            this.grid[row] = [];
            for (let col = 0; col < this.gridSize; col++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                cell.dataset.tooltip = `Row ${row}, Col ${col}`;
                
                // Add event listeners
                cell.addEventListener('mousedown', (e) => this.handleCellClick(e, row, col));
                cell.addEventListener('mouseenter', (e) => this.handleCellHover(e, row, col));
                cell.addEventListener('mouseup', () => this.handleMouseUp());
                
                gridWrapper.appendChild(cell);
                this.grid[row][col] = {
                    type: 'empty',
                    element: cell
                };
            }
        }
        
        gridContainer.appendChild(gridWrapper);
        
        // Add grid size indicator
        const indicator = document.createElement('div');
        indicator.className = 'grid-size-indicator';
        indicator.textContent = `${this.gridSize}x${this.gridSize}`;
        gridContainer.appendChild(indicator);
    }
    
    handleCellClick(e, row, col) {
        e.preventDefault();
        this.isDrawing = true;
        this.placeElement(row, col);
    }
    
    handleCellHover(e, row, col) {
        if (this.isDrawing) {
            this.placeElement(row, col);
        }
    }
    
    handleMouseUp() {
        this.isDrawing = false;
    }
    
    placeElement(row, col) {
        if (row < 0 || row >= this.gridSize || col < 0 || col >= this.gridSize) return;
        
        const cell = this.grid[row][col];
        const cellElement = cell.element;
        
        // Remove existing classes
        cellElement.className = 'grid-cell';
        
        if (this.currentTool === 'eraser') {
            // Clear the cell
            cell.type = 'empty';
            cell.category = null;
            cellElement.removeAttribute('data-tooltip');
        } else {
            // Place the selected element
            cell.type = this.currentTool;
            cellElement.classList.add(this.currentTool);
            
            // Add category class for shelves
            if (this.currentTool === 'shelf') {
                cell.category = this.currentShelfCategory;
                cellElement.classList.add(this.currentShelfCategory);
                cellElement.setAttribute('data-tooltip', `${this.shelfCategories[this.currentShelfCategory]} at (${row}, ${col})`);
            } else {
                cellElement.setAttribute('data-tooltip', `${this.getToolName(this.currentTool)} at (${row}, ${col})`);
            }
            
            // Update layout data
            this.updateLayoutData(row, col, this.currentTool);
            
            // Remove automatic popup trigger - will be triggered by "Apply to 3D" button instead
        }
        
        this.updateStats();
    }
    
    updateLayoutData(row, col, type) {
        const position = { row, col };
        
        // Remove from all arrays first
        this.layoutData.shelves = this.layoutData.shelves.filter(p => p.row !== row || p.col !== col);
        this.layoutData.packingStations = this.layoutData.packingStations.filter(p => p.row !== row || p.col !== col);
        this.layoutData.entryPoints = this.layoutData.entryPoints.filter(p => p.row !== row || p.col !== col);
        this.layoutData.exitPoints = this.layoutData.exitPoints.filter(p => p.row !== row || p.col !== col);
        this.layoutData.chargingStations = this.layoutData.chargingStations.filter(p => p.row !== row || p.col !== col);
        
        // Add to appropriate array
        switch (type) {
            case 'shelf':
                const shelfData = { ...position, category: this.currentShelfCategory };
                this.layoutData.shelves.push(shelfData);
                break;
            case 'packing':
                this.layoutData.packingStations.push(position);
                break;
            case 'entry':
                this.layoutData.entryPoints.push(position);
                break;
            case 'exit':
                this.layoutData.exitPoints.push(position);
                break;
            case 'charging':
                this.layoutData.chargingStations.push(position);
                break;
        }
    }
    
    updateStats() {
        document.getElementById('shelf-count').textContent = this.layoutData.shelves.length;
        document.getElementById('packing-count').textContent = this.layoutData.packingStations.length;
        document.getElementById('entry-count').textContent = this.layoutData.entryPoints.length;
        document.getElementById('exit-count').textContent = this.layoutData.exitPoints.length;
        document.getElementById('charging-count').textContent = this.layoutData.chargingStations.length;
        
        // Update shelf categories breakdown
        this.updateShelfCategoriesStats();
    }
    
    updateShelfCategoriesStats() {
        const statsContainer = document.getElementById('shelf-categories-stats');
        if (!statsContainer) return;
        
        // Count shelves by category
        const categoryCounts = {};
        this.layoutData.shelves.forEach(shelf => {
            const category = shelf.category || 'unknown';
            categoryCounts[category] = (categoryCounts[category] || 0) + 1;
        });
        
        // Generate HTML for category stats
        let statsHTML = '';
        Object.keys(this.shelfCategories).forEach(category => {
            const count = categoryCounts[category] || 0;
            if (count > 0) {
                statsHTML += `
                    <div class="category-stat">
                        <span class="category-name">${this.shelfCategories[category]}</span>
                        <span class="category-count">${count}</span>
                    </div>
                `;
            }
        });
        
        statsContainer.innerHTML = statsHTML;
    }
    
    getToolName(tool) {
        const toolNames = {
            'shelf': 'Shelf',
            'packing': 'Packing Station',
            'entry': 'Entry Point',
            'exit': 'Exit Point',
            'charging': 'Charging Station',
            'eraser': 'Eraser'
        };
        return toolNames[tool] || tool;
    }
    
    setupEventListeners() {
        // Global mouse up listener
        document.addEventListener('mouseup', () => {
            this.isDrawing = false;
        });
    }
    
    selectTool(tool) {
        this.currentTool = tool;
        
        // Update tool button states
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-tool="${tool}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }
    
    changeShelfCategory() {
        const categorySelect = document.getElementById('shelf-category');
        this.currentShelfCategory = categorySelect.value;
    }
    
    changeGridSize() {
        const sizeSelect = document.getElementById('grid-size');
        this.gridSize = parseInt(sizeSelect.value);
        this.generateGrid();
        this.updateStats();
    }
    
    updateCellSize() {
        const sizeSlider = document.getElementById('cell-size');
        const sizeValue = document.getElementById('cell-size-value');
        this.cellSize = parseInt(sizeSlider.value);
        sizeValue.textContent = `${this.cellSize}px`;
        
        // Update grid cell sizes
        const gridWrapper = document.querySelector('.grid-wrapper');
        if (gridWrapper) {
            gridWrapper.style.gridTemplateColumns = `repeat(${this.gridSize}, ${this.cellSize}px)`;
            gridWrapper.style.gridTemplateRows = `repeat(${this.gridSize}, ${this.cellSize}px)`;
        }
        
        // Update individual cell sizes
        document.querySelectorAll('.grid-cell').forEach(cell => {
            cell.style.width = `${this.cellSize}px`;
            cell.style.height = `${this.cellSize}px`;
        });
    }
    
    generateRandomLayout() {
        // Clear existing layout
        this.clearLayout();
        
        // Generate random layout
        const numShelves = Math.floor(Math.random() * 20) + 10;
        const numPacking = Math.floor(Math.random() * 3) + 1;
        const numEntry = Math.floor(Math.random() * 2) + 1;
        const numExit = Math.floor(Math.random() * 2) + 1;
        const numCharging = Math.floor(Math.random() * 3) + 1;
        
        // Place shelves randomly with different categories
        const categoryKeys = Object.keys(this.shelfCategories);
        for (let i = 0; i < numShelves; i++) {
            const row = Math.floor(Math.random() * this.gridSize);
            const col = Math.floor(Math.random() * this.gridSize);
            
            // Assign random category
            const randomCategory = categoryKeys[Math.floor(Math.random() * categoryKeys.length)];
            this.currentShelfCategory = randomCategory;
            
            this.placeElement(row, col);
        }
        
        // Place packing stations
        for (let i = 0; i < numPacking; i++) {
            const row = Math.floor(Math.random() * this.gridSize);
            const col = Math.floor(Math.random() * this.gridSize);
            this.placeElement(row, col, 'packing');
        }
        
        // Place entry points (usually on edges)
        for (let i = 0; i < numEntry; i++) {
            const edge = Math.floor(Math.random() * 4);
            let row, col;
            switch (edge) {
                case 0: // top
                    row = 0;
                    col = Math.floor(Math.random() * this.gridSize);
                    break;
                case 1: // right
                    row = Math.floor(Math.random() * this.gridSize);
                    col = this.gridSize - 1;
                    break;
                case 2: // bottom
                    row = this.gridSize - 1;
                    col = Math.floor(Math.random() * this.gridSize);
                    break;
                case 3: // left
                    row = Math.floor(Math.random() * this.gridSize);
                    col = 0;
                    break;
            }
            this.placeElement(row, col, 'entry');
        }
        
        // Place exit points
        for (let i = 0; i < numExit; i++) {
            const row = Math.floor(Math.random() * this.gridSize);
            const col = Math.floor(Math.random() * this.gridSize);
            this.placeElement(row, col, 'exit');
        }
        
        // Place charging stations
        for (let i = 0; i < numCharging; i++) {
            const row = Math.floor(Math.random() * this.gridSize);
            const col = Math.floor(Math.random() * this.gridSize);
            this.placeElement(row, col, 'charging');
        }
        
        this.updateStats();
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('Random layout generated successfully', 'success');
        }
    }
    
    clearLayout() {
        // Clear all cells
        for (let row = 0; row < this.gridSize; row++) {
            for (let col = 0; col < this.gridSize; col++) {
                const cell = this.grid[row][col];
                cell.type = 'empty';
                cell.category = null;
                cell.element.className = 'grid-cell';
                cell.element.removeAttribute('data-tooltip');
            }
        }
        
        // Clear layout data
        this.layoutData = {
            shelves: [],
            packingStations: [],
            entryPoints: [],
            exitPoints: [],
            chargingStations: [],
            walkways: []
        };
        
        this.updateStats();
    }
    
    saveLayout() {
        const layoutData = {
            gridSize: this.gridSize,
            cellSize: this.cellSize,
            layout: this.layoutData,
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(layoutData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `warehouse-layout-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('Layout saved successfully', 'success');
        }
    }
    
    loadLayout() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const layoutData = JSON.parse(e.target.result);
                        this.applyLayoutData(layoutData);
                        if (window.warehouseApp) {
                            window.warehouseApp.showNotification('Layout loaded successfully', 'success');
                        }
                    } catch (error) {
                        if (window.warehouseApp) {
                            window.warehouseApp.showNotification('Error loading layout file', 'error');
                        }
                    }
                };
                reader.readAsText(file);
            }
        };
        input.click();
    }
    
    applyLayoutData(layoutData) {
        // Update grid size if different
        if (layoutData.gridSize && layoutData.gridSize !== this.gridSize) {
            this.gridSize = layoutData.gridSize;
            document.getElementById('grid-size').value = this.gridSize;
            this.generateGrid();
        }
        
        // Clear current layout
        this.clearLayout();
        
        // Apply saved layout
        if (layoutData.layout) {
            this.layoutData = layoutData.layout;
            
            // Apply to grid
            Object.keys(this.layoutData).forEach(type => {
                this.layoutData[type].forEach(pos => {
                    if (pos.row >= 0 && pos.row < this.gridSize && pos.col >= 0 && pos.col < this.gridSize) {
                        const cell = this.grid[pos.row][pos.col];
                        const elementType = type.slice(0, -1); // Remove 's' from end
                        cell.type = elementType;
                        cell.element.className = `grid-cell ${elementType}`;
                        
                        // Handle shelf categories
                        if (elementType === 'shelf' && pos.category) {
                            cell.category = pos.category;
                            cell.element.classList.add(pos.category);
                            cell.element.setAttribute('data-tooltip', `${this.shelfCategories[pos.category]} at (${pos.row}, ${pos.col})`);
                        } else {
                            cell.element.setAttribute('data-tooltip', `${this.getToolName(elementType)} at (${pos.row}, ${pos.col})`);
                        }
                    }
                });
            });
        }
        
        this.updateStats();
    }
    
    applyTo3D() {
        // Send layout data to 2D visualization
        if (window.warehouse2D) {
            window.warehouse2D.refresh();
        }
        
        // Store layout data for visualization
        localStorage.setItem('customWarehouseLayout', JSON.stringify(this.layoutData));
        
        // Show success notification without navigating
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('Layout applied successfully!', 'success');
        }
        
        // Show order popup after applying layout
        setTimeout(() => {
            this.showOrderPopup();
        }, 1000); // 1 second delay after applying layout
    }

    createOrderPopup() {
        // Create popup container
        const popupContainer = document.createElement('div');
        popupContainer.id = 'order-popup-container';
        popupContainer.className = 'order-popup-container';
        popupContainer.style.display = 'none';
        
        popupContainer.innerHTML = `
            <div class="order-popup">
                <div class="order-popup-header">
                    <h3><i class="fas fa-shopping-cart me-2"></i>Latest Orders</h3>
                    <button class="close-popup-btn" onclick="closeOrderPopup()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="order-popup-content">
                    <div class="order-list" id="order-list">
                        <!-- Orders will be populated here -->
                    </div>
                    <div class="order-categories" id="order-categories">
                        <!-- Category breakdown will be shown here -->
                    </div>
                    <div class="simulation-actions">
                        <button class="btn btn-primary" onclick="goToSimulation()">
                            <i class="fas fa-play me-2"></i>Go to Simulation Page
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(popupContainer);
    }
    
    showOrderPopup() {
        const popup = document.getElementById('order-popup-container');
        if (popup) {
            popup.style.display = 'flex';
            popup.style.opacity = '0';
            
            // Fade in effect
            setTimeout(() => {
                popup.style.opacity = '1';
            }, 100);
            
            this.generateRandomOrders();
        }
    }
    
    generateRandomOrders() {
        const numOrders = Math.floor(Math.random() * 5) + 8; // 8-12 orders
        const orders = [];
        const categoryCounts = {};
        
        // Get only the categories that are actually placed in the grid
        const placedCategories = [...new Set(this.layoutData.shelves.map(shelf => shelf.category))];
        
        // If no shelves are placed, show a message
        if (placedCategories.length === 0) {
            this.displayNoOrdersMessage();
            return;
        }
        
        // Initialize category counts only for placed categories
        placedCategories.forEach(category => {
            categoryCounts[category] = 0;
        });
        
        // Generate random orders only from placed categories
        for (let i = 0; i < numOrders; i++) {
            const category = placedCategories[Math.floor(Math.random() * placedCategories.length)];
            const products = this.productCatalog[category];
            const product = products[Math.floor(Math.random() * products.length)];
            
            orders.push({
                id: i + 1,
                product: product,
                category: category
            });
            
            categoryCounts[category]++;
        }
        
        this.currentOrders = orders;
        this.displayOrders(orders, categoryCounts, numOrders);
    }
    
    displayNoOrdersMessage() {
        const orderList = document.getElementById('order-list');
        const orderCategories = document.getElementById('order-categories');
        
        // Display no orders message
        orderList.innerHTML = `
            <div class="no-orders-message">
                <i class="fas fa-info-circle"></i>
                <p>No orders generated. Please place some shelves in the layout first.</p>
            </div>
        `;
        
        // Clear category breakdown
        orderCategories.innerHTML = '';
    }
    
    getCurrentOrders() {
        return this.currentOrders || [];
    }
    
    displayOrders(orders, categoryCounts, totalOrders) {
        const orderList = document.getElementById('order-list');
        const orderCategories = document.getElementById('order-categories');
        
        // Display order list
        let orderListHTML = '<div class="orders-header"><h4>Order List:</h4></div>';
        orderListHTML += '<div class="orders-grid">';
        
        orders.forEach(order => {
            orderListHTML += `
                <div class="order-item">
                    <span class="order-number">${order.id}.</span>
                    <span class="order-product">${order.product}</span>
                </div>
            `;
        });
        
        orderListHTML += '</div>';
        orderList.innerHTML = orderListHTML;
        
        // Display category breakdown
        let categoryHTML = '<div class="categories-header"><h4>Orders by Category:</h4></div>';
        categoryHTML += '<div class="categories-grid">';
        
        Object.keys(categoryCounts).forEach(category => {
            const count = categoryCounts[category];
            if (count > 0) {
                const categoryName = this.shelfCategories[category];
                const percentage = ((count / totalOrders) * 100).toFixed(1);
                
                categoryHTML += `
                    <div class="category-item">
                        <div class="category-info">
                            <span class="category-name">${categoryName}</span>
                            <span class="category-count">${count} orders (${percentage}%)</span>
                        </div>
                        <div class="category-bar">
                            <div class="category-bar-fill" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                `;
            }
        });
        
        categoryHTML += '</div>';
        orderCategories.innerHTML = categoryHTML;
    }
}

// Global functions for HTML onclick handlers
function selectTool(tool) {
    if (window.layoutEditor) {
        window.layoutEditor.selectTool(tool);
    }
}

function changeGridSize() {
    if (window.layoutEditor) {
        window.layoutEditor.changeGridSize();
    }
}

function updateCellSize() {
    if (window.layoutEditor) {
        window.layoutEditor.updateCellSize();
    }
}

function generateRandomLayout() {
    if (window.layoutEditor) {
        window.layoutEditor.generateRandomLayout();
    }
}

function clearLayout() {
    if (window.layoutEditor) {
        window.layoutEditor.clearLayout();
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('Layout cleared', 'info');
        }
    }
}

function saveLayout() {
    if (window.layoutEditor) {
        window.layoutEditor.saveLayout();
    }
}

function loadLayout() {
    if (window.layoutEditor) {
        window.layoutEditor.loadLayout();
    }
}

function changeShelfCategory() {
    if (window.layoutEditor) {
        window.layoutEditor.changeShelfCategory();
    }
}

function applyLayout() {
    if (window.layoutEditor) {
        window.layoutEditor.applyTo3D();
    }
}

function showOrderPopup() {
    if (window.layoutEditor) {
        window.layoutEditor.showOrderPopup();
    }
}

function closeOrderPopup() {
    const popup = document.getElementById('order-popup-container');
    if (popup) {
        popup.style.opacity = '0';
        setTimeout(() => {
            popup.style.display = 'none';
        }, 300);
    }
}

function goToSimulation() {
    // Store current orders in localStorage for simulation
    if (window.layoutEditor) {
        const orders = window.layoutEditor.getCurrentOrders();
        const layout = window.layoutEditor.layoutData;
        localStorage.setItem('simulationOrders', JSON.stringify(orders));
        localStorage.setItem('simulationLayout', JSON.stringify(layout));
    }
    
    // Navigate to simulation page
    if (window.warehouseApp) {
        window.warehouseApp.showSection('simulation');
    }
    
    // Close popup
    closeOrderPopup();
}

// Initialize layout editor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize after a short delay to ensure other components are loaded
    setTimeout(() => {
        window.layoutEditor = new LayoutEditor();
    }, 100);
}); 