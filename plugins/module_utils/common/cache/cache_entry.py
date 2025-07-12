# MARK plugins/module_utils/common/cache/cache_entry.py
"""
Cache entry implementation with TTL support.

This module provides the CacheEntry class that wraps cached data with metadata
including timestamps and TTL (Time To Live) expiration tracking.
"""
from typing import Optional, Generic, TypeVar
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class CacheEntry(BaseModel, Generic[T]):
    """Generic cache entry with TTL support."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: T
    timestamp: datetime
    ttl_seconds: Optional[int] = None

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False

        expiry_time = self.timestamp + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time
