# MARK plugins/module_utils/vrf_attachment/states/replaced.py
"""
Replaced state handler for VRF attachment resources.

This module provides the Replaced class that handles the 'replaced' Ansible state,
which replaces existing VRF attachments with the desired configuration.
"""
from typing import Any, Dict, List, Optional, Set
from ..models.module_result import ModuleResult
from ..models.vrf_attachment_config import VrfAttachmentConfig, LanAttachConfig
from .base_state import BaseState


# pylint: disable=too-few-public-methods
class Replaced(BaseState):
    """Handle replaced state for VRF attachment resources."""

    def execute(self, configs: list[VrfAttachmentConfig]) -> ModuleResult:
        """Replace VRF attachment resources."""
        replaced_vrfs = []
        errors = []
        api_responses = []

        for config in configs:
            # For replaced state, implement full replace logic:
            # 1. Query current attachments
            # 2. Detach existing attachments not in the desired config
            # 3. Attach the desired configuration
            
            responses = self._replace_vrf_attachments(config, replaced_vrfs, errors)
            if responses:
                api_responses.extend(responses)

        # Finalize result with API responses
        self._finalize_result(replaced_vrfs, [], [], errors)

        # Set response data for successful operations
        if api_responses:
            self.result.response = api_responses

        return self.result

    def _replace_vrf_attachments(self, config: VrfAttachmentConfig, replaced_vrfs: List[str], errors: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Replace VRF attachments by detaching unwanted and attaching desired."""
        responses = []
        
        try:
            # Step 1: Query current attachments
            current_attachments = self._get_current_attachments(config.fabric, config.vrf_name)
            
            # Step 2: Determine which attachments to detach
            attachments_to_detach = self._determine_attachments_to_detach(current_attachments, config)
            
            # Step 3: Detach unwanted attachments
            if attachments_to_detach:
                detach_responses = self._detach_unwanted_attachments(config.fabric, config.vrf_name, attachments_to_detach, errors)
                if detach_responses:
                    responses.extend(detach_responses)
            
            # Step 4: Attach desired configuration
            attach_response = self._execute_vrf_attachment_operation_with_response(config, "attach", replaced_vrfs, errors)
            if attach_response:
                responses.append(attach_response)
                
            return responses if responses else None
            
        except Exception as e:
            errors.append(f"Failed to replace VRF attachments for {config.vrf_name}: {str(e)}")
            return None

    def _get_current_attachments(self, fabric: str, vrf_name: str) -> List[Dict[str, Any]]:
        """Get current VRF attachments from the controller."""
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

    def _determine_attachments_to_detach(self, current_attachments: List[Dict[str, Any]], desired_config: VrfAttachmentConfig) -> List[Dict[str, Any]]:
        """Determine which current attachments should be detached."""
        attachments_to_detach = []
        
        # Convert desired config to set of IP addresses for comparison
        desired_ips = {attach.ip_address for attach in desired_config.lan_attach_list}
        
        for current_attachment in current_attachments:
            # Check if this attachment should be kept
            current_ip = current_attachment.get("ipAddress")
            if current_ip and current_ip not in desired_ips:
                attachments_to_detach.append(current_attachment)
            elif current_ip and current_ip in desired_ips:
                # Check if properties differ and needs replacement
                if self._attachment_needs_replacement(current_attachment, desired_config):
                    attachments_to_detach.append(current_attachment)
        
        return attachments_to_detach

    def _attachment_needs_replacement(self, current_attachment: Dict[str, Any], desired_config: VrfAttachmentConfig) -> bool:
        """Check if an attachment needs replacement due to property differences."""
        current_ip = current_attachment.get("ipAddress")
        if not current_ip:
            return False
        
        # Find the corresponding desired attachment
        desired_attachment = None
        for attach in desired_config.lan_attach_list:
            if attach.ip_address == current_ip:
                desired_attachment = attach
                break
        
        if not desired_attachment:
            return False
        
        # Compare key properties
        return (
            current_attachment.get("vlanId") != desired_attachment.vlan_id or
            current_attachment.get("deployment") != desired_attachment.deployment or
            # Add more property comparisons as needed
            self._extension_values_differ(current_attachment, desired_attachment)
        )

    def _extension_values_differ(self, current: Dict[str, Any], desired: LanAttachConfig) -> bool:
        """Compare extension values between current and desired attachment."""
        # This is a simplified comparison - in production, you'd want more thorough comparison
        current_ext = current.get("extensionValues", "")
        desired_ext = ""
        
        if desired.extension_values:
            # Convert desired extension values to JSON string format
            import json
            ext_dict = desired.extension_values.model_dump(by_alias=True, exclude_none=True)
            if ext_dict:
                for key, value in ext_dict.items():
                    if isinstance(value, dict):
                        ext_dict[key] = json.dumps(value)
                desired_ext = json.dumps(ext_dict)
        
        return current_ext != desired_ext

    def _detach_unwanted_attachments(self, fabric: str, vrf_name: str, attachments_to_detach: List[Dict[str, Any]], errors: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Detach unwanted attachments."""
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
                errors.append(f"Failed to detach attachment {attachment.get('ipAddress', 'unknown')}: {str(e)}")
        
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