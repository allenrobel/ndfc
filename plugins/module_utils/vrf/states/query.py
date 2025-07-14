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
                # Query specific VRF - get full controller response
                success, response = self.api_client.query_vrf(config.fabric, config.vrf_name)
                if success and response:
                    # Add the full controller response directly
                    queried_vrfs.append(response)
                elif not success:
                    errors.append(f"Failed to query VRF {config.vrf_name} in fabric {config.fabric}")
                # If VRF doesn't exist, we don't add it to the results
            else:
                # Query all VRFs in fabric - get full controller response
                success, response = self.api_client.query_all_vrfs(config.fabric)
                if success and response:
                    # The response should contain the full controller response with DATA field
                    # DATA field contains the list of VRFs or single VRF
                    data_field = response.get("DATA", [])
                    if isinstance(data_field, list):
                        # Multiple VRFs - create individual responses for each VRF
                        for vrf_data in data_field:
                            if vrf_data and vrf_data.get("vrfName"):
                                individual_response = {
                                    "DATA": vrf_data,
                                    "MESSAGE": response.get("MESSAGE", "OK"),
                                    "METHOD": response.get("METHOD", "GET"),
                                    "REQUEST_PATH": response.get("REQUEST_PATH", ""),
                                    "RETURN_CODE": response.get("RETURN_CODE", 200)
                                }
                                queried_vrfs.append(individual_response)
                    elif isinstance(data_field, dict) and data_field.get("vrfName"):
                        # Single VRF - add the full response
                        queried_vrfs.append(response)
                elif not success:
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
