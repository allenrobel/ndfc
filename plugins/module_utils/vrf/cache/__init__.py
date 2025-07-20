# MARK plugins/module_utils/vrf/cache/__init__.py
"""
VRF cache package.

Provides VRF-specific caching services with Pydantic model support.
"""

from .vrf_cache_service import VrfCacheService

__all__ = ["VrfCacheService"]