"""
Redis-based caching system for the Corporate Spending Tracker.
Provides high-performance caching for frequently accessed data.
"""
import redis
import json
import pickle
from typing import Any, Optional, Dict, List, Union
from django.conf import settings
from django.core.cache import cache as django_cache
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Advanced caching manager using Redis for high-performance data caching.
    Provides both simple key-value caching and complex data structure caching.
    """
    
    def __init__(self):
        """Initialize the cache manager with Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                decode_responses=False  # We'll handle encoding ourselves
            )
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
        except Exception as e:
            logger.warning(f"Redis not available, falling back to Django cache: {e}")
            self.redis_available = False
            self.redis_client = None
        
        self.default_ttl = 3600  # 1 hour default TTL
        self.cache_prefix = "corp_spend:"
    
    def _get_key(self, key: str) -> str:
        """Get full cache key with prefix."""
        return f"{self.cache_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            full_key = self._get_key(key)
            
            if self.redis_available:
                value = self.redis_client.get(full_key)
                if value:
                    return pickle.loads(value)
            else:
                return django_cache.get(full_key)
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_key = self._get_key(key)
            ttl = ttl or self.default_ttl
            
            if self.redis_available:
                serialized_value = pickle.dumps(value)
                return self.redis_client.setex(full_key, ttl, serialized_value)
            else:
                return django_cache.set(full_key, value, ttl)
                
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_key = self._get_key(key)
            
            if self.redis_available:
                return bool(self.redis_client.delete(full_key))
            else:
                return django_cache.delete(full_key)
                
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, callable_func, ttl: Optional[int] = None):
        """
        Get from cache or set using callable.
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            ttl: Time to live in seconds
            
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is None:
            try:
                value = callable_func()
                self.set(key, value, ttl)
            except Exception as e:
                logger.error(f"Error in get_or_set callable for key {key}: {e}")
                raise
        return value
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs
        """
        result = {}
        
        if self.redis_available:
            try:
                full_keys = [self._get_key(key) for key in keys]
                values = self.redis_client.mget(full_keys)
                
                for key, value in zip(keys, values):
                    if value:
                        result[key] = pickle.loads(value)
            except Exception as e:
                logger.error(f"Cache get_many error: {e}")
        else:
            for key in keys:
                value = self.get(key)
                if value is not None:
                    result[key] = value
        
        return result
    
    def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.
        
        Args:
            data: Dictionary of key-value pairs
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            
            if self.redis_available:
                pipe = self.redis_client.pipeline()
                for key, value in data.items():
                    full_key = self._get_key(key)
                    serialized_value = pickle.dumps(value)
                    pipe.setex(full_key, ttl, serialized_value)
                pipe.execute()
                return True
            else:
                for key, value in data.items():
                    self.set(key, value, ttl)
                return True
                
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Redis pattern (e.g., "spending:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            if self.redis_available:
                full_pattern = self._get_key(pattern)
                keys = self.redis_client.keys(full_pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            if self.redis_available:
                info = self.redis_client.info()
                return {
                    'redis_available': True,
                    'used_memory': info.get('used_memory_human', 'Unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self._calculate_hit_rate(info)
                }
            else:
                return {
                    'redis_available': False,
                    'fallback': 'Django cache'
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


class SpendingCacheManager:
    """
    Specialized cache manager for spending-related data.
    Provides optimized caching for frequently accessed spending calculations.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.spending_ttl = 1800  # 30 minutes for spending data
        self.analytics_ttl = 3600  # 1 hour for analytics data
    
    def get_company_spending(self, company_id: int, category: str = 'all', 
                           start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        Get cached company spending data.
        
        Args:
            company_id: Company ID
            category: Spending category
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Cached spending data or None
        """
        cache_key = f"company_spending:{company_id}:{category}:{start_date}:{end_date}"
        return self.cache_manager.get(cache_key)
    
    def set_company_spending(self, company_id: int, category: str, 
                           start_date: str, end_date: str, data: Dict):
        """Set cached company spending data."""
        cache_key = f"company_spending:{company_id}:{category}:{start_date}:{end_date}"
        self.cache_manager.set(cache_key, data, self.spending_ttl)
    
    def get_spending_statistics(self) -> Optional[Dict]:
        """Get cached spending statistics."""
        return self.cache_manager.get("spending_statistics")
    
    def set_spending_statistics(self, data: Dict):
        """Set cached spending statistics."""
        self.cache_manager.set("spending_statistics", data, self.analytics_ttl)
    
    def get_top_spenders(self, limit: int, category: str = 'all') -> Optional[List]:
        """Get cached top spenders data."""
        cache_key = f"top_spenders:{limit}:{category}"
        return self.cache_manager.get(cache_key)
    
    def set_top_spenders(self, limit: int, category: str, data: List):
        """Set cached top spenders data."""
        cache_key = f"top_spenders:{limit}:{category}"
        self.cache_manager.set(cache_key, data, self.analytics_ttl)
    
    def invalidate_company_cache(self, company_id: int):
        """Invalidate all cache entries for a specific company."""
        pattern = f"company_spending:{company_id}:*"
        self.cache_manager.clear_pattern(pattern)
    
    def invalidate_spending_cache(self):
        """Invalidate all spending-related cache entries."""
        patterns = [
            "spending_statistics",
            "top_spenders:*",
            "company_spending:*"
        ]
        for pattern in patterns:
            self.cache_manager.clear_pattern(pattern)


class APICacheManager:
    """
    Specialized cache manager for API responses.
    Provides intelligent caching for API endpoints.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.api_ttl = 900  # 15 minutes for API responses
    
    def get_api_response(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        """
        Get cached API response.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Cached API response or None
        """
        cache_key = self._build_api_key(endpoint, params)
        return self.cache_manager.get(cache_key)
    
    def set_api_response(self, endpoint: str, params: Dict, response: Any, ttl: int = None):
        """Set cached API response."""
        cache_key = self._build_api_key(endpoint, params)
        ttl = ttl or self.api_ttl
        self.cache_manager.set(cache_key, response, ttl)
    
    def _build_api_key(self, endpoint: str, params: Dict = None) -> str:
        """Build cache key for API response."""
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            return f"api:{endpoint}:{param_str}"
        return f"api:{endpoint}"
    
    def invalidate_endpoint_cache(self, endpoint: str):
        """Invalidate all cache entries for an endpoint."""
        pattern = f"api:{endpoint}:*"
        self.cache_manager.clear_pattern(pattern)


# Global cache manager instances
cache_manager = CacheManager()
spending_cache = SpendingCacheManager()
api_cache = APICacheManager()


# Convenience functions
def get_cached_spending_statistics():
    """Get spending statistics with caching."""
    return spending_cache.get_spending_statistics()


def set_cached_spending_statistics(data: Dict):
    """Set spending statistics with caching."""
    spending_cache.set_spending_statistics(data)


def get_cached_company_spending(company_id: int, category: str = 'all', 
                               start_date: str = None, end_date: str = None) -> Optional[Dict]:
    """Get company spending with caching."""
    return spending_cache.get_company_spending(company_id, category, start_date, end_date)


def set_cached_company_spending(company_id: int, category: str, 
                               start_date: str, end_date: str, data: Dict):
    """Set company spending with caching."""
    spending_cache.set_company_spending(company_id, category, start_date, end_date, data)


def invalidate_company_cache(company_id: int):
    """Invalidate cache for a specific company."""
    spending_cache.invalidate_company_cache(company_id)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache_manager.get_stats()
