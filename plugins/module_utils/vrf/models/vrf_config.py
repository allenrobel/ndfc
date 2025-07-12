# MARK plugins/module_utils/vrf/models/vrf_config.py
"""
VrfConfig - Pydantic model to validate VRF playbook tasks.
"""
import json
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from .vrf_payload import VrfPayload
from ..enums.vrf_templates import VrfTemplates


class VrfConfig(BaseModel):
    """Pydantic model for VRF configuration from Ansible playbook."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    fabric: str = Field(..., min_length=1, max_length=64)
    vrf_name: str = Field(..., min_length=1, max_length=32)
    vrf_id: int
    vrf_template: str = Field(default=VrfTemplates.DEFAULT_VRF_UNIVERSAL.value)
    vrf_template_config: dict[str, Any] = Field(...)
    vrf_extension_template: str = Field(default=VrfTemplates.DEFAULT_VRF_EXTENSION_UNIVERSAL.value)
    service_vrf_template: Optional[dict[str, Any]] = Field(default=None)

    def to_payload(self) -> VrfPayload:
        """Convert VrfConfig to VrfPayload for API calls."""
        payload_data = {
            "fabric": self.fabric,
            "vrfName": self.vrf_name,
            "vrfId": self.vrf_id,
            "vrfTemplate": self.vrf_template,
            "vrfTemplateConfig": json.dumps(self.vrf_template_config),
            "vrfExtensionTemplate": self.vrf_extension_template,
            "source": None,
        }

        if self.service_vrf_template:
            payload_data["serviceVrfTemplate"] = json.dumps(self.service_vrf_template)

        return VrfPayload.model_validate(payload_data)
