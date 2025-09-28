"""
Application Performance Monitoring (APM) system for the Corporate Spending Tracker.
Provides comprehensive monitoring, logging, and alerting capabilities.
"""
import time
import json
import logging
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import psutil
import os

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    Tracks function execution times, database queries, and system metrics.
    """
    
    def __init__(self):
        self.metrics_cache = {}
        self.alert_thresholds = {
            'api_response_time': 1000,  # 1 second
            'db_query_time': 500,       # 500ms
            'memory_usage': 80,         # 80%
            'cpu_usage': 90             # 90%
        }
    
    def monitor_function(self, function_name: str = None, 
                        alert_threshold: float = None):
        """
        Decorator to monitor function performance.
        
        Args:
            function_name: Custom name for the function
            alert_threshold: Custom alert threshold in milliseconds
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                func_name = function_name or func.__name__
                threshold = alert_threshold or self.alert_thresholds.get('api_response_time', 1000)
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Log performance metric
                    self._log_performance_metric(func_name, duration, success=True)
                    
                    # Store in cache for dashboard
                    self._store_performance_metric(func_name, duration, success=True)
                    
                    # Check for alerts
                    if duration * 1000 > threshold:
                        self._trigger_performance_alert(func_name, duration, threshold)
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    self._log_performance_metric(func_name, duration, success=False, error=str(e))
                    self._store_performance_metric(func_name, duration, success=False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def monitor_database_queries(self, func: Callable) -> Callable:
        """
        Decorator to monitor database query performance.
        
        Args:
            func: Function to monitor
            
        Returns:
            Decorated function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_queries = len(connection.queries)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                queries_executed = len(connection.queries) - initial_queries
                
                # Log database performance
                self._log_database_metrics(func.__name__, duration, queries_executed)
                
                # Check for slow queries
                if duration * 1000 > self.alert_thresholds['db_query_time']:
                    self._trigger_database_alert(func.__name__, duration, queries_executed)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                self._log_database_metrics(func.__name__, duration, 0, error=str(e))
                raise
        
        return wrapper
    
    def _log_performance_metric(self, function_name: str, duration: float, 
                               success: bool = True, error: str = None):
        """Log performance metric with structured logging."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO' if success else 'ERROR',
            'type': 'performance_metric',
            'function_name': function_name,
            'duration_ms': duration * 1000,
            'success': success,
            'error': error
        }
        
        logger.info(json.dumps(log_data))
    
    def _log_database_metrics(self, function_name: str, duration: float, 
                            query_count: int, error: str = None):
        """Log database performance metrics."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO' if not error else 'ERROR',
            'type': 'database_metrics',
            'function_name': function_name,
            'duration_ms': duration * 1000,
            'query_count': query_count,
            'avg_query_time_ms': (duration * 1000) / query_count if query_count > 0 else 0,
            'error': error
        }
        
        logger.info(json.dumps(log_data))
    
    def _store_performance_metric(self, function_name: str, duration: float, 
                                 success: bool = True, error: str = None):
        """Store performance metric in cache for dashboard."""
        key = f"perf_metrics:{function_name}"
        metrics = cache.get(key, [])
        
        metric_data = {
            'timestamp': time.time(),
            'duration': duration,
            'success': success,
            'error': error
        }
        
        metrics.append(metric_data)
        
        # Keep only last 100 measurements
        if len(metrics) > 100:
            metrics = metrics[-100:]
        
        cache.set(key, metrics, 3600)  # 1 hour TTL
    
    def _trigger_performance_alert(self, function_name: str, duration: float, threshold: float):
        """Trigger performance alert for slow functions."""
        alert_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'WARNING',
            'type': 'performance_alert',
            'function_name': function_name,
            'duration_ms': duration * 1000,
            'threshold_ms': threshold,
            'message': f"Function {function_name} exceeded performance threshold"
        }
        
        logger.warning(json.dumps(alert_data))
    
    def _trigger_database_alert(self, function_name: str, duration: float, query_count: int):
        """Trigger database performance alert."""
        alert_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'WARNING',
            'type': 'database_alert',
            'function_name': function_name,
            'duration_ms': duration * 1000,
            'query_count': query_count,
            'message': f"Database operation {function_name} exceeded performance threshold"
        }
        
        logger.warning(json.dumps(alert_data))
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for dashboard."""
        summary = {}
        
        # Get metrics for all monitored functions
        function_names = ['api_call', 'data_ingestion', 'spending_calculation', 'database_query']
        
        for func_name in function_names:
            key = f"perf_metrics:{func_name}"
            metrics = cache.get(key, [])
            
            if metrics:
                durations = [m['duration'] for m in metrics if m.get('success', True)]
                success_count = sum(1 for m in metrics if m.get('success', True))
                error_count = len(metrics) - success_count
                
                summary[func_name] = {
                    'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
                    'max_duration_ms': max(durations) if durations else 0,
                    'min_duration_ms': min(durations) if durations else 0,
                    'sample_count': len(metrics),
                    'success_count': success_count,
                    'error_count': error_count,
                    'success_rate': success_count / len(metrics) if metrics else 0
                }
        
        return summary
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Process info
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'process_memory_mb': process_memory,
                'available_memory_mb': memory.available / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}


