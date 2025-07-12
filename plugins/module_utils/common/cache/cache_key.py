# MARK plugins/module_utils/common/cache/cache_key.py
"""
Cache key implementation for structured caching.

This module provides the CacheKey class that creates immutable, hashable keys
for cache entries based on resource type, fabric, and identifier.
"""
from pydantic import BaseModel, ConfigDict


class CacheKey(BaseModel):
    """Structured cache key for consistent hashing."""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)  # Make immutable for hashing

    resource_type: str  # e.g., "vrf", "network", "interface"
    fabric: str
    identifier: str  # e.g., vrf_name, network_id, interface_name

    def __hash__(self) -> int:
        """Make CacheKey hashable."""
        return hash((self.resource_type, self.fabric, self.identifier))

    def __str__(self) -> str:
        """String representation for logging."""
        return f"{self.resource_type}:{self.fabric}:{self.identifier}"
