// Frontend logging utility
class FrontendLogger {
    constructor() {
        this.logFile = 'frontend_debug.log';
        this.maxLogSize = 1024 * 1024; // 1MB max log size
    }

    // Write log entry to file
    async writeLog(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data,
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        try {
            // Send log to backend endpoint
            await fetch(window.CONFIG_HELPERS.getApiUrl('logs/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            // Fallback: store in localStorage if backend is unavailable
            this.storeInLocalStorage(logEntry);
        }
    }

    // Fallback storage in localStorage
    storeInLocalStorage(logEntry) {
        try {
            const logs = JSON.parse(localStorage.getItem('frontend_logs') || '[]');
            logs.push(logEntry);
            
            // Keep only last 100 logs
            if (logs.length > 100) {
                logs.splice(0, logs.length - 100);
            }
            
            localStorage.setItem('frontend_logs', JSON.stringify(logs));
        } catch (error) {
            console.error('Failed to store log in localStorage:', error);
        }
    }

    // Log levels
    async info(message, data = null) {
        console.info(`[INFO] ${message}`, data);
        await this.writeLog('INFO', message, data);
    }

    async error(message, data = null) {
        console.error(`[ERROR] ${message}`, data);
        await this.writeLog('ERROR', message, data);
    }

    async warn(message, data = null) {
        console.warn(`[WARN] ${message}`, data);
        await this.writeLog('WARN', message, data);
    }

    async debug(message, data = null) {
        console.debug(`[DEBUG] ${message}`, data);
        await this.writeLog('DEBUG', message, data);
    }

    // Log API requests
    async logApiRequest(url, method, params, response, error = null) {
        const logData = {
            url,
            method,
            params,
            response: response ? {
                status: response.status,
                statusText: response.statusText,
                data: response.data || response
            } : null,
            error: error ? {
                message: error.message,
                stack: error.stack
            } : null
        };

        if (error) {
            await this.error(`API Request Failed: ${method} ${url}`, logData);
        } else {
            await this.info(`API Request Success: ${method} ${url}`, logData);
        }
    }

    // Log user interactions
    async logUserAction(action, details = null) {
        await this.info(`User Action: ${action}`, details);
    }

    // Log Alpine.js state changes
    async logStateChange(component, property, oldValue, newValue) {
        await this.debug(`State Change: ${component}.${property}`, {
            oldValue,
            newValue
        });
    }

    // Get logs from localStorage (for debugging)
    getStoredLogs() {
        try {
            return JSON.parse(localStorage.getItem('frontend_logs') || '[]');
        } catch (error) {
            return [];
        }
    }

    // Clear stored logs
    clearStoredLogs() {
        localStorage.removeItem('frontend_logs');
    }
}

// Create global logger instance
window.frontendLogger = new FrontendLogger();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FrontendLogger;
}

