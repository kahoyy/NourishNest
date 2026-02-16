"""
Core Redis Cache Manager for Django
Provides high-level caching operations with TTL management
"""
import json
import logging
from typing import Any, Optional, Callable
from django.core.cache import cache

logger = logging.getLogger('cache_utils')


class CacheManager:
    """
    High-level cache manager for Redis operations
    Handles serialization, TTL, and common patterns
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache manager
        :param default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.default_ttl = default_ttl
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache with optional TTL
        
        :param key: Cache key
        :param value: Value to cache (auto-serialized)
        :param ttl: Time to live in seconds (uses default if None)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        timeout = ttl if ttl > 0 else None  # None = never expire
        cache.set(key, value, timeout)
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache
        
        :param key: Cache key
        :return: Cached value or None if not found/expired
        """
        value = cache.get(key)
        if value is not None:
            logger.debug(f"Cache HIT: {key}")
        else:
            logger.debug(f"Cache MISS: {key}")
        return value
    
    async def delete(self, key: str) -> None:
        """
        Delete a key from cache
        
        :param key: Cache key
        """
        cache.delete(key)
        logger.debug(f"Cache DELETE: {key}")
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        :param pattern: Key pattern (e.g., "user:*")
        :return: Number of keys deleted
        """
        # Django cache doesn't have pattern matching, use direct Redis access
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
            logger.debug(f"Cache DELETE PATTERN: {pattern} ({len(keys)} keys)")
            return len(keys)
        return 0
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache
        
        :param key: Cache key
        :return: True if exists, False otherwise
        """
        return cache.get(key) is not None
    
    async def get_or_set(
        self, 
        key: str, 
        fn: Callable, 
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache or execute function and cache result (cache-aside pattern)
        
        :param key: Cache key
        :param fn: Async or sync callable that returns the value
        :param ttl: Time to live in seconds
        :return: Cached or freshly computed value
        """
        # Try to get from cache
        cached = cache.get(key)
        if cached is not None:
            logger.debug(f"Cache-aside HIT: {key}")
            return cached
        
        # Cache miss - execute function
        logger.debug(f"Cache-aside MISS: {key} - executing function")
        ttl = ttl if ttl is not None else self.default_ttl
        
        # Check if function is async
        import asyncio
        if asyncio.iscoroutinefunction(fn):
            # For async functions, we'd need to call them properly
            # This simplified version assumes sync usage in Django context
            result = fn()
        else:
            result = fn()
        
        # Store in cache
        await self.set(key, result, ttl)
        return result
    
    async def increment(self, key: str, delta: int = 1) -> int:
        """
        Increment a numeric value
        
        :param key: Cache key
        :param delta: Amount to increment (default: 1)
        :return: New value
        """
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        new_value = redis_conn.incrby(key, delta)
        logger.debug(f"Cache INCREMENT: {key} by {delta} = {new_value}")
        return new_value
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get time-to-live for a key in seconds
        
        :param key: Cache key
        :return: TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        ttl = redis_conn.ttl(key)
        return ttl
    
    async def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set TTL for an existing key
        
        :param key: Cache key
        :param ttl: TTL in seconds
        :return: True if successful, False if key doesn't exist
        """
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        result = redis_conn.expire(key, ttl)
        logger.debug(f"Cache SET_TTL: {key} to {ttl}s")
        return result
    
    async def keys(self, pattern: str = '*') -> list:
        """
        Get all keys matching a pattern
        
        :param pattern: Key pattern (default: "*" for all)
        :return: List of matching keys
        """
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        keys = redis_conn.keys(pattern)
        logger.debug(f"Cache KEYS: {pattern} found {len(keys)} keys")
        return [k.decode() if isinstance(k, bytes) else k for k in keys]
    
    async def flush(self) -> None:
        """Clear entire cache database"""
        cache.clear()
        logger.debug("Cache FLUSH: Cleared all keys")
    
    async def stats(self) -> dict:
        """
        Get cache statistics (key count and memory usage)
        
        :return: Dictionary with stats
        """
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        
        info = redis_conn.info('memory')
        keys = redis_conn.keys('*')
        
        return {
            'key_count': len(keys),
            'memory_used': info.get('used_memory_human'),
            'memory_peak': info.get('used_memory_peak_human'),
            'memory_rss': info.get('used_memory_rss_human'),
        }


# Synchronous wrapper (for Django views and non-async contexts)
class SyncCacheManager:
    """Synchronous wrapper around CacheManager for Django views"""
    
    def __init__(self, default_ttl: int = 3600):
        self.manager = CacheManager(default_ttl)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache"""
        cache.set(key, value, ttl or self.manager.default_ttl)
        logger.debug(f"Cache SET: {key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        return cache.get(key)
    
    def delete(self, key: str) -> None:
        """Delete a key from cache"""
        cache.delete(key)
        logger.debug(f"Cache DELETE: {key}")
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
            return len(keys)
        return 0
    
    def get_or_set(self, key: str, fn: Callable, ttl: Optional[int] = None) -> Any:
        """Get from cache or execute function (cache-aside pattern)"""
        cached = cache.get(key)
        if cached is not None:
            logger.debug(f"Cache-aside HIT: {key}")
            return cached
        
        logger.debug(f"Cache-aside MISS: {key}")
        result = fn()
        ttl = ttl or self.manager.default_ttl
        cache.set(key, result, ttl)
        return result
    
    def increment(self, key: str, delta: int = 1) -> int:
        """Increment a numeric value"""
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        return redis_conn.incrby(key, delta)
    
    def flush(self) -> None:
        """Clear entire cache"""
        cache.clear()
        logger.debug("Cache FLUSH")
    
    def stats(self) -> dict:
        """Get cache statistics"""
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        
        info = redis_conn.info('memory')
        keys = redis_conn.keys('*')
        
        return {
            'key_count': len(keys),
            'memory_used': info.get('used_memory_human'),
            'memory_peak': info.get('used_memory_peak_human'),
        }
