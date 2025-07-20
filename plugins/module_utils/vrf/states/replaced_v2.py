# MARK plugins/module_utils/vrf/states/replaced_v2.py
"""
Replaced state handler for VRF resources with Pydantic model support.

This module provides the ReplacedV2 class that handles the 'replaced' Ansible state
using VrfApiV2 and VrfData models for type safety and consistent responses.
"""
from typing import List
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state_v2 import BaseStateV2


class ReplacedV2(BaseStateV2):
    """Handle replaced state for VRF resources with Pydantic model support."""

    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """
        Replace VRF resources using VrfApiV2 and VrfData models.

        Deletes existing VRFs and creates new ones with the desired configuration.
        This is a destructive operation that ensures exact configuration match.

        Args:
            configs: List of VRF configurations to replace

        Returns:
            ModuleResult with consistent response format
        """
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        created_vrfs = []
        replaced_vrfs = []
        errors = []
        controller_responses = []

        for config in configs:
            # Check if VRF exists using VrfData model
            exists, current_vrf_model = self._vrf_exists(config.fabric, config.vrf_name)

            if exists:
                # VRF exists - replace it (delete then create)
                controller_response = self._replace_existing_vrf(config, replaced_vrfs, errors)
                if controller_response:
                    controller_responses.append(controller_response)
            else:
                # VRF doesn't exist - create new VRF
                controller_response = self._execute_vrf_operation_with_response(config, "create", created_vrfs, replaced_vrfs, errors)
                if controller_response:
                    controller_responses.append(controller_response)

        # Finalize result with replaced VRFs treated as updates
        self._finalize_result(created_vrfs, replaced_vrfs, [], errors)

        # Set response data for successful operations with consistent format
        if controller_responses:
            self.result.response = self._convert_controller_responses_to_data_list(controller_responses)

        return self.result

    def _replace_existing_vrf(self, config: VrfConfig, replaced_vrfs: List[str], errors: List[str]):
        """
        Replace an existing VRF by deleting and recreating it.

        Args:
            config: VrfConfig with replacement configuration
            replaced_vrfs: List to append replaced VRF names to
            errors: List to append error messages to

        Returns:
            VrfControllerResponse from create operation if successful, None if failed
        """
        # First delete the existing VRF
        success, del_response = self.api_client.delete_vrf(config.fabric, config.vrf_name)

        if success and del_response.RETURN_CODE in (200, 201):
            # Delete successful - now create the new VRF
            success, create_response = self.api_client.create_vrf(config.to_payload())

            if success and create_response.RETURN_CODE in (200, 201):
                replaced_vrfs.append(config.vrf_name)
                self.result.changed = True
                return create_response
            else:
                errors.append(f"Failed to create replacement VRF {config.vrf_name}: {create_response.MESSAGE}")
        else:
            errors.append(f"Failed to delete existing VRF {config.vrf_name}: {del_response.MESSAGE}")

        return None
