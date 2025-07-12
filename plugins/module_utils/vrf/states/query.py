# MARK plugins/module_utils/vrf/states/query.py
"""
Query state handler for VRF resources.

This module provides the Query class that handles the 'query' Ansible state,
which retrieves current VRF configurations from DCNM/NDFC.
"""
from typing import Any
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Query(BaseState):
    """Handle query state for VRF resources."""

    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Query VRF resources."""
        # Pre-populate cache for all fabrics to minimize API calls
        self._populate_all_fabric_caches(configs)

        queried_vrfs: list[dict[str, Any]] = []
        errors: list[str] = []

        for config in configs:
            exists, current_vrf = self._vrf_exists(config.fabric, config.vrf_name)

            if exists and current_vrf:
                queried_vrfs.append(current_vrf)
            # If VRF doesn't exist, we don't add it to the results

        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            self.result.msg = f"Queried {len(queried_vrfs)} VRFs"
            self.result.stdout = self.result.msg
            self.result.response = queried_vrfs

        # Query never changes state
        self.result.changed = False

        return self.result
