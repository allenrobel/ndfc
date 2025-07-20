# MARK plugins/module_utils/vrf/states/query_v2.py
"""
Query state handler for VRF resources with Pydantic model support.

This module provides the QueryV2 class that handles the 'query' Ansible state
using VrfApiV2 and VrfData models for type safety and consistent responses.
"""
from typing import List, Dict, Any
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from .base_state_v2 import BaseStateV2


class QueryV2(BaseStateV2):
    """Handle query state for VRF resources with Pydantic model support."""

    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """
        Query VRF resources using VrfApiV2.

        Returns consistent controller response format for all query operations.

        Args:
            configs: List of VRF configurations to query

        Returns:
            ModuleResult with consistent response format
        """
        queried_responses = []
        errors = []

        for config in configs:
            if config.vrf_name:
                # Query specific VRF - returns VrfControllerResponse
                success, controller_response = self.api_client.query_vrf(config.fabric, config.vrf_name)
                if success:
                    queried_responses.append(controller_response)
                else:
                    errors.append(f"Failed to query VRF {config.vrf_name} in fabric {config.fabric}: {controller_response.MESSAGE}")
            else:
                # Query all VRFs in fabric - returns VrfControllerResponse
                success, controller_response = self.api_client.query_all_vrfs(config.fabric)
                if success:
                    queried_responses.append(controller_response)
                else:
                    errors.append(f"Failed to query VRFs in fabric {config.fabric}: {controller_response.MESSAGE}")

        # Finalize result
        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            # Count total VRFs across all responses
            total_vrfs = sum(len(response.DATA) for response in queried_responses)
            self.result.msg = f"Queried {total_vrfs} VRFs"
            self.result.stdout = self.result.msg

            # Convert VrfControllerResponse models to dict format for module response
            self.result.response = self._convert_controller_responses_to_data_list(queried_responses)

        # Query never changes state
        self.result.changed = False

        return self.result
