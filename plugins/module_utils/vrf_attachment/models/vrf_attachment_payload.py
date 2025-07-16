# MARK plugins/module_utils/vrf_attachment/models/vrf_attachment_payload.py
"""
VrfAttachmentPayload - Pydantic model for VRF attachment API payloads.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class LanAttachPayload(BaseModel):
    """Pydantic model for a single LAN attachment in the API payload."""
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    
    fabric: str = Field(..., min_length=1, max_length=64)
    vrf_name: str = Field(..., min_length=1, max_length=32, alias="vrfName")
    serial_number: str = Field(..., min_length=1, alias="serialNumber")
    vlan_id: int = Field(..., ge=2, le=4094, alias="vlanId")
    deployment: bool = Field(default=False)
    extension_values: str = Field(default="", alias="extensionValues")
    freeform_config: str = Field(default="", alias="freeformConfig")
    instance_values: str = Field(default="", alias="instanceValues")


class VrfAttachmentPayload(BaseModel):
    """Pydantic model for VRF attachment API payload."""
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    
    vrf_name: str = Field(..., min_length=1, max_length=32, alias="vrfName")
    lan_attach_list: List[LanAttachPayload] = Field(..., min_items=1, alias="lanAttachList")