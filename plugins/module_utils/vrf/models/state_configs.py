# MARK plugins/module_utils/vrf/models/state_configs.py
"""
State-specific VRF configuration models.

This module provides Pydantic models tailored to each Ansible state's
specific validation requirements, allowing for precise field requirements
per operation type.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from ..enums.vrf_templates import VrfTemplates
from .vrf_config import VrfConfig
from .template_models import VrfTemplateConfig, ServiceVrfTemplateConfig


class BaseVrfConfig(BaseModel):
    """Base VRF configuration with common settings."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="ignore")

    fabric: str = Field(..., min_length=1, max_length=64)


class DeletedVrfConfig(BaseVrfConfig):
    """VRF configuration model for deleted state (fabric required, vrf_name optional)."""

    vrf_name: Optional[str] = Field(default=None, min_length=1, max_length=32)

    def to_vrf_config(self) -> VrfConfig:
        """Convert to main VrfConfig model with sensible defaults."""
        return VrfConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name or "",  # Empty string when deleting all VRFs in fabric
            vrf_id=0,  # Default for deleted operations
            vrf_template_config=VrfTemplateConfig(),  # Default empty config for deleted operations
        )


class QueryVrfConfig(BaseVrfConfig):
    """VRF configuration model for query state (fabric required, others optional for filtering)."""

    vrf_name: Optional[str] = Field(default=None, min_length=1, max_length=32)
    vrf_id: Optional[int] = Field(default=None)
    vrf_template: Optional[str] = Field(default=None)
    vrf_template_config: Optional[VrfTemplateConfig] = Field(default=None)
    vrf_extension_template: Optional[str] = Field(default=None)
    service_vrf_template: Optional[ServiceVrfTemplateConfig] = Field(default=None)

    def to_vrf_config(self) -> VrfConfig:
        """Convert to main VrfConfig model with sensible defaults."""
        return VrfConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name or "",  # Default empty for query operations
            vrf_id=self.vrf_id or 0,
            vrf_template=self.vrf_template or VrfTemplates.DEFAULT_VRF_UNIVERSAL.value,
            vrf_template_config=self.vrf_template_config or VrfTemplateConfig(),
            vrf_extension_template=self.vrf_extension_template or VrfTemplates.DEFAULT_VRF_EXTENSION_UNIVERSAL.value,
            service_vrf_template=self.service_vrf_template,
        )


class MergedVrfConfig(BaseVrfConfig):
    """VRF configuration model for merged state (vrf_id optional, auto-assigned by NDFC)."""

    vrf_name: str = Field(..., min_length=1, max_length=32)
    vrf_id: Optional[int] = Field(default=None)
    vrf_template: str = Field(default=VrfTemplates.DEFAULT_VRF_UNIVERSAL.value)
    vrf_template_config: VrfTemplateConfig = Field(...)
    vrf_extension_template: str = Field(default=VrfTemplates.DEFAULT_VRF_EXTENSION_UNIVERSAL.value)
    service_vrf_template: Optional[ServiceVrfTemplateConfig] = Field(default=None)

    def to_vrf_config(self) -> VrfConfig:
        """Convert to main VrfConfig model."""
        return VrfConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            vrf_id=self.vrf_id or 0,  # Will be auto-assigned by NDFC if 0
            vrf_template=self.vrf_template,
            vrf_template_config=self.vrf_template_config,
            vrf_extension_template=self.vrf_extension_template,
            service_vrf_template=self.service_vrf_template,
        )


class ReplacedVrfConfig(BaseVrfConfig):
    """VRF configuration model for replaced state (all fields required)."""

    vrf_name: str = Field(..., min_length=1, max_length=32)
    vrf_id: int = Field(...)
    vrf_template: str = Field(default=VrfTemplates.DEFAULT_VRF_UNIVERSAL.value)
    vrf_template_config: VrfTemplateConfig = Field(...)
    vrf_extension_template: str = Field(default=VrfTemplates.DEFAULT_VRF_EXTENSION_UNIVERSAL.value)
    service_vrf_template: Optional[ServiceVrfTemplateConfig] = Field(default=None)

    def to_vrf_config(self) -> VrfConfig:
        """Convert to main VrfConfig model."""
        return VrfConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            vrf_id=self.vrf_id,
            vrf_template=self.vrf_template,
            vrf_template_config=self.vrf_template_config,
            vrf_extension_template=self.vrf_extension_template,
            service_vrf_template=self.service_vrf_template,
        )


class OverriddenVrfConfig(ReplacedVrfConfig):
    """VRF configuration model for overridden state (same as replaced)."""
