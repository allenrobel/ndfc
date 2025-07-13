# MARK plugins/module_utils/vrf/models/vrf_config.py
"""
VrfConfig - Pydantic model to validate VRF playbook tasks.
"""
import json
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .vrf_payload import VrfPayload
from .template_models import VrfTemplateConfig, ServiceVrfTemplateConfig
from ..enums.vrf_templates import VrfTemplates


class VrfConfig(BaseModel):
    """Pydantic model for VRF configuration from Ansible playbook."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    fabric: str = Field(..., min_length=1, max_length=64)
    vrf_name: str = Field(..., min_length=0, max_length=32)
    vrf_id: int = Field(default=0)
    vrf_template: str = Field(default=VrfTemplates.DEFAULT_VRF_UNIVERSAL.value)
    vrf_template_config: VrfTemplateConfig = Field(default_factory=VrfTemplateConfig)
    vrf_extension_template: str = Field(default=VrfTemplates.DEFAULT_VRF_EXTENSION_UNIVERSAL.value)
    service_vrf_template: Optional[ServiceVrfTemplateConfig] = Field(default=None)
    deploy: bool = Field(default=True)

    def to_payload(self) -> VrfPayload:
        """Convert VrfConfig to VrfPayload for API calls."""
        payload_data = {
            "fabric": self.fabric,
            "vrfName": self.vrf_name,
            "vrfId": self.vrf_id,
            "vrfTemplate": self.vrf_template,
            "vrfTemplateConfig": json.dumps(self.vrf_template_config.model_dump(by_alias=True, exclude_none=True)),  # pylint: disable=no-member
            "vrfExtensionTemplate": self.vrf_extension_template,
            "source": None,
            "deploy": self.deploy,
        }

        if self.service_vrf_template:
            payload_data["serviceVrfTemplate"] = json.dumps(self.service_vrf_template.model_dump(by_alias=True, exclude_none=True))  # pylint: disable=no-member

        return VrfPayload.model_validate(payload_data)
