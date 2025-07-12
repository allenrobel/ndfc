# MARK plugins/module_utils/common/cache/memory_cache.py
"""
In-memory cache implementation with TTL support.

This module provides the MemoryCache class that implements the CacheInterface
for storing cached data in memory with automatic expiration based on TTL.
"""
from typing import Any, Optional, Dict
from datetime import datetime
from .cache_interface import CacheInterface
from .cache_key import CacheKey
from .cache_entry import CacheEntry


class MemoryCache(CacheInterface[Any]):
    """In-memory cache implementation with TTL support."""

    def __init__(self, default_ttl_seconds: Optional[int] = None):
        self._cache: Dict[CacheKey, CacheEntry[Any]] = {}
        self._default_ttl = default_ttl_seconds

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self._cache[key]

    def get(self, key: CacheKey) -> Optional[Any]:
        """Get value from cache."""
        self._cleanup_expired()

        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            return entry.data

        # Remove expired entry
        if entry:
            del self._cache[key]

        return None

    def set(self, key: CacheKey, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        ttl = ttl_seconds or self._default_ttl
        entry = CacheEntry(data=value, timestamp=datetime.now(), ttl_seconds=ttl)
        self._cache[key] = entry

    def delete(self, key: CacheKey) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)

    def get_bulk(self, fabric: str, resource_type: str) -> dict[str, Any]:
        """Get all cached items for a fabric and resource type."""
        self._cleanup_expired()

        result = {}
        for key, entry in self._cache.items():
            if key.fabric == fabric and key.resource_type == resource_type and not entry.is_expired():
                result[key.identifier] = entry.data

        return result

    def set_bulk(self, fabric: str, resource_type: str, data: dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """Set multiple items in cache."""
        ttl = ttl_seconds or self._default_ttl
        timestamp = datetime.now()

        for identifier, value in data.items():
            key = CacheKey(resource_type=resource_type, fabric=fabric, identifier=identifier)
            entry = CacheEntry(data=value, timestamp=timestamp, ttl_seconds=ttl)
            self._cache[key] = entry

    def invalidate_fabric(self, fabric: str, resource_type: Optional[str] = None) -> None:
        """Invalidate all cache entries for a fabric, optionally filtered by resource type."""
        keys_to_remove = []

        for key in self._cache:
            if key.fabric == fabric:
                if resource_type is None or key.resource_type == resource_type:
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
