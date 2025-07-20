# MARK plugins/module_utils/vrf/states/merged_v2.py
"""
Merged state handler for VRF resources with Pydantic model support.

This module provides the MergedV2 class that handles the 'merged' Ansible state
using VrfApiV2 and VrfData models for type safety and consistent responses.
"""
from typing import List
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state_v2 import BaseStateV2


class MergedV2(BaseStateV2):
    """Handle merged state for VRF resources with Pydantic model support."""

    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """
        Merge VRF resources using VrfApiV2 and VrfData models.

        Creates new VRFs and updates existing ones to match desired configuration.
        All operations work with validated Pydantic models.

        Args:
            configs: List of VRF configurations to merge

        Returns:
            ModuleResult with consistent response format
        """
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        created_vrfs = []
        updated_vrfs = []
        errors = []
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

        # Finalize result
        self._finalize_result(created_vrfs, updated_vrfs, [], errors)

        # Set response data for successful operations with consistent format
        if controller_responses:
            self.result.response = self._convert_controller_responses_to_data_list(controller_responses)

        return self.result
