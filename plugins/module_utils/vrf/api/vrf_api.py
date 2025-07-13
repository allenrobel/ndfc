# MARK plugins/module_utils/vrf/api/vrf_api.py
"""
VRF API client for DCNM/NDFC operations.

This module provides the VrfApi class that handles all VRF-related API operations
including creation, deletion, updates, and querying with caching support.
"""
from typing import Any, Optional
from ansible.module_utils.basic import AnsibleModule
from ...common.classes.rest_send_v2 import RestSend
from ...common.cache.cached_resource_service import CachedResourceService
from ...common.cache.cache_manager import CacheManager
from .vrf_sender import VrfSender
from .vrf_response_handler import VrfResponseHandler
from ..models.vrf_payload import VrfPayload
from ..validators.vrf_validator import VrfValidator


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
            else:
                return False, {"error": result.get("error", "Request failed"), "response": raw_response}

        except (TypeError, ValueError) as e:
            return False, {"error": f"Request error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}

    def _fetch_single_vrf(self, fabric: str, vrf_name: str) -> Optional[dict[str, Any]]:
        """Fetch a single VRF from the API (internal method)."""
        path = f"{self.base_path}/{fabric}/vrfs/{vrf_name}"
        success, response = self._execute_request("GET", path)

        if success and response.get("result", {}).get("response"):
            try:
                validated_response = VrfValidator.validate_response(response["result"]["response"])
                return validated_response.model_dump()
            except ValueError:
                return response["result"]["response"]
        return None

    def _fetch_all_vrfs(self, fabric: str) -> dict[str, dict[str, Any]]:
        """Fetch all VRFs for a fabric from the API (internal method)."""
        path = f"{self.base_path}/{fabric}/vrfs"
        success, response = self._execute_request("GET", path)

        result = {}
        if success and response.get("result", {}).get("response"):
            response_data = response["result"]["response"]

            if isinstance(response_data, list):
                for vrf_data in response_data:
                    vrf_name = vrf_data.get("vrfName")
                    if vrf_name:
                        try:
                            validated = VrfValidator.validate_response(vrf_data)
                            result[vrf_name] = validated.model_dump()
                        except ValueError:
                            result[vrf_name] = vrf_data
            else:
                vrf_name = response_data.get("vrfName")
                if vrf_name:
                    try:
                        validated = VrfValidator.validate_response(response_data)
                        result[vrf_name] = validated.model_dump()
                    except ValueError:
                        result[vrf_name] = response_data

        return result

    # Public API methods using caching service
    def get_cached(self, fabric: str, vrf_name: str, ttl_seconds: Optional[int] = None) -> Optional[dict[str, Any]]:
        """Get a single VRF with caching."""
        return self._cached_service.get_cached(
            fabric=fabric, identifier=vrf_name, fetch_func=lambda: self._fetch_single_vrf(fabric, vrf_name), ttl_seconds=ttl_seconds
        )

    def get_all_cached(self, fabric: str, ttl_seconds: Optional[int] = None) -> dict[str, dict[str, Any]]:
        """Get all VRFs for a fabric with caching."""
        return self._cached_service.get_all_cached(fabric=fabric, fetch_func=lambda: self._fetch_all_vrfs(fabric), ttl_seconds=ttl_seconds)

    def exists_cached(self, fabric: str, vrf_name: str) -> tuple[bool, Optional[dict[str, Any]]]:
        """Check if VRF exists using cache."""
        return self._cached_service.exists_cached(fabric=fabric, identifier=vrf_name, fetch_func=lambda: self._fetch_single_vrf(fabric, vrf_name))

    def create_vrf(self, vrf_payload: VrfPayload) -> tuple[bool, dict[str, Any]]:
        """Create a VRF and update cache."""
        path = f"{self.base_path}/{vrf_payload.fabric}/vrfs"
        payload = vrf_payload.model_dump(by_alias=True)

        success, response = self._execute_request("POST", path, payload)

        if success:
            # Update cache after successful creation
            if response.get("result", {}).get("response"):
                response_data = response["result"]["response"]
                self._cached_service.update_cache_after_create(vrf_payload.fabric, vrf_payload.vrf_name, response_data)

            # Return the raw controller response with RETURN_CODE for module tests
            return True, response.get("response", {})
        else:
            return False, response

    def delete_vrf(self, fabric: str, vrf_name: str) -> tuple[bool, dict[str, Any]]:
        """Delete a VRF and update cache."""
        path = f"{self.base_path}/{fabric}/vrfs/{vrf_name}"

        success, response = self._execute_request("DELETE", path)

        if success:
            # Update cache after successful deletion
            self._cached_service.update_cache_after_delete(fabric, vrf_name)
            # Return the raw controller response with RETURN_CODE for module tests
            return True, response.get("response", {})
        else:
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
                self._cached_service.update_cache_after_update(vrf_payload.fabric, vrf_payload.vrf_name, response_data)

            # Return the raw controller response with RETURN_CODE for module tests
            return True, response.get("response", {})
        else:
            return False, response

    def invalidate_fabric_cache(self, fabric: str) -> None:
        """Invalidate all VRF cache for a fabric."""
        self._cached_service.invalidate_fabric_cache(fabric)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for VRF resources."""
        if hasattr(self._cached_service._cache_manager._cache, "get_cache_stats"):
            all_stats = self._cached_service._cache_manager._cache.get_cache_stats()
            return {
                "total_entries": all_stats.get("total_entries", 0),
                "vrf_entries": all_stats.get("by_resource_type", {}).get("vrf", 0),
                "fabrics": all_stats.get("by_fabric", {}),
            }
        return {"message": "Cache statistics not available"}

    # Legacy methods for backward compatibility
    def get_vrf(self, fabric: str, vrf_name: str) -> tuple[bool, dict[str, Any]]:
        """Get a VRF by name (legacy method)."""
        vrf_data = self.get_cached(fabric, vrf_name)
        if vrf_data:
            return True, {"response": vrf_data}
        else:
            return True, {"response": None}

    def get_all_vrfs(self, fabric: str) -> tuple[bool, dict[str, Any]]:
        """Get all VRFs for a fabric (legacy method)."""
        all_vrfs = self.get_all_cached(fabric)
        vrf_list = list(all_vrfs.values())
        return True, {"response": vrf_list}
