# MARK plugins/module_utils/common/cache/cache_manager.py
"""
Central cache manager for coordinating cache operations.

This module provides the CacheManager class that acts as the main entry point
for all caching operations, with pluggable cache implementations and TTL management.
"""
from typing import Any, Optional, Callable, TypeVar
from .cache_interface import CacheInterface
from .cache_key import CacheKey
from .memory_cache import MemoryCache

T = TypeVar("T")


class CacheManager:
    """Central cache manager for coordinating cache operations."""

    def __init__(self, cache_impl: Optional[CacheInterface[Any]] = None, default_ttl_seconds: Optional[int] = 300):
        """
        Initialize cache manager.

        Args:
            cache_impl: Cache implementation to use (defaults to MemoryCache)
            default_ttl_seconds: Default TTL for cache entries (5 minutes default)
        """
        self._cache = cache_impl or MemoryCache(default_ttl_seconds)
        self._default_ttl = default_ttl_seconds

    def get_or_fetch(self, key: CacheKey, fetch_func: Callable[[], T], ttl_seconds: Optional[int] = None) -> T:
        """
        Get from cache or fetch and cache the result.

        Args:
            key: Cache key
            fetch_func: Function to call if cache miss
            ttl_seconds: TTL for cached value

        Returns:
            The cached or fetched value
        """
        # Try cache first
        cached_value = self._cache.get(key)
        if cached_value is not None:
            return cached_value

        # Cache miss - fetch and cache
        value = fetch_func()
        self._cache.set(key, value, ttl_seconds or self._default_ttl)
        return value

    def get_bulk_or_fetch(self, fabric: str, resource_type: str, fetch_func: Callable[[], dict[str, T]], ttl_seconds: Optional[int] = None) -> dict[str, T]:
        """
        Get bulk data from cache or fetch and cache all results.

        Args:
            fabric: Fabric name
            resource_type: Type of resource (e.g., 'vrf', 'network')
            fetch_func: Function to fetch all resources
            ttl_seconds: TTL for cached values

        Returns:
            Dictionary of identifier -> resource data
        """
        # Check if we have any cached data for this fabric/resource_type
        cached_data = self._cache.get_bulk(fabric, resource_type)

        # For simplicity, if we have any cached data, return it
        # More sophisticated logic could check cache completeness
        if cached_data:
            return cached_data

        # Cache miss - fetch all and cache
        all_data = fetch_func()
        self._cache.set_bulk(fabric, resource_type, all_data, ttl_seconds or self._default_ttl)
        return all_data

    def update_cache(self, key: CacheKey, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Update cache after successful operations."""
        self._cache.set(key, value, ttl_seconds or self._default_ttl)

    def remove_from_cache(self, key: CacheKey) -> None:
        """Remove item from cache after successful deletion."""
        self._cache.delete(key)

    def invalidate_fabric(self, fabric: str, resource_type: Optional[str] = None) -> None:
        """Invalidate cache for a fabric."""
        self._cache.invalidate_fabric(fabric, resource_type)

    def clear_cache(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
