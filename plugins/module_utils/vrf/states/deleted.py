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
