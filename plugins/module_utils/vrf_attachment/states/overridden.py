# MARK plugins/module_utils/vrf_attachment/states/overridden.py
"""
Overridden state handler for VRF attachment resources.

This module provides the Overridden class that handles the 'overridden' Ansible state,
which overrides all attachments for the specified VRF with the desired configuration.
"""
from typing import Any, Dict, List, Optional
from ..models.module_result import ModuleResult
from ..models.vrf_attachment_config import VrfAttachmentConfig, LanAttachConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Overridden(BaseState):
    """Handle overridden state for VRF attachment resources."""

    def execute(self, configs: list[VrfAttachmentConfig]) -> ModuleResult:
        """Override VRF attachment resources."""
        overridden_vrfs = []
        errors = []
        api_responses = []

        for config in configs:
            # For overridden state, implement full override logic:
            # 1. Query all current attachments for the specified VRF
            # 2. Detach ALL existing attachments for this VRF (not in desired config)
            # 3. Attach the desired configuration
            
            responses = self._override_vrf_attachments(config, overridden_vrfs, errors)
            if responses:
                api_responses.extend(responses)

        # Finalize result with API responses
        self._finalize_result(overridden_vrfs, [], [], errors)

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result

    def _override_vrf_attachments(self, config: VrfAttachmentConfig, overridden_vrfs: List[str], errors: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Override all attachments for a specific VRF."""
        responses = []
        
        try:
            # Step 1: Query all current attachments for this specific VRF
            current_attachments = self._get_current_vrf_attachments(config.fabric, config.vrf_name)
            
            # Step 2: Determine which attachments to detach (ALL not in desired config)
            attachments_to_detach = self._determine_vrf_attachments_to_detach(current_attachments, config)
            
            # Step 3: Detach ALL unwanted attachments for this VRF
            if attachments_to_detach:
                detach_responses = self._detach_vrf_attachments(config.fabric, config.vrf_name, attachments_to_detach, errors)
                if detach_responses:
                    responses.extend(detach_responses)
            
            # Step 4: Attach the desired configuration
            attach_response = self._execute_vrf_attachment_operation_with_response(config, "attach", overridden_vrfs, errors)
            if attach_response:
                responses.append(attach_response)
                
            return responses if responses else None
            
        except Exception as e:
            errors.append(f"Failed to override VRF attachments for {config.vrf_name}: {str(e)}")
            return None

    def _get_current_vrf_attachments(self, fabric: str, vrf_name: str) -> List[Dict[str, Any]]:
        """Get all current attachments for a specific VRF."""
        try:
            success, response = self.api_client.query_vrf_attachments(fabric, vrf_name)
            if success and response:
                # Extract attachment data from response
                data = response.get("DATA", [])
                if isinstance(data, list):
                    return data
                return []
            return []
        except Exception:
            # If query fails, assume no current attachments
            return []

    def _determine_vrf_attachments_to_detach(self, current_attachments: List[Dict[str, Any]], desired_config: VrfAttachmentConfig) -> List[Dict[str, Any]]:
        """Determine which attachments should be detached for this VRF."""
        attachments_to_detach = []
        
        # Convert desired config to set of IP addresses for comparison
        desired_ips = {attach.ip_address for attach in desired_config.lan_attach_list}
        
        # For overridden state, ALL current attachments not in desired config should be detached
        for current_attachment in current_attachments:
            current_ip = current_attachment.get("ipAddress")
            if current_ip and current_ip not in desired_ips:
                attachments_to_detach.append(current_attachment)
        
        return attachments_to_detach

    def _detach_vrf_attachments(self, fabric: str, vrf_name: str, attachments_to_detach: List[Dict[str, Any]], errors: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Detach unwanted attachments from the specified VRF."""
        responses = []
        
        for attachment in attachments_to_detach:
            try:
                # Create a minimal config for detachment
                detach_config = self._create_detach_config(fabric, vrf_name, attachment)
                
                # Execute detach operation
                response = self._execute_vrf_attachment_operation_with_response(detach_config, "detach", [], errors)
                if response:
                    responses.append(response)
                    
            except Exception as e:
                errors.append(f"Failed to detach attachment {attachment.get('ipAddress', 'unknown')} from VRF {vrf_name}: {str(e)}")
        
        return responses if responses else None

    def _create_detach_config(self, fabric: str, vrf_name: str, attachment: Dict[str, Any]) -> VrfAttachmentConfig:
        """Create a minimal VrfAttachmentConfig for detachment."""
        # Create a minimal LanAttachConfig for detachment
        lan_attach = LanAttachConfig(
            ip_address=attachment.get("ipAddress", ""),
            vlan_id=attachment.get("vlanId", 1),
            deployment=False  # Set to false for detachment
        )
        
        return VrfAttachmentConfig(
            fabric=fabric,
            vrf_name=vrf_name,
            lan_attach_list=[lan_attach]
        )