class StructuredLogger:
    """
    Structured logging system for comprehensive application monitoring.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                     duration: float, user_id: str = None, **kwargs):
        """Log API call with structured data."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO',
            'type': 'api_call',
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_ms': duration * 1000,
            'user_id': user_id,
            **kwargs
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_data_ingestion(self, source: str, records_processed: int, 
                          success: bool, errors: List[str] = None):
        """Log data ingestion events."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO' if success else 'ERROR',
            'type': 'data_ingestion',
            'source': source,
            'records_processed': records_processed,
            'success': success,
            'errors': errors or []
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              unit: str = 'ms', **metadata):
        """Log performance metrics."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO',
            'type': 'performance_metric',
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            **metadata
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error_type: str, message: str, **context):
        """Log error with context."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'ERROR',
            'type': 'error',
            'error_type': error_type,
            'message': message,
            **context
        }
        
        self.logger.error(json.dumps(log_data))
    
    def log_security_event(self, event_type: str, user_id: str = None, 
                          ip_address: str = None, **context):
        """Log security-related events."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'WARNING',
            'type': 'security_event',
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            **context
        }
        
        self.logger.warning(json.dumps(log_data))


class AlertManager:
    """
    Alert management system for monitoring and notifications.
    """
    
    def __init__(self):
        self.alert_rules = {
            'high_error_rate': {'threshold': 0.1, 'window': 300},  # 10% error rate in 5 minutes
            'slow_response': {'threshold': 2000, 'window': 60},    # 2s response time
            'high_memory': {'threshold': 85, 'window': 60},        # 85% memory usage
            'database_slow': {'threshold': 1000, 'window': 60}     # 1s database query
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions and return active alerts."""
        alerts = []
        
        # Check error rate
        error_rate = self._calculate_error_rate()
        if error_rate > self.alert_rules['high_error_rate']['threshold']:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f'Error rate is {error_rate:.2%}',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check system metrics
        system_metrics = PerformanceMonitor().get_system_metrics()
        if system_metrics.get('memory_percent', 0) > self.alert_rules['high_memory']['threshold']:
            alerts.append({
                'type': 'high_memory',
                'severity': 'medium',
                'message': f'Memory usage is {system_metrics.get("memory_percent", 0):.1f}%',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        # This is a simplified implementation
        # In production, you'd query logs or metrics database
        return 0.0  # Placeholder


# Global instances
performance_monitor = PerformanceMonitor()
structured_logger = StructuredLogger('corp_spend')
alert_manager = AlertManager()


# Convenience decorators
def monitor_performance(function_name: str = None, threshold: float = None):
    """Decorator to monitor function performance."""
    return performance_monitor.monitor_function(function_name, threshold)


def monitor_database(func):
    """Decorator to monitor database queries."""
    return performance_monitor.monitor_database_queries(func)


def log_api_call(endpoint: str, method: str, status_code: int, duration: float, **kwargs):
    """Log API call."""
    structured_logger.log_api_call(endpoint, method, status_code, duration, **kwargs)


def log_data_ingestion(source: str, records: int, success: bool, errors: List[str] = None):
    """Log data ingestion event."""
    structured_logger.log_data_ingestion(source, records, success, errors)


def log_error(error_type: str, message: str, **context):
    """Log error event."""
    structured_logger.log_error(error_type, message, **context)
