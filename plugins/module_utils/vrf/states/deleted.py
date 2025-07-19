# MARK plugins/module_utils/vrf/states/deleted.py
"""
Deleted state handler for VRF resources.

This module provides the Deleted class that handles the 'deleted' Ansible state,
which removes VRF configurations from DCNM/NDFC.
"""
from typing import Any
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Deleted(BaseState):
    """Handle deleted state for VRF resources."""

    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Delete VRF resources."""
        deleted_vrfs = []
        errors = []
        api_responses = []

        for config in configs:
            if not config.vrf_name:
                # Delete all VRFs in fabric when vrf_name is empty
                responses = self._delete_all_vrfs_in_fabric(config.fabric, deleted_vrfs, errors)
                api_responses.extend(responses)
            else:
                # Delete specific VRF
                response_data = self._delete_specific_vrf(config, deleted_vrfs, errors)
                if response_data:
                    api_responses.append(response_data)

        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            if deleted_vrfs:
                self.result.msg = f"Deleted VRFs: {', '.join(deleted_vrfs)}"
            else:
                self.result.msg = "No VRFs to delete"
            self.result.stdout = self.result.msg

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result

    def _delete_specific_vrf(self, config: VrfConfig, deleted_vrfs: list[str], errors: list[str]) -> dict[str, Any] | None:
        """Delete a specific VRF and return the API response."""
        exists, _ = self._vrf_exists(config.fabric, config.vrf_name)

        if exists:
            success, response = self.api_client.delete_vrf(config.fabric, config.vrf_name)

            if success:
                deleted_vrfs.append(config.vrf_name)
                self.result.changed = True
                # Cache is automatically updated in VrfApi.delete_vrf()
                return response
            else:
                errors.append(f"Failed to delete VRF {config.vrf_name}: {response.get('error', 'Unknown error')}")
        # If VRF doesn't exist, no action needed (idempotent)
        return None

    def _delete_all_vrfs_in_fabric(self, fabric: str, deleted_vrfs: list[str], errors: list[str]) -> list[dict[str, Any]]:
        """Delete all VRFs in a fabric and return API responses."""
        responses = []
        
        # For delete operations, always get fresh data to ensure we catch
        # VRFs created outside of this module (bypassing cache)
        success, vrf_array = self.api_client.query_all_vrfs(fabric)
        
        if not success:
            errors.append(f"Failed to query VRFs in fabric {fabric}")
            return responses
            
        # vrf_array is now a list of VRF data dictionaries
        if not vrf_array:
            # No VRFs to delete in this fabric
            return responses
            
        vrfs_to_delete = []
        
        # Extract VRF names from the array
        for vrf_data in vrf_array:
            if vrf_data and vrf_data.get("vrfName"):
                vrfs_to_delete.append(vrf_data.get("vrfName"))

        if not vrfs_to_delete:
            # No VRFs to delete in this fabric
            return responses

        for vrf_name in vrfs_to_delete:
            success, response = self.api_client.delete_vrf(fabric, vrf_name)

            if success:
                deleted_vrfs.append(vrf_name)
                self.result.changed = True
                responses.append(response)
                # Cache is automatically updated in VrfApi.delete_vrf()
            else:
                errors.append(f"Failed to delete VRF {vrf_name}: {response.get('error', 'Unknown error')}")

        return responses
