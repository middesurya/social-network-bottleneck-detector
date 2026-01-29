"""Redis caching service."""
import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
import hashlib

import redis
from redis.exceptions import ConnectionError, TimeoutError

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data in Redis."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self._test_connection()
        return self._client
    
    def _test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            self._client.ping()
            self._connected = True
            logger.info("Redis connection established")
            return True
        except (ConnectionError, TimeoutError) as e:
            self._connected = False
            logger.warning(f"Redis connection failed: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"bottleneck:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self._connected:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        if not self._connected:
            return False
        
        try:
            ttl = ttl or settings.cache_ttl
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if not self._connected:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False
    
    def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with a given prefix."""
        if not self._connected:
            return 0
        
        try:
            pattern = f"bottleneck:{prefix}:*"
            keys = list(self.client.scan_iter(match=pattern))
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all bottleneck cache keys."""
        if not self._connected:
            return False
        
        try:
            keys = list(self.client.scan_iter(match="bottleneck:*"))
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            logger.warning(f"Cache clear all failed: {e}")
            return False


# Singleton instance
cache_service = CacheService()


def cached(prefix: str, ttl: Optional[int] = None):
    """Decorator to cache function results.
    
    Usage:
        @cached("graph_stats", ttl=300)
        async def get_stats():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_service._make_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache_service.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_service.set(key, result, ttl)
            logger.debug(f"Cache set: {key}")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(*prefixes: str):
    """Decorator to invalidate cache after function execution.
    
    Usage:
        @invalidate_cache("graph_stats", "bottlenecks")
        async def run_algorithm():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Clear caches
            for prefix in prefixes:
                cache_service.clear_prefix(prefix)
                logger.debug(f"Cache invalidated: {prefix}")
            
            return result
        return wrapper
    return decorator
