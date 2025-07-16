# MARK plugins/module_utils/vrf_attachment/states/query.py
"""
Query state handler for VRF attachment resources.

This module provides the Query class that handles the 'query' Ansible state,
which retrieves current VRF attachment configurations from DCNM/NDFC.
"""
from typing import Any
from ..models.module_result import ModuleResult
from ..models.vrf_attachment_config import VrfAttachmentConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Query(BaseState):
    """Handle query state for VRF attachment resources."""

    def execute(self, configs: list[VrfAttachmentConfig]) -> ModuleResult:
        """Query VRF attachment resources."""
        queried_attachments: list[dict[str, Any]] = []
        errors: list[str] = []

        for config in configs:
            if config.lan_attach_list:
                # Query specific VRF attachments (not commonly used)
                success, response = self.api_client.query_vrf_attachments(config.fabric, config.vrf_name)
                if success and response:
                    queried_attachments.append(response)
                elif not success:
                    errors.append(f"Failed to query VRF attachments for {config.vrf_name} in fabric {config.fabric}")
            else:
                # Query all VRF attachments for the VRF
                success, response = self.api_client.query_vrf_attachments(config.fabric, config.vrf_name)
                if success and response:
                    queried_attachments.append(response)
                elif not success:
                    errors.append(f"Failed to query VRF attachments for {config.vrf_name} in fabric {config.fabric}")

        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            self.result.msg = f"Queried {len(queried_attachments)} VRF attachments"
            self.result.stdout = self.result.msg
            self.result.response = queried_attachments

        # Query never changes state
        self.result.changed = False

        return self.result