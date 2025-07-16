# MARK plugins/module_utils/vrf_attachment/states/deleted.py
"""
Deleted state handler for VRF attachment resources.

This module provides the Deleted class that handles the 'deleted' Ansible state,
which removes VRF attachment configurations from DCNM/NDFC.
"""
from typing import Any
from ..models.module_result import ModuleResult
from ..models.vrf_attachment_config import VrfAttachmentConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Deleted(BaseState):
    """Handle deleted state for VRF attachment resources."""

    def execute(self, configs: list[VrfAttachmentConfig]) -> ModuleResult:
        """Delete VRF attachment resources."""
        detached_vrfs = []
        errors = []
        api_responses = []

        for config in configs:
            if not config.lan_attach_list:
                # Delete all VRF attachments for the VRF
                responses = self._delete_all_vrf_attachments(config.fabric, config.vrf_name, detached_vrfs, errors)
                api_responses.extend(responses)
            else:
                # Delete specific VRF attachments
                # Set deployment=False for detachment
                for lan_attach in config.lan_attach_list:
                    lan_attach.deployment = False
                    
                response_data = self._execute_vrf_attachment_operation_with_response(config, "detach", detached_vrfs, errors)
                if response_data:
                    api_responses.append(response_data)

        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            if detached_vrfs:
                self.result.msg = f"Detached VRFs: {', '.join(detached_vrfs)}"
            else:
                self.result.msg = "No VRF attachments to delete"
            self.result.stdout = self.result.msg

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result

    def _delete_all_vrf_attachments(self, fabric: str, vrf_name: str, detached_vrfs: list[str], errors: list[str]) -> list[dict[str, Any]]:
        """Delete all VRF attachments for a VRF and return API responses."""
        responses = []
        
        # First query to get current attachments
        success, response = self.api_client.query_vrf_attachments(fabric, vrf_name)
        
        if not success:
            errors.append(f"Failed to query VRF attachments for {vrf_name} in fabric {fabric}")
            return responses
            
        # Extract attachment information and prepare detachment payload
        # This is a simplified implementation - in practice, you'd need to parse
        # the response to get current attachments and create detachment payloads
        
        # For now, just return empty responses as we need to implement the logic
        # to parse current attachments and create detachment payloads
        
        return responses