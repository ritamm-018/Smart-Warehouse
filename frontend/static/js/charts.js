// Charts and Analytics for Smart Warehouse Simulator

class ChartManager {
    constructor() {
        this.charts = {};
        this.chartColors = {
            primary: '#2563eb',
            success: '#059669',
            warning: '#d97706',
            danger: '#dc2626',
            info: '#0891b2',
            secondary: '#6b7280'
        };
    }
    
    initCharts() {
        this.initPerformanceChart();
        this.initEfficiencyChart();
        this.initDemandForecastChart();
        this.initRobotUtilizationChart();
    }
    
    initPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        this.charts.performance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Efficiency', 'Utilization', 'Completion Rate', 'Energy Usage', 'Travel Distance'],
                datasets: [{
                    label: 'Current Performance',
                    data: [85, 78, 92, 88, 82],
                    backgroundColor: this.chartColors.primary,
                    borderColor: this.chartColors.primary,
                    borderWidth: 1
                }, {
                    label: 'Target Performance',
                    data: [95, 85, 98, 90, 90],
                    backgroundColor: this.chartColors.success,
                    borderColor: this.chartColors.success,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Warehouse Performance Metrics'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    initEfficiencyChart() {
        const ctx = document.getElementById('efficiencyChart');
        if (!ctx) return;
        
        this.charts.efficiency = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Picking Speed', 'Route Optimization', 'Battery Management', 'Load Balancing', 'Error Rate', 'Throughput'],
                datasets: [{
                    label: 'Current Efficiency',
                    data: [85, 78, 92, 88, 95, 82],
                    borderColor: this.chartColors.primary,
                    backgroundColor: this.hexToRgba(this.chartColors.primary, 0.2),
                    pointBackgroundColor: this.chartColors.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: this.chartColors.primary
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Efficiency Analysis'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    initDemandForecastChart() {
        const ctx = document.getElementById('demandForecastChart');
        if (!ctx) return;
        
        // Generate sample forecast data
        const dates = this.generateDateLabels(30);
        const forecastData = dates.map(() => Math.floor(Math.random() * 50) + 20);
        
        this.charts.demandForecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Predicted Demand',
                    data: forecastData,
                    borderColor: this.chartColors.primary,
                    backgroundColor: this.hexToRgba(this.chartColors.primary, 0.1),
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: '30-Day Demand Forecast'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Orders per Day'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }
    
    initRobotUtilizationChart() {
        const ctx = document.getElementById('robotUtilizationChart');
        if (!ctx) return;
        
        this.charts.robotUtilization = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Idle', 'Charging', 'Maintenance'],
                datasets: [{
                    data: [65, 20, 10, 5],
                    backgroundColor: [
                        this.chartColors.success,
                        this.chartColors.secondary,
                        this.chartColors.warning,
                        this.chartColors.danger
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Robot Fleet Utilization'
                    }
                }
            }
        });
    }
    
    updatePerformanceChart(data) {
        if (!this.charts.performance) return;
        
        this.charts.performance.data.datasets[0].data = [
            data.efficiency || 85,
            data.utilization || 78,
            data.completion_rate || 92,
            data.energy_efficiency || 88,
            data.route_efficiency || 82
        ];
        
        this.charts.performance.update();
    }
    
    updateEfficiencyChart(data) {
        if (!this.charts.efficiency) return;
        
        this.charts.efficiency.data.datasets[0].data = [
            data.picking_speed || 85,
            data.route_optimization || 78,
            data.battery_management || 92,
            data.load_balancing || 88,
            data.error_rate || 95,
            data.throughput || 82
        ];
        
        this.charts.efficiency.update();
    }
    
    updateDemandForecast(forecastData) {
        if (!this.charts.demandForecast) return;
        
        this.charts.demandForecast.data.datasets[0].data = forecastData;
        this.charts.demandForecast.update();
    }
    
    updateRobotUtilization(robotData) {
        if (!this.charts.robotUtilization) return;
        
        const active = robotData.filter(r => r.status === 'busy').length;
        const idle = robotData.filter(r => r.status === 'idle').length;
        const charging = robotData.filter(r => r.status === 'charging').length;
        const maintenance = robotData.filter(r => r.status === 'maintenance').length;
        
        this.charts.robotUtilization.data.datasets[0].data = [active, idle, charging, maintenance];
        this.charts.robotUtilization.update();
    }
    
    createRealTimeChart(containerId, title, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: data.label || 'Real-time Data',
                    data: data.values || [],
                    borderColor: this.chartColors.primary,
                    backgroundColor: this.hexToRgba(this.chartColors.primary, 0.1),
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        return chart;
    }
    
    generateDateLabels(days) {
        const labels = [];
        const today = new Date();
        
        for (let i = 0; i < days; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        return labels;
    }
    
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Global chart manager instance
window.chartManager = new ChartManager();

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager.initCharts();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartManager;
} 