# MARK plugins/module_utils/vrf/states/overridden.py
"""
class Overridden

Handle Ansible overridden state.
"""
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Overridden(BaseState):
    """Handle overridden state for VRF resources."""

    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Override VRF resources."""
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        created_vrfs = []
        updated_vrfs = []
        deleted_vrfs = []
        errors = []
        api_responses = []

        # Delete VRFs not in desired configuration
        delete_responses = self._delete_unwanted_vrfs(configs, deleted_vrfs, errors)
        api_responses.extend(delete_responses)

        # Create/update desired VRFs
        process_responses = self._process_desired_vrfs(configs, created_vrfs, updated_vrfs, errors)
        api_responses.extend(process_responses)

        # Finalize result
        self._finalize_result(created_vrfs, updated_vrfs, deleted_vrfs, errors)

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result

    def _delete_unwanted_vrfs(self, configs: list[VrfConfig], deleted_vrfs: list[str], errors: list[str]) -> list[dict]:
        """Delete VRFs that are not in the desired configuration and return API responses."""
        responses = []
        # Get all fabrics being managed
        fabrics = list(set(config.fabric for config in configs))

        for fabric in fabrics:
            # Get all existing VRFs for this fabric from cache
            existing_vrfs = self._get_all_fabric_vrfs(fabric)
            desired_vrf_names = [config.vrf_name for config in configs if config.fabric == fabric]

            # Delete VRFs not in desired configuration
            for existing_vrf_name in existing_vrfs.keys():
                if existing_vrf_name not in desired_vrf_names:
                    success, del_response = self.api_client.delete_vrf(fabric, existing_vrf_name)
                    if self._handle_api_response(success, del_response, existing_vrf_name, "delete", deleted_vrfs, errors):
                        responses.append(del_response)

        return responses

    def _process_desired_vrfs(self, configs: list[VrfConfig], created_vrfs: list[str], updated_vrfs: list[str], errors: list[str]) -> list[dict]:
        """Process desired VRFs for create/update operations and return API responses."""
        responses = []
        for config in configs:
            exists, current_vrf = self._vrf_exists(config.fabric, config.vrf_name)
            if current_vrf is None:
                current_vrf = {}

            if exists:
                # Update if different
                if not self._vrfs_equal(current_vrf, config):
                    response_data = self._execute_vrf_operation_with_response(config, "update", created_vrfs, updated_vrfs, errors)
                    if response_data:
                        responses.append(response_data)
            else:
                # Create new VRF
                response_data = self._execute_vrf_operation_with_response(config, "create", created_vrfs, updated_vrfs, errors)
                if response_data:
                    responses.append(response_data)

        return responses
