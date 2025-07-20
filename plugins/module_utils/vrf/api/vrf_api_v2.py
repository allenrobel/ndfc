# MARK plugins/module_utils/vrf/api/vrf_api_v2.py
"""
VRF API client with Pydantic model support (Version 2).

This module provides the VrfApiV2 class that handles all VRF-related API operations
using Pydantic models throughout for type safety and consistent response formats.
"""
from typing import Any, Optional, List, Dict, Tuple
from ansible.module_utils.basic import AnsibleModule

from ...common.classes.rest_send_v2 import RestSend
from .vrf_sender import VrfSender
from .vrf_response_handler import VrfResponseHandler
from ..models.vrf_payload import VrfPayload
from ..models.vrf_data import VrfData
from ..models.controller_response import VrfControllerResponse
from ..models.response_builder import VrfResponseBuilder
from ..cache.vrf_cache_service import VrfCacheService


class VrfApiV2:
    """
    VRF API client with full Pydantic model support.

    Provides type-safe VRF operations that work exclusively with Pydantic models
    internally and return consistent VrfControllerResponse formats. All caching
    uses validated VrfData models.
    """

    def __init__(self, ansible_module: AnsibleModule, check_mode: bool = False, cache_service: Optional[VrfCacheService] = None):
        """
        Initialize VRF API client with Pydantic model support.

        Args:
            ansible_module: Ansible module instance
            check_mode: Whether in check mode
            cache_service: Optional VRF cache service for dependency injection
        """
        self.ansible_module = ansible_module
        self.check_mode = check_mode
        self.base_path = "/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics"

        # Initialize cache service with Pydantic model support
        self._cache_service = cache_service or VrfCacheService()

        # Initialize sender and response handler
        self.sender = VrfSender(ansible_module)
        self.response_handler = VrfResponseHandler()

        # Initialize RestSend
        params = {"check_mode": check_mode, "state": "merged"}
        self.rest_send = RestSend(params)
        self.rest_send.sender = self.sender
        self.rest_send.response_handler = self.response_handler

        # Configure non-retryable response codes for VRF operations
        self.rest_send.non_retryable_codes = {400, 404, 409}

    def _execute_request(self, verb: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Tuple[bool, VrfControllerResponse]:
        """
        Execute a REST request and return standardized VrfControllerResponse.

        Args:
            verb: HTTP verb (GET, POST, PUT, DELETE)
            path: Request path
            payload: Optional request payload

        Returns:
            Tuple of (success, VrfControllerResponse)
        """
        try:
            self.rest_send.path = path
            self.rest_send.verb = verb.upper()

            # Set request path in response handler for metadata
            self.response_handler.request_path = path

            if payload:
                self.rest_send.payload = payload

            self.rest_send.commit()

            # Get the VrfControllerResponse from the response handler
            controller_response = self.response_handler.get_controller_response()

            if controller_response:
                success = controller_response.RETURN_CODE in (200, 201)
                return success, controller_response
            else:
                # Fallback error response
                error_response = VrfResponseBuilder.build_error_response(
                    error_message="Failed to process controller response", method=verb, request_path=path, return_code=500
                )
                return False, error_response

        except Exception as e:
            error_response = VrfResponseBuilder.build_error_response(error_message=f"Request error: {str(e)}", method=verb, request_path=path, return_code=500)
            return False, error_response

    def _fetch_single_vrf_model(self, fabric: str, vrf_name: str) -> Optional[VrfData]:
        """
        Fetch a single VRF as VrfData model (internal method).

        Uses all-VRFs endpoint to avoid controller bug with missing vrfStatus.

        Args:
            fabric: Fabric name
            vrf_name: VRF name to fetch

        Returns:
            VrfData model or None if not found
        """
        all_vrfs = self._fetch_all_vrfs_models(fabric)
        return all_vrfs.get(vrf_name)

    def _fetch_all_vrfs_models(self, fabric: str) -> Dict[str, VrfData]:
        """
        Fetch all VRFs as VrfData models (internal method).

        Args:
            fabric: Fabric name

        Returns:
            Dictionary of vrf_name -> VrfData models
        """
        path = f"{self.base_path}/{fabric}/vrfs"
        success, controller_response = self._execute_request("GET", path)

        vrf_models = {}
        if success:
            # Extract VrfData models from controller response
            vrf_data_list = VrfResponseBuilder.validate_and_extract_vrf_data(controller_response)

            for vrf_data in vrf_data_list:
                if vrf_data.vrf_name:
                    vrf_models[vrf_data.vrf_name] = vrf_data

        return vrf_models

    # Public API methods with Pydantic model support
    def get_vrf_cached(self, fabric: str, vrf_name: str, ttl_seconds: Optional[int] = None) -> Optional[VrfData]:
        """
        Get a single VRF as VrfData model with caching.

        Args:
            fabric: Fabric name
            vrf_name: VRF name
            ttl_seconds: Optional cache TTL

        Returns:
            VrfData model or None if not found
        """
        return self._cache_service.get_vrf(
            fabric=fabric, vrf_name=vrf_name, fetch_func=lambda: self._fetch_single_vrf_model(fabric, vrf_name), ttl_seconds=ttl_seconds
        )

    def get_all_vrfs_cached(self, fabric: str, ttl_seconds: Optional[int] = None) -> Dict[str, VrfData]:
        """
        Get all VRFs as VrfData models with caching.

        Args:
            fabric: Fabric name
            ttl_seconds: Optional cache TTL

        Returns:
            Dictionary of vrf_name -> VrfData models
        """
        return self._cache_service.get_all_vrfs(fabric=fabric, fetch_func=lambda: self._fetch_all_vrfs_models(fabric), ttl_seconds=ttl_seconds)

    def vrf_exists_cached(self, fabric: str, vrf_name: str) -> Tuple[bool, Optional[VrfData]]:
        """
        Check if VRF exists using cache, returning VrfData model.

        Args:
            fabric: Fabric name
            vrf_name: VRF name to check

        Returns:
            Tuple of (exists, VrfData_model_or_None)
        """
        return self._cache_service.vrf_exists(fabric=fabric, vrf_name=vrf_name, fetch_func=lambda: self._fetch_single_vrf_model(fabric, vrf_name))

    def create_vrf(self, vrf_payload: VrfPayload) -> Tuple[bool, VrfControllerResponse]:
        """
        Create a VRF and return consistent controller response.

        Args:
            vrf_payload: VrfPayload model with VRF configuration

        Returns:
            Tuple of (success, VrfControllerResponse)
        """
        path = f"{self.base_path}/{vrf_payload.fabric}/vrfs"

        # Convert Pydantic model to controller payload format
        payload = vrf_payload.model_dump(by_alias=True)

        success, controller_response = self._execute_request("POST", path, payload)

        if success:
            # Extract VrfData models and update cache
            vrf_data_list = VrfResponseBuilder.validate_and_extract_vrf_data(controller_response)

            for vrf_data in vrf_data_list:
                if vrf_data.vrf_name:
                    self._cache_service.cache_vrf_after_create(vrf_payload.fabric, vrf_data)

        return success, controller_response

    def update_vrf(self, vrf_payload: VrfPayload) -> Tuple[bool, VrfControllerResponse]:
        """
        Update a VRF and return consistent controller response.

        Args:
            vrf_payload: VrfPayload model with updated VRF configuration

        Returns:
            Tuple of (success, VrfControllerResponse)
        """
        path = f"{self.base_path}/{vrf_payload.fabric}/vrfs"

        # Convert Pydantic model to controller payload format
        payload = vrf_payload.model_dump(by_alias=True)

        success, controller_response = self._execute_request("POST", path, payload)

        if success:
            # Extract VrfData models and update cache
            vrf_data_list = VrfResponseBuilder.validate_and_extract_vrf_data(controller_response)

            for vrf_data in vrf_data_list:
                if vrf_data.vrf_name:
                    self._cache_service.cache_vrf_after_update(vrf_payload.fabric, vrf_data)

        return success, controller_response

    def delete_vrf(self, fabric: str, vrf_name: str) -> Tuple[bool, VrfControllerResponse]:
        """
        Delete a VRF and return consistent controller response.

        Args:
            fabric: Fabric name
            vrf_name: VRF name to delete

        Returns:
            Tuple of (success, VrfControllerResponse)
        """
        path = f"{self.base_path}/{fabric}/vrfs/{vrf_name}"

        success, controller_response = self._execute_request("DELETE", path)

        if success:
            # Remove from cache after successful deletion
            self._cache_service.remove_vrf_from_cache(fabric, vrf_name)

        return success, controller_response

    def query_vrf(self, fabric: str, vrf_name: str) -> Tuple[bool, VrfControllerResponse]:
        """
        Query a specific VRF and return consistent controller response.

        Always uses all-VRFs endpoint and filters to ensure vrfStatus field
        is present (works around controller bug).

        Args:
            fabric: Fabric name
            vrf_name: VRF name to query

        Returns:
            Tuple of (success, VrfControllerResponse)
        """
        # Query all VRFs first
        success, all_vrfs_response = self.query_all_vrfs(fabric)

        if not success:
            return False, all_vrfs_response

        # Filter to specific VRF
        matching_vrfs = [vrf_dict for vrf_dict in all_vrfs_response.DATA if vrf_dict.get("vrfName") == vrf_name]

        # Build filtered response
        filtered_response = VrfResponseBuilder.from_query_response(
            raw_response=matching_vrfs, method="GET", request_path=f"{self.base_path}/{fabric}/vrfs/{vrf_name}"
        )

        return True, filtered_response

    def query_all_vrfs(self, fabric: str) -> Tuple[bool, VrfControllerResponse]:
        """
        Query all VRFs and return consistent controller response.

        Args:
            fabric: Fabric name

        Returns:
            Tuple of (success, VrfControllerResponse)
        """
        path = f"{self.base_path}/{fabric}/vrfs"
        return self._execute_request("GET", path)

    def invalidate_fabric_cache(self, fabric: str) -> None:
        """
        Invalidate all VRF cache for a fabric.

        Args:
            fabric: Fabric name to invalidate
        """
        self._cache_service.invalidate_fabric_cache(fabric)
