# MARK plugins/module_utils/vrf/api/vrf_api.py
"""
VRF API client for DCNM/NDFC operations.

This module provides the VrfApi class that handles all VRF-related API operations
including creation, deletion, updates, and querying with caching support.
"""
import copy
from typing import Any, Optional
from ansible.module_utils.basic import AnsibleModule
from ...common.classes.rest_send_v2 import RestSend
from ...common.cache.cached_resource_service import CachedResourceService
from ...common.cache.cache_manager import CacheManager
from .vrf_sender import VrfSender
from .vrf_response_handler import VrfResponseHandler
from ..models.vrf_payload import VrfPayload


class VrfApi:
    """VRF API client with composable caching support."""

    def __init__(self, ansible_module: AnsibleModule, check_mode: bool = False, cached_service: Optional[CachedResourceService[dict[str, Any]]] = None):
        self.ansible_module = ansible_module
        self.check_mode = check_mode
        self.base_path = "/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics"

        # Inject caching service via composition
        if cached_service is None:
            # Create default cache manager and service
            cache_manager = CacheManager(default_ttl_seconds=300)
            self._cached_service = CachedResourceService[dict[str, Any]](cache_manager, "vrf")
        else:
            self._cached_service = cached_service

        # Initialize sender and response handler
        self.sender = VrfSender(ansible_module)
        self.response_handler = VrfResponseHandler()

        # Initialize RestSend
        params = {"check_mode": check_mode, "state": "merged"}
        self.rest_send = RestSend(params)
        self.rest_send.sender = self.sender
        self.rest_send.response_handler = self.response_handler

        # Configure non-retryable response codes for VRF operations
        # 400: Bad Request - Invalid parameters won't improve with retries
        # 404: Not Found - Definitive response for existence checks
        # 409: Conflict - Resource already exists or conflicts with current state
        self.rest_send.non_retryable_codes = {400, 404, 409}

    def _extract_vrf_data_for_cache(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract VRF data from response for cache storage.

        The controller response includes metadata (MESSAGE, RETURN_CODE, etc.)
        but cache should only store the actual VRF data.

        Args:
            response_data: Full controller response

        Returns:
            VRF data suitable for cache storage
        """
        # For POST responses, the VRF data might be directly in the response
        # (after field name transformation) or in a DATA field

        if "DATA" in response_data:
            # Query-style response with DATA field
            return response_data["DATA"]

        # POST response - extract VRF fields, exclude controller metadata
        vrf_data = {}
        controller_fields = {"MESSAGE", "METHOD", "REQUEST_PATH", "RETURN_CODE", "ERROR"}

        for key, value in response_data.items():
            if key not in controller_fields:
                vrf_data[key] = value

        return vrf_data

    def _transform_vrf_field_names(self, vrf_data: dict[str, Any]) -> dict[str, Any]:
        """
        Transform VRF field names from controller format to standard format for cache consistency.

        Args:
            vrf_data: VRF data with controller field names

        Returns:
            VRF data with transformed field names
        """
        # Create a copy to avoid modifying the original
        transformed_data = copy.deepcopy(vrf_data)

        # Field name mappings from controller format to standard format
        field_mappings = {"VRF Id": "vrfId", "VRF Name": "vrfName"}

        # Handle both direct VRF data and DATA-wrapped responses
        if "DATA" in transformed_data:
            # Response has DATA wrapper
            data_field = transformed_data["DATA"]
            if isinstance(data_field, dict):
                self._apply_field_mappings(data_field, field_mappings)
            elif isinstance(data_field, list):
                for item in data_field:
                    if isinstance(item, dict):
                        self._apply_field_mappings(item, field_mappings)
        else:
            # Direct VRF data
            self._apply_field_mappings(transformed_data, field_mappings)

        return transformed_data

    def _apply_field_mappings(self, vrf_dict: dict[str, Any], field_mappings: dict[str, str]) -> None:
        """Apply field name mappings to a VRF dictionary in place."""
        for old_field, new_field in field_mappings.items():
            if old_field in vrf_dict:
                vrf_dict[new_field] = vrf_dict.pop(old_field)

    def _execute_request(self, verb: str, path: str, payload: Optional[dict[str, Any]] = None) -> tuple[bool, dict[str, Any]]:
        """Execute a REST request using RestSend."""
        try:
            self.rest_send.path = path
            self.rest_send.verb = verb.upper()

            if payload:
                self.rest_send.payload = payload

            self.rest_send.commit()
            result = self.rest_send.result_current

            # Include raw controller response for modules that need RETURN_CODE, etc.
            raw_response = self.rest_send.response_current

            if result.get("success", False):
                # Return both processed result and raw controller response
                return True, {"result": result, "response": raw_response}

            return False, {"error": result.get("error", "Request failed"), "response": raw_response}

        except (TypeError, ValueError) as e:
            return False, {"error": f"Request error: {str(e)}"}
        except (AttributeError, KeyError) as e:
            return False, {"error": f"Unexpected error: {str(e)}"}

    def _fetch_single_vrf_from_all(self, fabric: str, vrf_name: str) -> Optional[dict[str, Any]]:
        """Fetch a single VRF by querying all VRFs (avoids controller bug with missing vrfStatus)."""
        all_vrfs = self._fetch_all_vrfs(fabric)
        return all_vrfs.get(vrf_name)

    def _fetch_all_vrfs(self, fabric: str) -> dict[str, dict[str, Any]]:
        """Fetch all VRFs for a fabric from the API (internal method)."""
        path = f"{self.base_path}/{fabric}/vrfs"
        success, response = self._execute_request("GET", path)

        result = {}
        if success and response.get("result", {}).get("response"):
            response_data = response["result"]["response"]

            if isinstance(response_data, list):
                for vrf_data in response_data:
                    # Transform field names for cache consistency
                    transformed_vrf = self._transform_vrf_field_names(vrf_data)
                    # Get VRF name (try both transformed and original field names)
                    vrf_name = transformed_vrf.get("vrfName") or transformed_vrf.get("VRF Name")
                    if vrf_name:
                        result[vrf_name] = transformed_vrf
            else:
                # Transform field names for cache consistency
                transformed_vrf = self._transform_vrf_field_names(response_data)
                # Get VRF name (try both transformed and original field names)
                vrf_name = transformed_vrf.get("vrfName") or transformed_vrf.get("VRF Name")
                if vrf_name:
                    result[vrf_name] = transformed_vrf

        return result

    # Public API methods using caching service
    def get_cached(self, fabric: str, vrf_name: str, ttl_seconds: Optional[int] = None) -> Optional[dict[str, Any]]:
        """Get a single VRF with caching."""
        return self._cached_service.get_cached(
            fabric=fabric, identifier=vrf_name, fetch_func=lambda: self._fetch_single_vrf_from_all(fabric, vrf_name), ttl_seconds=ttl_seconds
        )

    def get_all_cached(self, fabric: str, ttl_seconds: Optional[int] = None) -> dict[str, dict[str, Any]]:
        """Get all VRFs for a fabric with caching."""
        return self._cached_service.get_all_cached(fabric=fabric, fetch_func=lambda: self._fetch_all_vrfs(fabric), ttl_seconds=ttl_seconds)

    def exists_cached(self, fabric: str, vrf_name: str) -> tuple[bool, Optional[dict[str, Any]]]:
        """Check if VRF exists using cache."""
        return self._cached_service.exists_cached(fabric=fabric, identifier=vrf_name, fetch_func=lambda: self._fetch_single_vrf_from_all(fabric, vrf_name))

    def create_vrf(self, vrf_payload: VrfPayload) -> tuple[bool, dict[str, Any]]:
        """Create a VRF and update cache."""
        path = f"{self.base_path}/{vrf_payload.fabric}/vrfs"
        payload = vrf_payload.model_dump(by_alias=True)

        success, response = self._execute_request("POST", path, payload)

        if success:
            # Update cache after successful creation
            if response.get("result", {}).get("response"):
                response_data = response["result"]["response"]

                # Extract VRF data for cache (excluding controller metadata)
                vrf_data = self._extract_vrf_data_for_cache(response_data)
                self._cached_service.update_cache_after_create(vrf_payload.fabric, vrf_payload.vrf_name, vrf_data)

            # Return the processed response with field transformations
            processed_response = self.response_handler.result
            if processed_response and processed_response.get("response"):
                return True, processed_response["response"]
            # Fail early if response processing failed
            raise ValueError(f"VRF creation succeeded but response processing failed. Raw response: {response}")
        return False, response

    def delete_vrf(self, fabric: str, vrf_name: str) -> tuple[bool, dict[str, Any]]:
        """Delete a VRF and update cache."""
        path = f"{self.base_path}/{fabric}/vrfs/{vrf_name}"

        success, response = self._execute_request("DELETE", path)

        if success:
            # Update cache after successful deletion
            self._cached_service.update_cache_after_delete(fabric, vrf_name)
            # Return the raw controller response with RETURN_CODE for module tests
            return True, response.get("response", response)

        return False, response

    def update_vrf(self, vrf_payload: VrfPayload) -> tuple[bool, dict[str, Any]]:
        """Update a VRF and update cache."""
        path = f"{self.base_path}/{vrf_payload.fabric}/vrfs"
        payload = vrf_payload.model_dump(by_alias=True)

        success, response = self._execute_request("POST", path, payload)

        if success:
            # Update cache after successful update
            if response.get("result", {}).get("response"):
                response_data = response["result"]["response"]

                # Extract VRF data for cache (excluding controller metadata)
                vrf_data = self._extract_vrf_data_for_cache(response_data)
                self._cached_service.update_cache_after_update(vrf_payload.fabric, vrf_payload.vrf_name, vrf_data)

            # Return the processed response with field transformations
            processed_response = self.response_handler.result
            if processed_response and processed_response.get("response"):
                return True, processed_response["response"]
            # Fail early if response processing failed
            raise ValueError(f"VRF update succeeded but response processing failed. Raw response: {response}")
        return False, response

    def invalidate_fabric_cache(self, fabric: str) -> None:
        """Invalidate all VRF cache for a fabric."""
        self._cached_service.invalidate_fabric_cache(fabric)

    # Query methods that return VRF data arrays (with vrfStatus field)
    def query_vrf(self, fabric: str, vrf_name: str) -> tuple[bool, list[dict[str, Any]]]:
        """Query a specific VRF and return array with single VRF (includes vrfStatus)."""
        # Always query all VRFs to ensure vrfStatus field is present (controller bug workaround)
        success, all_vrfs = self.query_all_vrfs(fabric)
        if not success:
            return False, []

        # Filter to specific VRF
        matching_vrfs = [vrf for vrf in all_vrfs if vrf.get("vrfName") == vrf_name]
        return True, matching_vrfs

    def query_all_vrfs(self, fabric: str) -> tuple[bool, list[dict[str, Any]]]:
        """Query all VRFs for a fabric and return array of VRF data (includes vrfStatus)."""
        path = f"{self.base_path}/{fabric}/vrfs"
        success, response = self._execute_request("GET", path)

        if success:
            # Extract just the VRF data array, no controller metadata wrapping
            response_data = response.get("response", response)
            vrf_data = response_data.get("DATA", [])
            # Ensure we return a list even if controller returns single VRF as dict
            if isinstance(vrf_data, dict):
                return True, [vrf_data]
            return True, vrf_data if isinstance(vrf_data, list) else []
        return False, []
