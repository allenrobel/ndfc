# MARK plugins/module_utils/vrf/states/merged.py
"""
Merged state handler for VRF resources.

This module provides the Merged class that handles the 'merged' Ansible state,
which creates new VRFs and updates existing ones to match the desired configuration.
"""
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Merged(BaseState):
    """Handle merged state for VRF resources."""

    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Merge VRF resources."""
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        created_vrfs = []
        updated_vrfs = []
        errors = []

        for config in configs:
            exists, current_vrf = self._vrf_exists(config.fabric, config.vrf_name)
            if current_vrf is None:
                current_vrf = {}

            if exists:
                # Update if different
                if not self._vrfs_equal(current_vrf, config):
                    self._execute_vrf_operation(config, "update", created_vrfs, updated_vrfs, errors)
                # If VRF exists and is identical, no action needed (idempotent)
            else:
                # Create new VRF
                self._execute_vrf_operation(config, "create", created_vrfs, updated_vrfs, errors)

        # Finalize result
        self._finalize_result(created_vrfs, updated_vrfs, [], errors)

        return self.result
