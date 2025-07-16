# MARK plugins/module_utils/vrf_attachment/models/state_configs.py
"""
State-specific VRF attachment configuration models.

This module provides Pydantic models tailored to each Ansible state's
specific validation requirements, allowing for precise field requirements
per operation type.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .vrf_attachment_config import VrfAttachmentConfig, LanAttachConfig
from .instance_values import InstanceValues
from .extension_values import ExtensionValues


class BaseVrfAttachmentConfig(BaseModel):
    """Base VRF attachment configuration with common settings."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="ignore")

    fabric: str = Field(..., min_length=1, max_length=64)
    vrf_name: str = Field(..., min_length=1, max_length=32)


class DeletedVrfAttachmentConfig(BaseVrfAttachmentConfig):
    """VRF attachment configuration model for deleted state."""

    # For deletion, we can specify specific attachments or delete all
    lan_attach_list: Optional[List[LanAttachConfig]] = Field(default=None)

    def to_vrf_attachment_config(self) -> VrfAttachmentConfig:
        """Convert to main VrfAttachmentConfig model with sensible defaults."""
        lan_attach_list = self.lan_attach_list or []
        
        return VrfAttachmentConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            lan_attach_list=lan_attach_list
        )


class QueryVrfAttachmentConfig(BaseVrfAttachmentConfig):
    """VRF attachment configuration model for query state."""

    # For query, we can optionally filter by specific attachments
    lan_attach_list: Optional[List[LanAttachConfig]] = Field(default=None)

    def to_vrf_attachment_config(self) -> VrfAttachmentConfig:
        """Convert to main VrfAttachmentConfig model with sensible defaults."""
        lan_attach_list = self.lan_attach_list or []
        
        return VrfAttachmentConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            lan_attach_list=lan_attach_list
        )


class MergedVrfAttachmentConfig(BaseVrfAttachmentConfig):
    """VRF attachment configuration model for merged state."""

    # For merged, lan_attach_list is required
    lan_attach_list: List[LanAttachConfig] = Field(..., min_items=1)

    def to_vrf_attachment_config(self) -> VrfAttachmentConfig:
        """Convert to main VrfAttachmentConfig model."""
        return VrfAttachmentConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            lan_attach_list=self.lan_attach_list
        )


class ReplacedVrfAttachmentConfig(BaseVrfAttachmentConfig):
    """VRF attachment configuration model for replaced state."""

    # For replaced, lan_attach_list is required
    lan_attach_list: List[LanAttachConfig] = Field(..., min_items=1)

    def to_vrf_attachment_config(self) -> VrfAttachmentConfig:
        """Convert to main VrfAttachmentConfig model."""
        return VrfAttachmentConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            lan_attach_list=self.lan_attach_list
        )


class OverriddenVrfAttachmentConfig(BaseVrfAttachmentConfig):
    """VRF attachment configuration model for overridden state."""

    # For overridden, lan_attach_list is required
    lan_attach_list: List[LanAttachConfig] = Field(..., min_items=1)

    def to_vrf_attachment_config(self) -> VrfAttachmentConfig:
        """Convert to main VrfAttachmentConfig model."""
        return VrfAttachmentConfig(
            fabric=self.fabric,
            vrf_name=self.vrf_name,
            lan_attach_list=self.lan_attach_list
        )