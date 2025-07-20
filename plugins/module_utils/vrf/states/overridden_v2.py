# MARK plugins/module_utils/vrf/states/overridden_v2.py
"""
Overridden state handler for VRF resources with Pydantic model support.

This module provides the OverriddenV2 class that handles the 'overridden' Ansible state
using VrfApiV2 and VrfData models for type safety and consistent responses.
"""
from typing import List, Set
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state_v2 import BaseStateV2


class OverriddenV2(BaseStateV2):
    """Handle overridden state for VRF resources with Pydantic model support."""

    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """
        Override VRF resources using VrfApiV2 and VrfData models.

        Ensures only the specified VRFs exist in each fabric by:
        1. Creating/updating desired VRFs
        2. Deleting any existing VRFs not in the desired set

        Args:
            configs: List of VRF configurations that should be the only VRFs

        Returns:
            ModuleResult with consistent response format
        """
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        created_vrfs = []
        updated_vrfs = []
        deleted_vrfs = []
        errors = []
        controller_responses = []

        # Group configs by fabric for override processing
        fabric_configs = {}
        for config in configs:
            if config.fabric not in fabric_configs:
                fabric_configs[config.fabric] = []
            fabric_configs[config.fabric].append(config)

        # Process each fabric independently
        for fabric, fabric_config_list in fabric_configs.items():
            self._process_fabric_override(fabric, fabric_config_list, created_vrfs, updated_vrfs, deleted_vrfs, errors, controller_responses)

        # Finalize result
        self._finalize_result(created_vrfs, updated_vrfs, deleted_vrfs, errors)

        # Set response data for successful operations with consistent format
        if controller_responses:
            self.result.response = self._convert_controller_responses_to_data_list(controller_responses)

        return self.result

    def _process_fabric_override(
        self,
        fabric: str,
        desired_configs: List[VrfConfig],
        created_vrfs: List[str],
        updated_vrfs: List[str],
        deleted_vrfs: List[str],
        errors: List[str],
        controller_responses: List,
    ) -> None:
        """
        Process override operation for a single fabric.

        Args:
            fabric: Fabric name to process
            desired_configs: List of desired VRF configurations for this fabric
            created_vrfs: List to append created VRF names to
            updated_vrfs: List to append updated VRF names to
            deleted_vrfs: List to append deleted VRF names to
            errors: List to append error messages to
            controller_responses: List to append successful controller responses to
        """
        # Get desired VRF names for this fabric
        desired_vrf_names = {config.vrf_name for config in desired_configs}

        # Get all existing VRFs in fabric as VrfData models
        existing_vrf_models = self._get_all_fabric_vrfs(fabric)
        existing_vrf_names = set(existing_vrf_models.keys())

        # Step 1: Create or update desired VRFs
        for config in desired_configs:
            if config.vrf_name in existing_vrf_models:
                # VRF exists - check if update needed using VrfData model
                current_vrf_model = existing_vrf_models[config.vrf_name]
                if not self._vrfs_equal(current_vrf_model, config):
                    controller_response = self._execute_vrf_operation_with_response(config, "update", created_vrfs, updated_vrfs, errors)
                    if controller_response:
                        controller_responses.append(controller_response)
                # If VRF exists and is identical, no action needed
            else:
                # VRF doesn't exist - create it
                controller_response = self._execute_vrf_operation_with_response(config, "create", created_vrfs, updated_vrfs, errors)
                if controller_response:
                    controller_responses.append(controller_response)

        # Step 2: Delete VRFs that exist but are not desired
        vrfs_to_delete = existing_vrf_names - desired_vrf_names

        for vrf_name in vrfs_to_delete:
            success, controller_response = self.api_client.delete_vrf(fabric, vrf_name)

            if success and controller_response.RETURN_CODE in (200, 201):
                deleted_vrfs.append(vrf_name)
                self.result.changed = True
                controller_responses.append(controller_response)
            else:
                errors.append(f"Failed to delete unwanted VRF {vrf_name}: {controller_response.MESSAGE}")
