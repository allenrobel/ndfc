# MARK plugins/module_utils/vrf/models/vrf_payload.py
"""
VrfPayload - Pydantic model to validate VRF payload.
"""
import json
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class VrfPayload(BaseModel):
    """Pydantic model for VRF payload validation."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    fabric: str = Field(..., min_length=1, max_length=64)
    vrf_name: str = Field(..., min_length=1, max_length=32, alias="vrfName")
    vrf_id: int = Field(..., alias="vrfId")
    vrf_template: str = Field(default="Default_VRF_Universal", alias="vrfTemplate")
    vrf_template_config: str = Field(..., alias="vrfTemplateConfig")
    vrf_extension_template: str = Field(default="Default_VRF_Extension_Universal", alias="vrfExtensionTemplate")
    service_vrf_template: Optional[str] = Field(default=None, alias="serviceVrfTemplate")
    source: Optional[str] = Field(default=None)
    deploy: bool = Field(default=True)

    @field_validator("vrf_template_config")
    @classmethod
    def validate_vrf_template_config(cls, v: str) -> str:
        """Validate that vrfTemplateConfig is valid JSON."""
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError as error:
            msg = "vrfTemplateConfig must be valid JSON string. "
            msg += f"Error detail: {error}"
            raise ValueError(msg) from error

    @field_validator("service_vrf_template")
    @classmethod
    def validate_service_vrf_template(cls, v: Optional[str]) -> Optional[str]:
        """Validate that serviceVrfTemplate is valid JSON if provided."""
        if v is not None:
            try:
                json.loads(v)
                return v
            except json.JSONDecodeError as error:
                msg = "serviceVrfTemplate must be valid JSON string. "
                msg += f"Error detail: {error}"
                raise ValueError("serviceVrfTemplate must be valid JSON string") from error
        return v
