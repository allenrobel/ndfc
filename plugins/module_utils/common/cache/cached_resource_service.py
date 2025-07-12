# MARK plugins/module_utils/common/cache/cached_resource_service.py
"""
Cached resource service for API client composition.

This module provides the CachedResourceService class that adds caching capabilities
to any API client through composition, with type-safe resource-specific operations.
"""
from typing import Optional, TypeVar, Generic, Callable
from .cache_manager import CacheManager
from .cache_key import CacheKey

T = TypeVar("T")


class CachedResourceService(Generic[T]):
    """
    Service class that provides caching functionality for any resource type.
    Uses composition to inject caching capabilities into API clients.
    """

    def __init__(self, cache_manager: CacheManager, resource_type: str):
        """
        Initialize cached resource service.

        Args:
            cache_manager: Cache manager instance
            resource_type: Type of resource this service manages
        """
        self._cache_manager = cache_manager
        self._resource_type = resource_type

    def get_cached(self, fabric: str, identifier: str, fetch_func: Callable[[], Optional[T]], ttl_seconds: Optional[int] = None) -> Optional[T]:
        """
        Get a single resource with caching.

        Args:
            fabric: Fabric name
            identifier: Resource identifier
            fetch_func: Function to fetch the resource if cache miss
            ttl_seconds: TTL for cached value

        Returns:
            The cached or fetched resource
        """
        key = CacheKey(resource_type=self._resource_type, fabric=fabric, identifier=identifier)

        return self._cache_manager.get_or_fetch(key=key, fetch_func=fetch_func, ttl_seconds=ttl_seconds)

    def get_all_cached(self, fabric: str, fetch_func: Callable[[], dict[str, T]], ttl_seconds: Optional[int] = None) -> dict[str, T]:
        """
        Get all resources for a fabric with caching.

        Args:
            fabric: Fabric name
            fetch_func: Function to fetch all resources if cache miss
            ttl_seconds: TTL for cached values

        Returns:
            Dictionary of identifier -> resource data
        """
        return self._cache_manager.get_bulk_or_fetch(fabric=fabric, resource_type=self._resource_type, fetch_func=fetch_func, ttl_seconds=ttl_seconds)

    def exists_cached(self, fabric: str, identifier: str, fetch_func: Callable[[], Optional[T]]) -> tuple[bool, Optional[T]]:
        """
        Check if resource exists using cache.

        Args:
            fabric: Fabric name
            identifier: Resource identifier
            fetch_func: Function to fetch the resource if cache miss

        Returns:
            Tuple of (exists, resource_data)
        """
        resource = self.get_cached(fabric, identifier, fetch_func)
        return (resource is not None), resource

    def update_cache_after_create(self, fabric: str, identifier: str, data: T) -> None:
        """Update cache after successful create operation."""
        key = CacheKey(resource_type=self._resource_type, fabric=fabric, identifier=identifier)
        self._cache_manager.update_cache(key, data)

    def update_cache_after_update(self, fabric: str, identifier: str, data: T) -> None:
        """Update cache after successful update operation."""
        key = CacheKey(resource_type=self._resource_type, fabric=fabric, identifier=identifier)
        self._cache_manager.update_cache(key, data)

    def update_cache_after_delete(self, fabric: str, identifier: str) -> None:
        """Update cache after successful delete operation."""
        key = CacheKey(resource_type=self._resource_type, fabric=fabric, identifier=identifier)
        self._cache_manager.remove_from_cache(key)

    def invalidate_fabric_cache(self, fabric: str) -> None:
        """Invalidate all cache for a fabric."""
        self._cache_manager.invalidate_fabric(fabric, self._resource_type)
