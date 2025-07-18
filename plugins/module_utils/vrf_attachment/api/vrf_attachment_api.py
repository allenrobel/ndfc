# MARK plugins/module_utils/vrf_attachment/api/vrf_attachment_api.py
"""
VRF attachment API client for DCNM/NDFC operations.

This module provides the VrfAttachmentApi class that handles all VRF attachment-related
API operations including creation, deletion, updates, and querying with caching support.
"""
import json
from typing import Any, Optional, List
from ansible.module_utils.basic import AnsibleModule
from ...common.classes.rest_send_v2 import RestSend
from ...common.epp.v1.lan_fabric.rest.inventory.ep_all_switches import AllSwitches
from ...common.classes.results import Results
from ...common.cache.cached_resource_service import CachedResourceService
from ...common.cache.cache_manager import CacheManager
from .vrf_attachment_sender import VrfAttachmentSender
from .vrf_attachment_response_handler import VrfAttachmentResponseHandler
from ..models.vrf_attachment_payload import VrfAttachmentPayload


class VrfAttachmentApi:
    """VRF attachment API client with composable caching support."""

    def __init__(self, ansible_module: AnsibleModule, check_mode: bool = False, cached_service: Optional[CachedResourceService[dict[str, Any]]] = None):
        self.ansible_module = ansible_module
        self.check_mode = check_mode
        self.base_path = "/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics"

        # Inject caching service via composition
        if cached_service is None:
            # Create default cache manager and service
            cache_manager = CacheManager(default_ttl_seconds=300)
            self._cached_service = CachedResourceService[dict[str, Any]](cache_manager, "vrf_attachment")
        else:
            self._cached_service = cached_service

        # Initialize sender and response handler
        self.sender = VrfAttachmentSender(ansible_module)
        self.response_handler = VrfAttachmentResponseHandler()

        # Initialize RestSend
        params = {"check_mode": check_mode, "state": "merged"}
        self.rest_send = RestSend(params)
        self.rest_send.sender = self.sender
        self.rest_send.response_handler = self.response_handler

        # Configure non-retryable response codes for VRF attachment operations
        self.rest_send.non_retryable_codes = {400, 404, 409}

    def _execute_request(self, verb: str, path: str, payload: Optional[List[dict[str, Any]]] = None) -> tuple[bool, dict[str, Any]]:
        """Execute a REST request using RestSend."""
        try:
            self.rest_send.path = path
            self.rest_send.verb = verb.upper()

            if payload:
                # VRF attachment payload is a list, convert to JSON string
                self.rest_send.payload = json.dumps(payload)

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

    def _translate_ip_to_serial(self, fabric: str, ip_address: str) -> Optional[str]:
        """
        Translate IP address to serial number using fabric inventory.
        
        Args:
            fabric: The fabric name (used for error messages)
            ip_address: The IP address to translate
            
        Returns:
            The serial number corresponding to the IP address
            
        Raises:
            ValueError: If the IP address cannot be translated to a serial number
        """
        try:
            # Create AllSwitches instance
            all_switches = AllSwitches()
            
            # Create results instance
            results = Results()
            
            # Create RestSend instance with our sender
            params = {"check_mode": self.check_mode, "state": "merged"}
            rest_send = RestSend(params)
            rest_send.sender = self.sender
            rest_send.response_handler = self.response_handler
            
            # Configure AllSwitches
            all_switches.results = results
            all_switches.rest_send = rest_send
            
            # Refresh switch details from controller
            all_switches.refresh()
            
            # Set filter to the IP address and get serial number
            all_switches.filter = ip_address
            serial_number = all_switches.serial_number
            
            if serial_number is None:
                raise ValueError(f"Could not find serial number for IP address {ip_address} in fabric {fabric}")
                
            return serial_number
            
        except Exception as e:
            raise ValueError(f"Failed to translate IP {ip_address} to serial number: {str(e)}") from e

    def _prepare_payload_for_controller(self, payload: VrfAttachmentPayload) -> List[dict[str, Any]]:
        """
        Prepare the payload for controller by translating IP addresses to serial numbers.
        
        Args:
            payload: VrfAttachmentPayload with IP addresses
            
        Returns:
            List containing the controller payload with serial numbers
        """
        controller_payload = payload.model_dump(by_alias=True)
        
        # Translate IP addresses to serial numbers in lan_attach_list
        for lan_attach in controller_payload["lanAttachList"]:
            ip_address = lan_attach.get("ipAddress")
            if ip_address:
                # Translate IP to serial number
                serial_number = self._translate_ip_to_serial(controller_payload["fabric"], ip_address)
                lan_attach["serialNumber"] = serial_number
                # Remove the IP address field as it's not part of the controller API
                del lan_attach["ipAddress"]
        
        # Return as a list (required by controller API)
        return [controller_payload]

    def attach_vrf(self, fabric: str, payload: VrfAttachmentPayload) -> tuple[bool, dict[str, Any]]:
        """Attach VRF to switches."""
        path = f"{self.base_path}/{fabric}/vrfs/attachments"
        controller_payload = self._prepare_payload_for_controller(payload)

        success, response = self._execute_request("POST", path, controller_payload)

        if success:
            # Update cache after successful attachment
            if response.get("result", {}).get("response"):
                response_data = response["result"]["response"]
                # Cache the attachment data for the VRF
                cache_key = f"{fabric}:{payload.vrf_name}"
                self._cached_service.update_cache_after_create(fabric, cache_key, response_data)

            # Return the raw controller response
            return True, response.get("response", response)
        else:
            return False, response

    def detach_vrf(self, fabric: str, vrf_name: str, payload: VrfAttachmentPayload) -> tuple[bool, dict[str, Any]]:
        """Detach VRF from switches."""
        path = f"{self.base_path}/{fabric}/vrfs/attachments"
        controller_payload = self._prepare_payload_for_controller(payload)

        success, response = self._execute_request("POST", path, controller_payload)

        if success:
            # Update cache after successful detachment
            cache_key = f"{fabric}:{vrf_name}"
            self._cached_service.update_cache_after_delete(fabric, cache_key)

            # Return the raw controller response
            return True, response.get("response", response)
        else:
            return False, response

    def query_vrf_attachments(self, fabric: str, vrf_name: str) -> tuple[bool, dict[str, Any]]:
        """Query VRF attachments for a specific VRF."""
        path = f"{self.base_path}/{fabric}/vrfs/{vrf_name}/attachments"
        success, response = self._execute_request("GET", path)
        
        if success:
            # Return the raw controller response for query operations
            return True, response.get("response", response)
        else:
            return False, response

    def query_all_vrf_attachments(self, fabric: str) -> tuple[bool, dict[str, Any]]:
        """Query all VRF attachments in a fabric."""
        path = f"{self.base_path}/{fabric}/vrfs/attachments"
        success, response = self._execute_request("GET", path)
        
        if success:
            # Return the raw controller response for query operations
            return True, response.get("response", response)
        else:
            return False, response

    def invalidate_fabric_cache(self, fabric: str) -> None:
        """Invalidate all VRF attachment cache for a fabric."""
        self._cached_service.invalidate_fabric_cache(fabric)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for VRF attachment resources."""
        if hasattr(self._cached_service._cache_manager._cache, "get_cache_stats"):
            all_stats = self._cached_service._cache_manager._cache.get_cache_stats()
            return {
                "total_entries": all_stats.get("total_entries", 0),
                "vrf_attachment_entries": all_stats.get("by_resource_type", {}).get("vrf_attachment", 0),
                "fabrics": all_stats.get("by_fabric", {}),
            }
        return {"message": "Cache statistics not available"}