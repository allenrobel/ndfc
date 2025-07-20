# MARK plugins/module_utils/vrf/states/deleted_v2.py
"""
Deleted state handler for VRF resources with Pydantic model support.

This module provides the DeletedV2 class that handles the 'deleted' Ansible state
using VrfApiV2 and VrfData models for type safety and consistent responses.
"""
from typing import List, Set
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state_v2 import BaseStateV2


class DeletedV2(BaseStateV2):
    """Handle deleted state for VRF resources with Pydantic model support."""

    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """
        Delete VRF resources using VrfApiV2 and VrfData models.

        Deletes specified VRFs or all VRFs in a fabric if no specific VRF is named.
        All operations work with validated Pydantic models.

        Args:
            configs: List of VRF configurations to delete

        Returns:
            ModuleResult with consistent response format
        """
        deleted_vrfs = []
        errors = []
        controller_responses = []

        for config in configs:
            if config.vrf_name:
                # Delete specific VRF
                controller_response = self._delete_specific_vrf(config, deleted_vrfs, errors)
                if controller_response:
                    controller_responses.append(controller_response)
            else:
                # Delete all VRFs in fabric
                fabric_responses = self._delete_all_vrfs_in_fabric(config.fabric, deleted_vrfs, errors)
                controller_responses.extend(fabric_responses)

        # Finalize result
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

        # Set response data for successful operations with consistent format
        if controller_responses:
            self.result.response = self._convert_controller_responses_to_data_list(controller_responses)

        return self.result

    def _delete_specific_vrf(self, config: VrfConfig, deleted_vrfs: List[str], errors: List[str]):
        """
        Delete a specific VRF using VrfApiV2.

        Args:
            config: VrfConfig with VRF to delete
            deleted_vrfs: List to append deleted VRF names to
            errors: List to append error messages to

        Returns:
            VrfControllerResponse if successful, None if failed
        """
        # Check if VRF exists using VrfData model
        exists, _ = self._vrf_exists(config.fabric, config.vrf_name)

        if exists:
            success, controller_response = self.api_client.delete_vrf(config.fabric, config.vrf_name)

            if success and controller_response.RETURN_CODE in (200, 201):
                deleted_vrfs.append(config.vrf_name)
                self.result.changed = True
                return controller_response
            else:
                errors.append(f"Failed to delete VRF {config.vrf_name}: {controller_response.MESSAGE}")
        else:
            # VRF doesn't exist - this is not an error for delete operations (idempotent)
            pass

        return None

    def _delete_all_vrfs_in_fabric(self, fabric: str, deleted_vrfs: List[str], errors: List[str]) -> List:
        """
        Delete all VRFs in a fabric using VrfApiV2.

        Args:
            fabric: Fabric name
            deleted_vrfs: List to append deleted VRF names to
            errors: List to append error messages to

        Returns:
            List of VrfControllerResponse models for successful deletions
        """
        controller_responses = []

        # Get all VRFs in fabric as VrfData models
        vrf_models = self._get_all_fabric_vrfs(fabric)

        for vrf_name, vrf_model in vrf_models.items():
            success, controller_response = self.api_client.delete_vrf(fabric, vrf_name)

            if success and controller_response.RETURN_CODE in (200, 201):
                deleted_vrfs.append(vrf_name)
                self.result.changed = True
                controller_responses.append(controller_response)
            else:
                errors.append(f"Failed to delete VRF {vrf_name}: {controller_response.MESSAGE}")

        return controller_responses
