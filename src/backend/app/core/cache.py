"""
Cache module for Phase 2 Adaptive Learning
Uses Redis for caching LLM responses and token budgets
"""
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import redis.asyncio as redis
from ..config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

class Cache:
    def __init__(self):
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL)
        else:
            self.redis = None
            logger.warning("Redis URL not configured, using in-memory cache only")
        
        # In-memory fallback cache
        self.memory_cache: Dict[str, tuple] = {}  # key -> (value, expiry_timestamp)
    
    async def get(self, key: str, allow_stale: bool = False) -> Optional[Any]:
        """
        Get value from cache (Redis first, then memory fallback).
        """
        # Try Redis first
        if self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error for key {key}: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            if expiry is None or expiry > datetime.now().timestamp():
                return value
            elif allow_stale:
                # Return stale value but warn
                logger.warning(f"Returning stale cache value for {key}")
                return value
            else:
                # Remove expired entry
                del self.memory_cache[key]
        
        return None
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set value in cache (Redis first, then memory fallback).
        """
        success = True
        
        # Set in Redis
        if self.redis:
            try:
                await self.redis.set(key, json.dumps(value), ex=ex)
            except Exception as e:
                logger.warning(f"Redis set error for key {key}: {e}")
                success = False
        
        # Set in memory cache
        expiry = None
        if ex:
            expiry = datetime.now().timestamp() + ex
        self.memory_cache[key] = (value, expiry)
        
        return success
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        """
        success = True
        
        # Delete from Redis
        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error for key {key}: {e}")
                success = False
        
        # Delete from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        return success
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        """
        # Check Redis
        if self.redis:
            try:
                return await self.redis.exists(key) > 0
            except Exception as e:
                logger.warning(f"Redis exists error for key {key}: {e}")
        
        # Check memory cache
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            if expiry is None or expiry > datetime.now().timestamp():
                return True
            else:
                # Remove expired entry
                del self.memory_cache[key]
        
        return False
    
    async def flush(self) -> bool:
        """
        Flush all cache entries.
        """
        success = True
        
        # Flush Redis
        if self.redis:
            try:
                await self.redis.flushdb()
            except Exception as e:
                logger.warning(f"Redis flush error: {e}")
                success = False
        
        # Flush memory cache
        self.memory_cache.clear()
        
        return success

# Global instance
cache = Cache()