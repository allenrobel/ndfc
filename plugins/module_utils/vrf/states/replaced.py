# MARK plugins/module_utils/vrf/states/replaced.py
"""
Replaced state handler for VRF resources.

This module provides the Replaced class that handles the 'replaced' Ansible state,
which replaces existing VRF configurations in DCNM/NDFC.
"""
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Replaced(BaseState):
    """Handle replaced state for VRF resources."""

    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Replace VRF resources."""
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        replaced_vrfs = []
        created_vrfs = []
        errors = []
        api_responses = []

        # Process each VRF configuration
        self._process_vrf_replacements(configs, replaced_vrfs, created_vrfs, errors, api_responses)

        # Finalize result using BaseState helper
        self._finalize_result(created_vrfs, replaced_vrfs, [], errors)

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result

    def _process_vrf_replacements(
        self, configs: list[VrfConfig], replaced_vrfs: list[str], created_vrfs: list[str], errors: list[str], api_responses: list[dict]
    ) -> None:
        """Process VRF replacements for each configuration."""
        for config in configs:
            exists, current_vrf = self._vrf_exists(config.fabric, config.vrf_name)
            if current_vrf is None:
                current_vrf = {}

            if exists:
                # Replace if different
                if not self._vrfs_equal(current_vrf, config):
                    response_data = self._replace_existing_vrf(config, replaced_vrfs, errors)
                    if response_data:
                        api_responses.extend(response_data)  # extend because replace returns list
                # If VRF exists and is identical, no action needed (idempotent)
            else:
                # Create new VRF (same as merged for non-existing resources)
                response_data = self._execute_vrf_operation_with_response(config, "create", created_vrfs, [], errors)
                if response_data:
                    api_responses.append(response_data)

    def _replace_existing_vrf(self, config: VrfConfig, replaced_vrfs: list[str], errors: list[str]) -> list[dict] | None:
        """Replace an existing VRF by deleting and recreating it and return API responses."""
        responses = []
        # For NDFC, replace is typically DELETE followed by POST
        # First delete the existing VRF
        success, del_response = self.api_client.delete_vrf(config.fabric, config.vrf_name)

        if success:
            responses.append(del_response)
            # Cache is automatically updated in VrfApi.delete_vrf()
            # Now create the new VRF
            success, create_response = self.api_client.create_vrf(config.to_payload())

            if success:
                replaced_vrfs.append(config.vrf_name)
                self.result.changed = True
                responses.append(create_response)
                # Cache is automatically updated in VrfApi.create_vrf()
                return responses
            else:
                errors.append(f"Failed to create VRF {config.vrf_name} after deletion: {create_response.get('error', 'Unknown error')}")
        else:
            errors.append(f"Failed to delete VRF {config.vrf_name} for replacement: {del_response.get('error', 'Unknown error')}")

        return None
