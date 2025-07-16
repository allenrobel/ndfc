# MARK plugins/module_utils/vrf_attachment/states/merged.py
"""
Merged state handler for VRF attachment resources.

This module provides the Merged class that handles the 'merged' Ansible state,
which creates new VRF attachments and updates existing ones to match the desired configuration.
"""
from ..models.module_result import ModuleResult
from ..models.vrf_attachment_config import VrfAttachmentConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Merged(BaseState):
    """Handle merged state for VRF attachment resources."""

    def execute(self, configs: list[VrfAttachmentConfig]) -> ModuleResult:
        """Merge VRF attachment resources."""
        attached_vrfs = []
        errors = []
        api_responses = []

        for config in configs:
            # For merged state, we always try to attach
            # The controller will handle idempotency
            response_data = self._execute_vrf_attachment_operation_with_response(config, "attach", attached_vrfs, errors)
            if response_data:
                api_responses.append(response_data)

        # Finalize result with API responses
        self._finalize_result(attached_vrfs, [], [], errors)

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result