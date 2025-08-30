/**
 * Frontend Configuration
 * Centralized configuration for the Corporate Spending Tracker frontend
 */

// Configuration object that can be easily modified for different environments
window.APP_CONFIG = {
    // API Configuration
    API: {
        // Base URL for the backend API
        BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'http://127.0.0.1:8000/api'
            : '/api',  // Use relative path for production
        
        // Timeout for API requests (in milliseconds)
        TIMEOUT: 30000,
        
        // Retry configuration
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000,
    },
    
    // Documentation URLs (can be overridden for different environments)
    DOCS: {
        SWAGGER: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:8000/api/docs/'
            : '/api/docs/',
        REDOC: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:8000/api/redoc/'
            : '/api/redoc/',
    },
    
    // UI Configuration
    UI: {
        // Default pagination size
        DEFAULT_PAGE_SIZE: 20,
        
        // Chart colors for consistent theming
        CHART_COLORS: {
            lobbying: '#ef4444',      // Red
            charitable: '#10b981',    // Green
            political: '#3b82f6',     // Blue
            total: '#f59e0b',         // Amber
        },
        
        // Animation delays
        ANIMATION_DELAY: 300,
        
        // Default chart configuration
        CHART_OPTIONS: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#e5e7eb'  // Light gray for dark theme
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#e5e7eb' },
                    grid: { color: '#374151' }
                },
                y: {
                    ticks: { color: '#e5e7eb' },
                    grid: { color: '#374151' }
                }
            }
        }
    },
    
    // Logging Configuration
    LOGGING: {
        // Enable/disable frontend logging
        ENABLED: true,
        
        // Log level: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
        LEVEL: 'INFO',
        
        // Send logs to backend
        SEND_TO_BACKEND: true,
        
        // Maximum log entries to keep in memory
        MAX_LOG_ENTRIES: 100,
    },
    
    // Application metadata
    APP: {
        NAME: 'Corporate Spending Tracker',
        VERSION: '1.0.0',
        DESCRIPTION: 'Track corporate spending across lobbying, political contributions, and charitable grants',
    }
};

// Helper functions for configuration
window.CONFIG_HELPERS = {
    /**
     * Get the full API URL for an endpoint
     * @param {string} endpoint - The API endpoint path (without leading slash)
     * @returns {string} Full API URL
     */
    getApiUrl: function(endpoint) {
        const baseUrl = window.APP_CONFIG.API.BASE_URL;
        const separator = endpoint.startsWith('/') ? '' : '/';
        return `${baseUrl}${separator}${endpoint}`;
    },
    
    /**
     * Get chart colors for consistent theming
     * @param {string} category - Category name (lobbying, charitable, political, total)
     * @returns {string} Hex color code
     */
    getChartColor: function(category) {
        return window.APP_CONFIG.UI.CHART_COLORS[category] || '#6b7280';
    },
    
    /**
     * Get chart colors array for multiple categories
     * @param {string[]} categories - Array of category names
     * @returns {string[]} Array of hex color codes
     */
    getChartColors: function(categories) {
        return categories.map(category => this.getChartColor(category));
    },
    
    /**
     * Check if we're running in development mode
     * @returns {boolean} True if in development
     */
    isDevelopment: function() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1';
    },
    
    /**
     * Format currency values
     * @param {number} value - Numeric value
     * @returns {string} Formatted currency string
     */
    formatCurrency: function(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    },
    
    /**
     * Format large numbers with appropriate suffixes
     * @param {number} value - Numeric value
     * @returns {string} Formatted number string
     */
    formatNumber: function(value) {
        if (value >= 1e9) {
            return (value / 1e9).toFixed(1) + 'B';
        } else if (value >= 1e6) {
            return (value / 1e6).toFixed(1) + 'M';
        } else if (value >= 1e3) {
            return (value / 1e3).toFixed(1) + 'K';
        }
        return value.toString();
    }
};

// Environment-specific overrides
// This allows for easy customization per environment without changing the main config

// Development environment overrides
if (window.CONFIG_HELPERS.isDevelopment()) {
    // Enable debug logging in development
    window.APP_CONFIG.LOGGING.LEVEL = 'DEBUG';
    
    // You can add more development-specific overrides here
    console.log('🔧 Development mode detected - using local API endpoints');
    console.log('📡 API Base URL:', window.APP_CONFIG.API.BASE_URL);
}

// Production environment overrides
else {
    // Disable debug logging in production
    window.APP_CONFIG.LOGGING.LEVEL = 'WARNING';
    
    // You can add more production-specific overrides here
    console.log('🚀 Production mode - using production API endpoints');
}

// Make configuration globally available
console.log('⚙️ Configuration loaded:', window.APP_CONFIG.APP.NAME, 'v' + window.APP_CONFIG.APP.VERSION);
