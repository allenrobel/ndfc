# MARK plugins/module_utils/vrf_attachment/models/vrf_attachment_config.py
"""
VrfAttachmentConfig - Pydantic model to validate VRF attachment playbook tasks.
"""
import json
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .vrf_attachment_payload import VrfAttachmentPayload
from .instance_values import InstanceValues
from .extension_values import ExtensionValues


class LanAttachConfig(BaseModel):
    """Configuration for a single LAN attachment within a VRF attachment."""
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    
    # Switch identification (user provides IP, we'll translate to serialNumber)
    ip_address: str = Field(..., min_length=1, max_length=64)
    
    # VLAN configuration
    vlan_id: int = Field(..., ge=2, le=4094)
    
    # Deployment control
    deployment: bool = Field(default=False)
    
    # Extension values for VRF Lite configuration
    extension_values: Optional[ExtensionValues] = Field(default_factory=ExtensionValues)
    
    # Freeform configuration
    freeform_config: Optional[str] = Field(default="")
    
    # Instance values for advanced configuration
    instance_values: Optional[InstanceValues] = Field(default_factory=InstanceValues)


class VrfAttachmentConfig(BaseModel):
    """Pydantic model for VRF attachment configuration from Ansible playbook."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    # Fabric and VRF identification
    fabric: str = Field(..., min_length=1, max_length=64)
    vrf_name: str = Field(..., min_length=1, max_length=32)
    
    # List of LAN attachments
    lan_attach_list: List[LanAttachConfig] = Field(..., min_items=1)
    
    def to_payload(self) -> VrfAttachmentPayload:
        """Convert VrfAttachmentConfig to VrfAttachmentPayload for API calls."""
        lan_attach_list_data = []
        
        for lan_attach in self.lan_attach_list:
            # Prepare extension values as JSON string
            extension_values_json = ""
            if lan_attach.extension_values:
                extension_dict = lan_attach.extension_values.model_dump(by_alias=True, exclude_none=True)
                if extension_dict:
                    # Convert nested structures to JSON strings as required by NDFC
                    for key, value in extension_dict.items():
                        if isinstance(value, dict):
                            extension_dict[key] = json.dumps(value)
                    extension_values_json = json.dumps(extension_dict)
            
            # Prepare instance values as JSON string
            instance_values_json = ""
            if lan_attach.instance_values:
                instance_dict = lan_attach.instance_values.model_dump(by_alias=True, exclude_none=True)
                instance_values_json = json.dumps(instance_dict)
            
            lan_attach_data = {
                "fabric": self.fabric,
                "vrfName": self.vrf_name,
                "ipAddress": lan_attach.ip_address,  # Will be translated to serialNumber
                "vlanId": lan_attach.vlan_id,
                "deployment": lan_attach.deployment,
                "extensionValues": extension_values_json,
                "freeformConfig": lan_attach.freeform_config,
                "instanceValues": instance_values_json
            }
            lan_attach_list_data.append(lan_attach_data)
        
        payload_data = {
            "vrfName": self.vrf_name,
            "lanAttachList": lan_attach_list_data
        }

        return VrfAttachmentPayload.model_validate(payload_data)