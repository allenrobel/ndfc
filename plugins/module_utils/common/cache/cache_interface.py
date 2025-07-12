# MARK plugins/module_utils/common/cache/cache_interface.py
"""
Abstract cache interface for pluggable cache implementations.

This module defines the CacheInterface abstract base class that provides
a common interface for different cache implementations (memory, Redis, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic
from .cache_key import CacheKey

T = TypeVar("T")


class CacheInterface(ABC, Generic[T]):
    """Abstract interface for cache implementations."""

    @abstractmethod
    def get(self, key: CacheKey) -> Optional[T]:
        """Get value from cache."""

    @abstractmethod
    def set(self, key: CacheKey, value: T, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""

    @abstractmethod
    def delete(self, key: CacheKey) -> None:
        """Delete value from cache."""

    @abstractmethod
    def get_bulk(self, fabric: str, resource_type: str) -> dict[str, T]:
        """Get all cached items for a fabric and resource type."""

    @abstractmethod
    def set_bulk(self, fabric: str, resource_type: str, data: dict[str, T], ttl_seconds: Optional[int] = None) -> None:
        """Set multiple items in cache."""

    @abstractmethod
    def invalidate_fabric(self, fabric: str, resource_type: Optional[str] = None) -> None:
        """Invalidate all cache entries for a fabric, optionally filtered by resource type."""

    @abstractmethod
    def clear(self) -> None:
        """Clear entire cache."""
