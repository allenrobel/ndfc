# MARK plugins/module_utils/vrf/cache/vrf_cache_service.py
"""
VRF-specific cache service for Pydantic model storage.

This module provides a specialized cache service for VRF operations that
ensures all cached data uses VrfData Pydantic models for type safety.
"""
from typing import Optional, Callable, Dict, List
from ...common.cache.cached_resource_service import CachedResourceService
from ...common.cache.cache_manager import CacheManager
from ..models.vrf_data import VrfData


class VrfCacheService:
    """
    VRF-specific cache service with Pydantic model enforcement.

    Wraps the generic CachedResourceService to ensure all VRF data
    is stored and retrieved as VrfData Pydantic models, providing
    type safety and validation throughout the VRF workflow.
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize VRF cache service.

        Args:
            cache_manager: Optional cache manager. If None, creates default.
        """
        if cache_manager is None:
            cache_manager = CacheManager(default_ttl_seconds=300)

        # Create underlying cached service with VrfData type
        self._cached_service = CachedResourceService[VrfData](cache_manager=cache_manager, resource_type="vrf")

    def get_vrf(self, fabric: str, vrf_name: str, fetch_func: Callable[[], Optional[VrfData]], ttl_seconds: Optional[int] = None) -> Optional[VrfData]:
        """
        Get a single VRF with caching, ensuring VrfData model.

        Args:
            fabric: Fabric name
            vrf_name: VRF name identifier
            fetch_func: Function that returns VrfData model on cache miss
            ttl_seconds: TTL for cached value

        Returns:
            VrfData model or None if not found
        """
        return self._cached_service.get_cached(fabric=fabric, identifier=vrf_name, fetch_func=fetch_func, ttl_seconds=ttl_seconds)

    def get_all_vrfs(self, fabric: str, fetch_func: Callable[[], Dict[str, VrfData]], ttl_seconds: Optional[int] = None) -> Dict[str, VrfData]:
        """
        Get all VRFs for a fabric with caching, ensuring VrfData models.

        Args:
            fabric: Fabric name
            fetch_func: Function that returns dict of vrf_name -> VrfData
            ttl_seconds: TTL for cached values

        Returns:
            Dictionary of vrf_name -> VrfData models
        """
        return self._cached_service.get_all_cached(fabric=fabric, fetch_func=fetch_func, ttl_seconds=ttl_seconds)

    def vrf_exists(self, fabric: str, vrf_name: str, fetch_func: Callable[[], Optional[VrfData]]) -> tuple[bool, Optional[VrfData]]:
        """
        Check if VRF exists using cache.

        Args:
            fabric: Fabric name
            vrf_name: VRF name to check
            fetch_func: Function that returns VrfData model on cache miss

        Returns:
            Tuple of (exists, VrfData_model_or_None)
        """
        return self._cached_service.exists_cached(fabric=fabric, identifier=vrf_name, fetch_func=fetch_func)

    def cache_vrf_after_create(self, fabric: str, vrf_data: VrfData) -> None:
        """
        Cache VRF data after successful creation.

        Args:
            fabric: Fabric name
            vrf_data: VrfData model to cache
        """
        if not vrf_data.vrf_name:
            raise ValueError("VrfData must have vrf_name for caching")

        self._cached_service.update_cache_after_create(fabric=fabric, identifier=vrf_data.vrf_name, data=vrf_data)

    def cache_vrf_after_update(self, fabric: str, vrf_data: VrfData) -> None:
        """
        Cache VRF data after successful update.

        Args:
            fabric: Fabric name
            vrf_data: Updated VrfData model to cache
        """
        if not vrf_data.vrf_name:
            raise ValueError("VrfData must have vrf_name for caching")

        self._cached_service.update_cache_after_update(fabric=fabric, identifier=vrf_data.vrf_name, data=vrf_data)

    def remove_vrf_from_cache(self, fabric: str, vrf_name: str) -> None:
        """
        Remove VRF from cache after deletion.

        Args:
            fabric: Fabric name
            vrf_name: VRF name to remove
        """
        self._cached_service.update_cache_after_delete(fabric=fabric, identifier=vrf_name)

    def invalidate_fabric_cache(self, fabric: str) -> None:
        """
        Invalidate all VRF cache for a fabric.

        Args:
            fabric: Fabric name to invalidate
        """
        self._cached_service.invalidate_fabric_cache(fabric)

    def cache_multiple_vrfs(self, fabric: str, vrf_data_list: List[VrfData]) -> None:
        """
        Cache multiple VRF models efficiently.

        Args:
            fabric: Fabric name
            vrf_data_list: List of VrfData models to cache
        """
        for vrf_data in vrf_data_list:
            if vrf_data.vrf_name:
                self.cache_vrf_after_update(fabric, vrf_data)

    def get_cached_vrf_names(self, fabric: str) -> List[str]:
        """
        Get list of cached VRF names for a fabric.

        Args:
            fabric: Fabric name

        Returns:
            List of VRF names currently in cache
        """
        cached_vrfs = self._cached_service.get_all_cached(fabric=fabric, fetch_func=lambda: {})  # Don't fetch if not in cache
        return list(cached_vrfs.keys())

    def convert_dict_to_vrf_data(self, vrf_dict: Dict[str, any]) -> VrfData:
        """
        Convert a dictionary to VrfData model with validation.

        Args:
            vrf_dict: Dictionary containing VRF data

        Returns:
            Validated VrfData model

        Raises:
            ValidationError: If data is invalid
        """
        return VrfData.model_validate(vrf_dict)

    def convert_dicts_to_vrf_data_map(self, vrf_dicts: Dict[str, Dict[str, any]]) -> Dict[str, VrfData]:
        """
        Convert dictionary of VRF dicts to VrfData models.

        Args:
            vrf_dicts: Dict of vrf_name -> vrf_data_dict

        Returns:
            Dict of vrf_name -> VrfData models
        """
        vrf_models = {}
        for vrf_name, vrf_dict in vrf_dicts.items():
            try:
                vrf_models[vrf_name] = self.convert_dict_to_vrf_data(vrf_dict)
            except Exception:
                # Skip invalid VRF data but continue processing others
                continue
        return vrf_models
