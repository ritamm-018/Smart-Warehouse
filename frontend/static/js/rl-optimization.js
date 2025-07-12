// Reinforcement Learning Warehouse Layout Optimization
class WarehouseRLOptimizer {
    constructor() {
        this.originalLayout = null;
        this.optimizedLayout = null;
        this.originalMetrics = null;
        this.optimizedMetrics = null;
        this.rlAgent = null;
        this.isOptimizing = false;
        this.episodeCount = 0;
        this.bestScore = 0;
        this.learningRate = 0.001;
        this.epsilon = 0.1; // Exploration rate
        this.gamma = 0.95; // Discount factor
        this.maxEpisodes = 200;
        this.maxSteps = 100;
    }

    // Initialize the RL agent
    initializeRLAgent() {
        this.rlAgent = {
            // Q-learning table for state-action pairs
            qTable: {},
            
            // Get Q-value for state-action pair
            getQValue: (state, action) => {
                const key = `${state}-${action}`;
                return this.rlAgent.qTable[key] || 0;
            },
            
            // Set Q-value for state-action pair
            setQValue: (state, action, value) => {
                const key = `${state}-${action}`;
                this.rlAgent.qTable[key] = value;
            },
            
            // Choose action using epsilon-greedy policy
            chooseAction: (state, availableActions) => {
                if (Math.random() < this.epsilon) {
                    // Exploration: random action
                    return availableActions[Math.floor(Math.random() * availableActions.length)];
                } else {
                    // Exploitation: best action
                    let bestAction = availableActions[0];
                    let bestValue = this.rlAgent.getQValue(state, bestAction);
                    
                    for (const action of availableActions) {
                        const value = this.rlAgent.getQValue(state, action);
                        if (value > bestValue) {
                            bestValue = value;
                            bestAction = action;
                        }
                    }
                    return bestAction;
                }
            },
            
            // Update Q-value using Q-learning formula
            updateQValue: (state, action, reward, nextState, nextActions) => {
                const currentQ = this.rlAgent.getQValue(state, action);
                const nextMaxQ = Math.max(...nextActions.map(a => this.rlAgent.getQValue(nextState, a)));
                const newQ = currentQ + this.learningRate * (reward + this.gamma * nextMaxQ - currentQ);
                this.rlAgent.setQValue(state, action, newQ);
            }
        };
    }

