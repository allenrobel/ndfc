# MARK plugins/module_utils/vrf/states/deleted.py
"""
Deleted state handler for VRF resources.

This module provides the Deleted class that handles the 'deleted' Ansible state,
which removes VRF configurations from DCNM/NDFC.
"""
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Deleted(BaseState):
    """Handle deleted state for VRF resources."""

    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Delete VRF resources."""
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        deleted_vrfs = []
        errors = []

        for config in configs:
            if not config.vrf_name:
                # Delete all VRFs in fabric when vrf_name is empty
                self._delete_all_vrfs_in_fabric(config.fabric, deleted_vrfs, errors)
            else:
                # Delete specific VRF
                self._delete_specific_vrf(config, deleted_vrfs, errors)

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

        return self.result

    def _delete_specific_vrf(self, config: VrfConfig, deleted_vrfs: list[str], errors: list[str]) -> None:
        """Delete a specific VRF."""
        exists, _ = self._vrf_exists(config.fabric, config.vrf_name)

        if exists:
            success, response = self.api_client.delete_vrf(config.fabric, config.vrf_name)

            if success:
                deleted_vrfs.append(config.vrf_name)
                self.result.changed = True
                # Cache is automatically updated in VrfApi.delete_vrf()
            else:
                errors.append(f"Failed to delete VRF {config.vrf_name}: {response.get('error', 'Unknown error')}")
        # If VRF doesn't exist, no action needed (idempotent)

    def _delete_all_vrfs_in_fabric(self, fabric: str, deleted_vrfs: list[str], errors: list[str]) -> None:
        """Delete all VRFs in a fabric."""
        # Get all VRFs in the fabric
        all_vrfs = self._get_all_fabric_vrfs(fabric)

        if not all_vrfs:
            # No VRFs to delete in this fabric
            return

        for vrf_name in all_vrfs:
            success, response = self.api_client.delete_vrf(fabric, vrf_name)

            if success:
                deleted_vrfs.append(vrf_name)
                self.result.changed = True
                # Cache is automatically updated in VrfApi.delete_vrf()
            else:
                errors.append(f"Failed to delete VRF {vrf_name}: {response.get('error', 'Unknown error')}")
