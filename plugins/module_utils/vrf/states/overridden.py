# MARK plugins/module_utils/vrf/states/overridden.py
"""
Overridden state handler for VRF resources with Pydantic model support.

This module provides the Overridden class that handles the 'overridden' Ansible state
using VrfApiV2 and VrfData models for type safety and consistent responses.
"""
from typing import List, Set
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state_v2 import BaseStateV2


class Overridden(BaseStateV2):
    """Handle overridden state for VRF resources with Pydantic model support."""

    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """
        Override VRF resources using VrfApiV2 and VrfData models.

        Ensures only the specified VRFs exist in their fabrics. Deletes all other VRFs
        and creates/updates the desired ones to match exact configuration.

        Args:
            configs: List of VRF configurations that should exist

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

        # Delete unwanted VRFs first
        delete_responses = self._delete_unwanted_vrfs(configs, deleted_vrfs, errors)
        controller_responses.extend(delete_responses)

        # Create/update desired VRFs
        process_responses = self._process_desired_vrfs(configs, created_vrfs, updated_vrfs, errors)
        controller_responses.extend(process_responses)

        # Finalize result
        self._finalize_result(created_vrfs, updated_vrfs, deleted_vrfs, errors)

        # Set response data for successful operations with consistent format
        if controller_responses:
            self.result.response = self._convert_controller_responses_to_data_list(controller_responses)

        return self.result

    def _delete_unwanted_vrfs(self, configs: List[VrfConfig], deleted_vrfs: List[str], errors: List[str]) -> List:
        """
        Delete VRFs not in desired configuration using VrfApiV2.

        Args:
            configs: List of desired VRF configurations
            deleted_vrfs: List to append deleted VRF names to
            errors: List to append error messages to

        Returns:
            List of VrfControllerResponse models for successful deletions
        """
        controller_responses = []
        # Get all fabrics being managed
        fabrics = list(set(config.fabric for config in configs))

        for fabric in fabrics:
            # Get all existing VRFs for this fabric as VrfData models
            existing_vrf_models = self._get_all_fabric_vrfs(fabric)
            desired_vrf_names = [config.vrf_name for config in configs if config.fabric == fabric]

            # Delete VRFs not in desired configuration
            for existing_vrf_name in existing_vrf_models.keys():
                if existing_vrf_name not in desired_vrf_names:
                    success, controller_response = self.api_client.delete_vrf(fabric, existing_vrf_name)

                    if success and controller_response.RETURN_CODE in (200, 201):
                        deleted_vrfs.append(existing_vrf_name)
                        self.result.changed = True
                        controller_responses.append(controller_response)
                    else:
                        errors.append(f"Failed to delete unwanted VRF {existing_vrf_name}: {controller_response.MESSAGE}")

        return controller_responses

    def _process_desired_vrfs(self, configs: List[VrfConfig], created_vrfs: List[str], updated_vrfs: List[str], errors: List[str]) -> List:
        """
        Process desired VRFs for create/update operations using VrfApiV2.

        Args:
            configs: List of desired VRF configurations
            created_vrfs: List to append created VRF names to
            updated_vrfs: List to append updated VRF names to
            errors: List to append error messages to

        Returns:
            List of VrfControllerResponse models for successful operations
        """
        controller_responses = []

        for config in configs:
            # Check if VRF exists using VrfData model
            exists, current_vrf_model = self._vrf_exists(config.fabric, config.vrf_name)

            if exists and current_vrf_model:
                # VRF exists - check if update is needed using VrfData model
                if not self._vrfs_equal(current_vrf_model, config):
                    controller_response = self._execute_vrf_operation_with_response(config, "update", created_vrfs, updated_vrfs, errors)
                    if controller_response:
                        controller_responses.append(controller_response)
                # If VRF exists and is identical, no action needed (idempotent)
            else:
                # VRF doesn't exist - create new VRF
                controller_response = self._execute_vrf_operation_with_response(config, "create", created_vrfs, updated_vrfs, errors)
                if controller_response:
                    controller_responses.append(controller_response)

        return controller_responses
