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
        queried_vrfs: list[dict[str, Any]] = []
        errors: list[str] = []

        for config in configs:
            if config.vrf_name:
                # Query specific VRF - get array of VRF data (includes vrfStatus)
                success, vrf_array = self.api_client.query_vrf(config.fabric, config.vrf_name)
                if success:
                    queried_vrfs.extend(vrf_array)
                else:
                    errors.append(f"Failed to query VRF {config.vrf_name} in fabric {config.fabric}")
            else:
                # Query all VRFs in fabric - get array of VRF data (includes vrfStatus)
                success, vrf_array = self.api_client.query_all_vrfs(config.fabric)
                if success:
                    queried_vrfs.extend(vrf_array)
                else:
                    errors.append(f"Failed to query VRFs in fabric {config.fabric}")

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