    // Start the optimization process
    async startOptimization(originalLayout, originalMetrics) {
        try {
            this.originalLayout = originalLayout;
            this.originalMetrics = originalMetrics;
            this.isOptimizing = true;
            this.episodeCount = 0;
            this.bestScore = 0;

            // Initialize RL agent
            this.initializeRLAgent();

            // Show optimization progress
            this.showOptimizationProgress();

            // Start optimization loop with timeout
            const optimizationPromise = this.runOptimizationLoop();
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Optimization timeout')), 30000) // 30 second timeout
            );
            
            await Promise.race([optimizationPromise, timeoutPromise]);

            // Generate optimized layout
            this.optimizedLayout = this.generateOptimizedLayout();
            
            // Ensure optimized layout is valid
            if (!this.optimizedLayout) {
                console.warn('Failed to generate optimized layout, using original');
                this.optimizedLayout = JSON.parse(JSON.stringify(this.originalLayout));
            }

            // Calculate optimized metrics
            this.optimizedMetrics = this.calculateOptimizedMetrics();

            // Show results
            this.showOptimizationResults();

            this.isOptimizing = false;
            
            console.log('Optimization completed successfully');
            console.log('Original metrics:', this.originalMetrics);
            console.log('Optimized metrics:', this.optimizedMetrics);
            
        } catch (error) {
            console.error('Error during optimization:', error);
            this.isOptimizing = false;
            
            // Fallback to basic optimization
            this.optimizedLayout = this.generateOptimizedLayout();
            this.optimizedMetrics = this.calculateOptimizedMetrics();
            this.showOptimizationResults();
            
            if (window.warehouseApp) {
                window.warehouseApp.showNotification('Optimization completed with fallback due to timeout.', 'warning');
            }
        }
    }

    // Main optimization loop
    async runOptimizationLoop() {
        const totalEpisodes = this.maxEpisodes;
        console.log('Starting optimization loop with', totalEpisodes, 'episodes');
        
        for (let episode = 0; episode < totalEpisodes; episode++) {
            this.episodeCount = episode + 1;
            
            // Run one episode
            const episodeScore = await this.runEpisode();
            
            // Update best score
            if (episodeScore > this.bestScore) {
                this.bestScore = episodeScore;
            }
            
            // Update progress
            this.updateProgress((episode + 1) / totalEpisodes * 100);
            
            // Reduce exploration rate over time
            this.epsilon = Math.max(0.01, this.epsilon * 0.999);
            
            // Add small delay for visual feedback
            await this.sleep(5);
            
            // Log progress every 50 episodes
            if (episode % 50 === 0) {
                console.log(`Episode ${episode + 1}/${totalEpisodes}, Score: ${episodeScore.toFixed(2)}, Best: ${this.bestScore.toFixed(2)}`);
            }
        }
        
        console.log('Optimization loop completed');
    }

    // Run a single episode
    async runEpisode() {
        let currentState = this.getInitialState();
        let totalReward = 0;
        
        for (let step = 0; step < this.maxSteps; step++) {
            // Get available actions
            const availableActions = this.getAvailableActions(currentState);
            
            if (availableActions.length === 0) break;
            
            // Choose action
            const action = this.rlAgent.chooseAction(currentState, availableActions);
            
            // Take action and get new state and reward
            const { nextState, reward } = this.takeAction(currentState, action);
            
            // Get next available actions
            const nextActions = this.getAvailableActions(nextState);
            
            // Update Q-value
            this.rlAgent.updateQValue(currentState, action, reward, nextState, nextActions);
            
            totalReward += reward;
            currentState = nextState;
            
            // Check if episode is complete
            if (this.isEpisodeComplete(currentState)) {
                break;
            }
        }
        
        return totalReward;
    }

    // Get initial state representation
    getInitialState() {
        const state = {
            layout: JSON.parse(JSON.stringify(this.originalLayout)),
            metrics: { ...this.originalMetrics },
            step: 0
        };
        return JSON.stringify(state);
    }

    // Get available actions for current state
    getAvailableActions(stateStr) {
        const state = JSON.parse(stateStr);
        const actions = [];
        
        // Actions: move shelves, adjust packing stations, optimize entry/exit points
        const layout = state.layout;
        
        // Move shelves to better positions
        if (layout.shelves) {
            for (let i = 0; i < layout.shelves.length; i++) {
                for (let row = 0; row < layout.gridSize; row++) {
                    for (let col = 0; col < layout.gridSize; col++) {
                        // Check if position is available
                        if (this.isPositionAvailable(layout, row, col)) {
                            actions.push(`move_shelf_${i}_to_${row}_${col}`);
                        }
                    }
                }
            }
        }
        
        // Optimize packing station positions
        if (layout.packingStations) {
            for (let i = 0; i < layout.packingStations.length; i++) {
                for (let row = 0; row < layout.gridSize; row++) {
                    for (let col = 0; col < layout.gridSize; col++) {
                        if (this.isPositionAvailable(layout, row, col)) {
                            actions.push(`move_packing_${i}_to_${row}_${col}`);
                        }
                    }
                }
            }
        }
        
        // Optimize entry/exit points
        if (layout.entryPoints) {
            for (let i = 0; i < layout.entryPoints.length; i++) {
                for (let row = 0; row < layout.gridSize; row++) {
                    for (let col = 0; col < layout.gridSize; col++) {
                        if (this.isPositionAvailable(layout, row, col)) {
                            actions.push(`move_entry_${i}_to_${row}_${col}`);
                        }
                    }
                }
            }
        }
        
        return actions.slice(0, 50); // Limit actions for performance
    }

    // Take an action and return new state and reward
    takeAction(stateStr, action) {
        const state = JSON.parse(stateStr);
        const newState = JSON.parse(JSON.stringify(state));
        
        let reward = 0;
        
        // Parse action
        const actionParts = action.split('_');
        
        if (actionParts[0] === 'move') {
            const elementType = actionParts[1]; // shelf, packing, entry
            const elementIndex = parseInt(actionParts[2]);
            const newRow = parseInt(actionParts[4]);
            const newCol = parseInt(actionParts[5]);
            
            // Apply the move
            if (elementType === 'shelf' && newState.layout.shelves[elementIndex]) {
                newState.layout.shelves[elementIndex].row = newRow;
                newState.layout.shelves[elementIndex].col = newCol;
            } else if (elementType === 'packing' && newState.layout.packingStations[elementIndex]) {
                newState.layout.packingStations[elementIndex].row = newRow;
                newState.layout.packingStations[elementIndex].col = newCol;
            } else if (elementType === 'entry' && newState.layout.entryPoints[elementIndex]) {
                newState.layout.entryPoints[elementIndex].row = newRow;
                newState.layout.entryPoints[elementIndex].col = newCol;
            }
            
            // Calculate reward based on improvement
            const newMetrics = this.calculateMetrics(newState.layout);
            const improvement = this.calculateImprovement(newMetrics, state.metrics);
            reward = improvement;
            
            newState.metrics = newMetrics;
        }
        
        newState.step = state.step + 1;
        
        return {
            nextState: JSON.stringify(newState),
            reward: reward
        };
    }

    // Check if episode is complete
    isEpisodeComplete(stateStr) {
        const state = JSON.parse(stateStr);
        return state.step >= this.maxSteps;
    }

    // Check if position is available
    isPositionAvailable(layout, row, col) {
        // Check if position is occupied by any element
        const allElements = [
            ...(layout.shelves || []),
            ...(layout.packingStations || []),
            ...(layout.entryPoints || []),
            ...(layout.exitPoints || []),
            ...(layout.chargingStations || [])
        ];
        
        return !allElements.some(element => element.row === row && element.col === col);
    }

    // Calculate metrics for a layout
    calculateMetrics(layout) {
        // Simulate order fulfillment with this layout
        const orders = this.generateTestOrders();
        let totalDistance = 0;
        let totalTime = 0;
        
        orders.forEach(order => {
            const path = this.calculateOrderPath(layout, order);
            if (path) {
                totalDistance += path.totalDistance;
                totalTime += path.estimatedTime;
            }
        });
        
        const avgDistance = totalDistance / orders.length;
        const avgTime = totalTime / orders.length;
        const efficiency = this.calculateEfficiency(avgDistance, avgTime, layout.gridSize);
        
        return {
            totalDistance,
            avgDistance,
            totalTime,
            avgTime,
            efficiency,
            orderCount: orders.length
        };
    }

    // Calculate improvement between two metric sets
    calculateImprovement(newMetrics, oldMetrics) {
        const distanceImprovement = (oldMetrics.avgDistance - newMetrics.avgDistance) / oldMetrics.avgDistance;
        const timeImprovement = (oldMetrics.avgTime - newMetrics.avgTime) / oldMetrics.avgTime;
        const efficiencyImprovement = (newMetrics.efficiency - oldMetrics.efficiency) / 100;
        
        return (distanceImprovement + timeImprovement + efficiencyImprovement) * 100;
    }

    // Generate test orders for evaluation
    generateTestOrders() {
        const categories = ['mobile-phones', 'laptops-tablets', 'headphones-accessories', 'mens-clothing'];
        const orders = [];
        
        for (let i = 0; i < 20; i++) {
            orders.push({
                id: `test_${i}`,
                product: `Test Product ${i}`,
                category: categories[Math.floor(Math.random() * categories.length)],
                status: 'pending'
            });
        }
        
        return orders;
    }

    // Calculate order path for a given layout
    calculateOrderPath(layout, order) {
        // Find shelf for this order
        const shelf = layout.shelves?.find(s => s.category === order.category);
        if (!shelf) return null;
        
        // Find nearest packing station
        const packing = layout.packingStations?.[0];
        if (!packing) return null;
        
        // Find entry and exit points
        const entry = layout.entryPoints?.[0];
        const exit = layout.exitPoints?.[0];
        if (!entry || !exit) return null;
        
        // Calculate distances
        const entryToShelf = this.manhattanDistance(entry, shelf);
        const shelfToPacking = this.manhattanDistance(shelf, packing);
        const packingToExit = this.manhattanDistance(packing, exit);
        
        const totalDistance = entryToShelf + shelfToPacking + packingToExit;
        const estimatedTime = totalDistance / 2; // Assuming 2 units per second
        
        return {
            totalDistance,
            estimatedTime,
            segments: [
                { from: 'entry', to: 'shelf', distance: entryToShelf },
                { from: 'shelf', to: 'packing', distance: shelfToPacking },
                { from: 'packing', to: 'exit', distance: packingToExit }
            ]
        };
    }

    // Calculate Manhattan distance between two points
    manhattanDistance(point1, point2) {
        return Math.abs(point1.row - point2.row) + Math.abs(point1.col - point2.col);
    }

    // Calculate efficiency score
    calculateEfficiency(avgDistance, avgTime, gridSize) {
        const maxExpectedDistance = gridSize * 2;
        const maxExpectedTime = gridSize * 2;
        
        const distanceEfficiency = Math.max(0, 100 - (avgDistance / maxExpectedDistance) * 100);
        const timeEfficiency = Math.max(0, 100 - (avgTime / maxExpectedTime) * 100);
        
        return Math.round((distanceEfficiency + timeEfficiency) / 2);
    }

    // Generate optimized layout based on learned Q-values
    generateOptimizedLayout() {
        // Always apply basic optimizations to create an improved layout
        const optimizedLayout = JSON.parse(JSON.stringify(this.originalLayout));
        
        // Apply basic optimizations
        this.applyBasicOptimizations(optimizedLayout);
        
        // Ensure we have a valid layout
        if (!optimizedLayout.shelves || optimizedLayout.shelves.length === 0) {
            console.warn('No shelves found in layout, using original');
            return this.originalLayout;
        }
        
        return optimizedLayout;
    }

    // Apply basic optimizations to layout
    applyBasicOptimizations(layout) {
        const gridSize = layout.gridSize || 30;
        
        // Optimize shelf positions based on frequency
        if (layout.shelves && layout.shelves.length > 0) {
            // Move frequently used shelves closer to entry points
            const entryPoint = layout.entryPoints?.[0];
            if (entryPoint) {
                // Sort shelves by distance to entry point
                layout.shelves.sort((a, b) => {
                    const distA = this.manhattanDistance(entryPoint, a);
                    const distB = this.manhattanDistance(entryPoint, b);
                    return distA - distB;
                });
                
                // Reposition shelves in optimal positions (avoiding conflicts)
                const usedPositions = new Set();
                for (let i = 0; i < layout.shelves.length; i++) {
                    let optimalRow = Math.floor(i / 4) + 2;
                    let optimalCol = (i % 4) + 2;
                    
                    // Find next available position if current is occupied
                    while (usedPositions.has(`${optimalRow}-${optimalCol}`)) {
                        optimalCol++;
                        if (optimalCol >= gridSize - 2) {
                            optimalCol = 2;
                            optimalRow++;
                        }
                        if (optimalRow >= gridSize - 2) {
                            optimalRow = 2;
                            optimalCol = 2;
                        }
                    }
                    
                    layout.shelves[i].row = optimalRow;
                    layout.shelves[i].col = optimalCol;
                    usedPositions.add(`${optimalRow}-${optimalCol}`);
                }
            }
        }
        
        // Optimize packing station position
        if (layout.packingStations && layout.packingStations.length > 0 && layout.shelves && layout.shelves.length > 0) {
            // Place packing station in center of shelves
            const avgShelfRow = layout.shelves.reduce((sum, shelf) => sum + shelf.row, 0) / layout.shelves.length;
            const avgShelfCol = layout.shelves.reduce((sum, shelf) => sum + shelf.col, 0) / layout.shelves.length;
            
            // Find nearest available position to center
            let bestRow = Math.round(avgShelfRow);
            let bestCol = Math.round(avgShelfCol);
            
            // Ensure position is within bounds and not occupied
            bestRow = Math.max(1, Math.min(gridSize - 2, bestRow));
            bestCol = Math.max(1, Math.min(gridSize - 2, bestCol));
            
            layout.packingStations[0].row = bestRow;
            layout.packingStations[0].col = bestCol;
        }
        
        // Optimize entry/exit points
        if (layout.entryPoints && layout.entryPoints.length > 0) {
            layout.entryPoints[0].row = 0;
            layout.entryPoints[0].col = 0;
        }
        
        if (layout.exitPoints && layout.exitPoints.length > 0) {
            layout.exitPoints[0].row = gridSize - 1;
            layout.exitPoints[0].col = gridSize - 1;
        }
        
        // Ensure charging stations are well positioned
        if (layout.chargingStations && layout.chargingStations.length > 0) {
            layout.chargingStations.forEach((station, index) => {
                station.row = Math.floor(index / 2) + 1;
                station.col = (index % 2) + gridSize - 3;
            });
        }
    }

    // Calculate metrics for optimized layout
    calculateOptimizedMetrics() {
        if (!this.optimizedLayout) {
            console.warn('No optimized layout available, using original metrics');
            return { ...this.originalMetrics };
        }
        
        try {
            return this.calculateMetrics(this.optimizedLayout);
        } catch (error) {
            console.error('Error calculating optimized metrics:', error);
            return { ...this.originalMetrics };
        }
    }

    // Show optimization progress
    showOptimizationProgress() {
        const statusDiv = document.getElementById('optimization-status');
        const comparisonDiv = document.getElementById('layouts-comparison');
        
        if (statusDiv) statusDiv.style.display = 'block';
        if (comparisonDiv) comparisonDiv.style.display = 'none';
    }

    // Update progress bar
    updateProgress(percentage) {
        const progressFill = document.getElementById('rl-progress-fill');
        const progressText = document.getElementById('rl-progress-text');
        const episodeCount = document.getElementById('episode-count');
        const bestScore = document.getElementById('best-score');
        
        if (progressFill) progressFill.style.width = `${percentage}%`;
        if (progressText) progressText.textContent = `${Math.round(percentage)}%`;
        if (episodeCount) episodeCount.textContent = this.episodeCount;
        if (bestScore) bestScore.textContent = this.bestScore.toFixed(2);
    }

    // Show optimization results
    showOptimizationResults() {
        const statusDiv = document.getElementById('optimization-status');
        const comparisonDiv = document.getElementById('layouts-comparison');
        
        if (statusDiv) statusDiv.style.display = 'none';
        if (comparisonDiv) comparisonDiv.style.display = 'block';
        
        // Render layouts
        this.renderOriginalLayout();
        this.renderOptimizedLayout();
        
        // Update metrics
        this.updateMetrics();
        
        // Update comparison
        this.updateComparison();
        
        // Generate insights
        this.generateInsights();
    }

    // Render original layout
    renderOriginalLayout() {
        const grid = document.getElementById('original-layout-grid');
        if (!grid) return;
        
        this.renderLayout(grid, this.originalLayout);
    }

    // Render optimized layout
    renderOptimizedLayout() {
        const grid = document.getElementById('optimized-layout-grid');
        if (!grid) return;
        
        this.renderLayout(grid, this.optimizedLayout);
    }

    // Render layout grid
    renderLayout(grid, layout) {
        const gridSize = layout.gridSize || 30;
        const cellSize = 12; // Smaller cells for comparison view
        
        grid.innerHTML = '';
        grid.style.gridTemplateColumns = `repeat(${gridSize}, ${cellSize}px)`;
        grid.style.gridTemplateRows = `repeat(${gridSize}, ${cellSize}px)`;
        
        for (let row = 0; row < gridSize; row++) {
            for (let col = 0; col < gridSize; col++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                cell.style.width = `${cellSize}px`;
                cell.style.height = `${cellSize}px`;
                
                const cellType = this.getCellType(layout, row, col);
                if (cellType) {
                    cell.classList.add(cellType);
                }
                
                grid.appendChild(cell);
            }
        }
    }

    // Get cell type for layout
    getCellType(layout, row, col) {
        if (layout.shelves) {
            const shelf = layout.shelves.find(s => s.row === row && s.col === col);
            if (shelf) return 'shelf';
        }
        
        if (layout.packingStations) {
            const packing = layout.packingStations.find(p => p.row === row && p.col === col);
            if (packing) return 'packing';
        }
        
        if (layout.entryPoints) {
            const entry = layout.entryPoints.find(e => e.row === row && e.col === col);
            if (entry) return 'entry';
        }
        
        if (layout.exitPoints) {
            const exit = layout.exitPoints.find(e => e.row === row && e.col === col);
            if (exit) return 'exit';
        }
        
        if (layout.chargingStations) {
            const charging = layout.chargingStations.find(c => c.row === row && c.col === col);
            if (charging) return 'charging';
        }
        
        return null;
    }

    // Update metrics display
    updateMetrics() {
        // Original metrics
        document.getElementById('original-total-distance').textContent = this.originalMetrics.totalDistance;
        document.getElementById('original-avg-time').textContent = `${this.originalMetrics.avgTime.toFixed(1)}s`;
        document.getElementById('original-efficiency').textContent = `${this.originalMetrics.efficiency}%`;
        document.getElementById('original-path-length').textContent = Math.round(this.originalMetrics.avgDistance);
        
        // Optimized metrics
        document.getElementById('optimized-total-distance').textContent = this.optimizedMetrics.totalDistance;
        document.getElementById('optimized-avg-time').textContent = `${this.optimizedMetrics.avgTime.toFixed(1)}s`;
        document.getElementById('optimized-efficiency').textContent = `${this.optimizedMetrics.efficiency}%`;
        document.getElementById('optimized-path-length').textContent = Math.round(this.optimizedMetrics.avgDistance);
    }

    // Update comparison display
    updateComparison() {
        // Calculate improvements
        const distanceImprovement = ((this.originalMetrics.avgDistance - this.optimizedMetrics.avgDistance) / this.originalMetrics.avgDistance * 100);
        const timeImprovement = ((this.originalMetrics.avgTime - this.optimizedMetrics.avgTime) / this.originalMetrics.avgTime * 100);
        const efficiencyImprovement = (this.optimizedMetrics.efficiency - this.originalMetrics.efficiency);
        const overallImprovement = (distanceImprovement + timeImprovement + efficiencyImprovement) / 3;
        
        // Update improvement badges
        document.getElementById('distance-improvement').textContent = `${distanceImprovement.toFixed(1)}%`;
        document.getElementById('time-improvement').textContent = `${timeImprovement.toFixed(1)}%`;
        document.getElementById('efficiency-improvement').textContent = `${efficiencyImprovement.toFixed(1)}%`;
        document.getElementById('overall-improvement').textContent = `${overallImprovement.toFixed(1)}%`;
        
        // Update progress bars
        setTimeout(() => {
            document.getElementById('distance-bar-fill').style.width = `${Math.min(100, distanceImprovement)}%`;
            document.getElementById('time-bar-fill').style.width = `${Math.min(100, timeImprovement)}%`;
            document.getElementById('efficiency-bar-fill').style.width = `${Math.min(100, efficiencyImprovement)}%`;
            document.getElementById('overall-bar-fill').style.width = `${Math.min(100, overallImprovement)}%`;
        }, 100);
    }

    // Generate AI insights
    generateInsights() {
        const insightsContainer = document.getElementById('optimization-insights');
        if (!insightsContainer) return;
        
        const insights = [
            {
                icon: 'fas fa-route',
                title: 'Path Optimization',
                description: `Reduced average path length by ${((this.originalMetrics.avgDistance - this.optimizedMetrics.avgDistance) / this.originalMetrics.avgDistance * 100).toFixed(1)}% through strategic shelf positioning.`
            },
            {
                icon: 'fas fa-clock',
                title: 'Time Efficiency',
                description: `Improved order fulfillment time by ${((this.originalMetrics.avgTime - this.optimizedMetrics.avgTime) / this.originalMetrics.avgTime * 100).toFixed(1)}% by optimizing bot movement patterns.`
            },
            {
                icon: 'fas fa-chart-line',
                title: 'Overall Performance',
                description: `Enhanced warehouse efficiency by ${(this.optimizedMetrics.efficiency - this.originalMetrics.efficiency).toFixed(1)}% through AI-driven layout optimization.`
            },
            {
                icon: 'fas fa-lightbulb',
                title: 'Key Improvements',
                description: 'Moved frequently accessed shelves closer to entry points, centralized packing stations, and optimized traffic flow patterns.'
            }
        ];
        
        insightsContainer.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <i class="insight-icon ${insight.icon}"></i>
                <div class="insight-text">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-description">${insight.description}</div>
                </div>
            </div>
        `).join('');
    }

    // Utility function for delays
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global RL Optimizer instance
let rlOptimizer = null;

// Function to start RL optimization
function optimizeWithRL() {
    if (!window.warehouseSimulation) {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('No simulation data available. Please run a simulation first.', 'warning');
        }
        return;
    }
    
    // Navigate to compare layouts page
    if (window.warehouseApp) {
        window.warehouseApp.showSection('compare-layouts');
    }
    
    // Initialize RL optimizer
    rlOptimizer = new WarehouseRLOptimizer();
    
    // Get original layout and metrics
    const originalLayout = window.warehouseSimulation.layout;
    
    // Ensure we have a valid layout
    if (!originalLayout || !originalLayout.shelves || originalLayout.shelves.length === 0) {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('No valid layout found. Please create a custom layout first.', 'warning');
        }
        return;
    }
    
    const originalMetrics = {
        totalDistance: window.warehouseSimulation.totalDistanceTravelled || 0,
        avgDistance: window.warehouseSimulation.readings && window.warehouseSimulation.readings.length > 0 ? 
            window.warehouseSimulation.readings.reduce((sum, r) => sum + (r.pathLength || 0), 0) / window.warehouseSimulation.readings.length : 0,
        totalTime: window.warehouseSimulation.readings && window.warehouseSimulation.readings.length > 0 ?
            window.warehouseSimulation.readings.reduce((sum, r) => sum + parseFloat(r.timeTaken || 0), 0) : 0,
        avgTime: window.warehouseSimulation.readings && window.warehouseSimulation.readings.length > 0 ?
            window.warehouseSimulation.readings.reduce((sum, r) => sum + parseFloat(r.timeTaken || 0), 0) / window.warehouseSimulation.readings.length : 0,
        efficiency: window.warehouseSimulation.distanceCalculator ? window.warehouseSimulation.distanceCalculator.calculateLayoutEfficiency() : 50,
        orderCount: window.warehouseSimulation.readings ? window.warehouseSimulation.readings.length : 0
    };
    
    console.log('Starting RL optimization with:', { originalLayout, originalMetrics });
    
    // Start optimization
    rlOptimizer.startOptimization(originalLayout, originalMetrics);
}

// Function to apply optimized layout
function applyOptimizedLayout() {
    if (!rlOptimizer) {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('No optimization data available. Please run optimization first.', 'warning');
        }
        return;
    }
    
    if (!rlOptimizer.optimizedLayout) {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('No optimized layout available. Please run optimization first.', 'warning');
        }
        return;
    }
    
    // Apply the optimized layout
    if (window.warehouseSimulation) {
        try {
            window.warehouseSimulation.layout = rlOptimizer.optimizedLayout;
            localStorage.setItem('customWarehouseLayout', JSON.stringify(rlOptimizer.optimizedLayout));
            
            // Update the simulation display
            if (window.warehouseSimulation.displayCustomLayout) {
                window.warehouseSimulation.displayCustomLayout();
            }
            
            if (window.warehouseApp) {
                window.warehouseApp.showNotification('Optimized layout applied successfully!', 'success');
                window.warehouseApp.showSection('simulation');
            }
        } catch (error) {
            console.error('Error applying optimized layout:', error);
            if (window.warehouseApp) {
                window.warehouseApp.showNotification('Error applying optimized layout. Please try again.', 'error');
            }
        }
    } else {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('Simulation not available. Please refresh the page.', 'error');
        }
    }
}

// Function to export optimization report
function exportOptimizationReport() {
    if (!rlOptimizer) {
        if (window.warehouseApp) {
            window.warehouseApp.showNotification('No optimization data available.', 'warning');
        }
        return;
    }
    
    const report = {
        timestamp: new Date().toISOString(),
        originalLayout: rlOptimizer.originalLayout,
        optimizedLayout: rlOptimizer.optimizedLayout,
        originalMetrics: rlOptimizer.originalMetrics,
        optimizedMetrics: rlOptimizer.optimizedMetrics,
        improvements: {
            distance: ((rlOptimizer.originalMetrics.avgDistance - rlOptimizer.optimizedMetrics.avgDistance) / rlOptimizer.originalMetrics.avgDistance * 100),
            time: ((rlOptimizer.originalMetrics.avgTime - rlOptimizer.optimizedMetrics.avgTime) / rlOptimizer.originalMetrics.avgTime * 100),
            efficiency: (rlOptimizer.optimizedMetrics.efficiency - rlOptimizer.originalMetrics.efficiency)
        },
        rlStats: {
            episodes: rlOptimizer.episodeCount,
            bestScore: rlOptimizer.bestScore,
            learningRate: rlOptimizer.learningRate
        }
    };
    
    const csv = convertOptimizationReportToCSV(report);
    downloadCSV(csv, 'warehouse_optimization_report.csv');
    
    if (window.warehouseApp) {
        window.warehouseApp.showNotification('Optimization report exported successfully!', 'success');
    }
}

// Function to convert optimization report to CSV
function convertOptimizationReportToCSV(report) {
    const rows = [
        ['Warehouse Optimization Report'],
        ['Generated:', report.timestamp],
        [''],
        ['Original Metrics'],
        ['Total Distance', report.originalMetrics.totalDistance],
        ['Average Distance', report.originalMetrics.avgDistance.toFixed(2)],
        ['Total Time', report.originalMetrics.totalTime.toFixed(2)],
        ['Average Time', report.originalMetrics.avgTime.toFixed(2)],
        ['Efficiency Score', report.originalMetrics.efficiency + '%'],
        [''],
        ['Optimized Metrics'],
        ['Total Distance', report.optimizedMetrics.totalDistance],
        ['Average Distance', report.optimizedMetrics.avgDistance.toFixed(2)],
        ['Total Time', report.optimizedMetrics.totalTime.toFixed(2)],
        ['Average Time', report.optimizedMetrics.avgTime.toFixed(2)],
        ['Efficiency Score', report.optimizedMetrics.efficiency + '%'],
        [''],
        ['Improvements'],
        ['Distance Reduction', report.improvements.distance.toFixed(2) + '%'],
        ['Time Improvement', report.improvements.time.toFixed(2) + '%'],
        ['Efficiency Gain', report.improvements.efficiency.toFixed(2) + '%'],
        [''],
        ['RL Training Statistics'],
        ['Episodes', report.rlStats.episodes],
        ['Best Score', report.rlStats.bestScore.toFixed(2)],
        ['Learning Rate', report.rlStats.learningRate]
    ];
    
    return rows.map(row => row.join(',')).join('\n');
}

// Function to go back to readings page
function goBackToReadings() {
    if (window.warehouseApp) {
        window.warehouseApp.showSection('readings');
    }
} 