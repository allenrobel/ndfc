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

        # Delete VRFs not in desired configuration
        self._delete_unwanted_vrfs(configs, deleted_vrfs, errors)

        # Create/update desired VRFs
        self._process_desired_vrfs(configs, created_vrfs, updated_vrfs, errors)

        # Finalize result
        self._finalize_result(created_vrfs, updated_vrfs, deleted_vrfs, errors)

        return self.result

    def _delete_unwanted_vrfs(self, configs: list[VrfConfig], deleted_vrfs: list[str], errors: list[str]) -> None:
        """Delete VRFs that are not in the desired configuration."""
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
                    self._handle_api_response(success, del_response, existing_vrf_name, "delete", deleted_vrfs, errors)

    def _process_desired_vrfs(self, configs: list[VrfConfig], created_vrfs: list[str], updated_vrfs: list[str], errors: list[str]) -> None:
        """Process desired VRFs for create/update operations."""
        for config in configs:
            exists, current_vrf = self._vrf_exists(config.fabric, config.vrf_name)
            if current_vrf is None:
                current_vrf = {}

            if exists:
                # Update if different
                if not self._vrfs_equal(current_vrf, config):
                    self._execute_vrf_operation(config, "update", created_vrfs, updated_vrfs, errors)
            else:
                # Create new VRF
                self._execute_vrf_operation(config, "create", created_vrfs, updated_vrfs, errors)
