# MARK plugins/module_utils/vrf/models/template_models.py
"""
Pydantic models for VRF template configurations.

This module provides structured models for VRF template configurations,
allowing us to work with type-safe objects throughout the business logic
instead of raw dictionaries or JSON strings.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class VrfTemplateConfig(BaseModel):
    """Pydantic model for VRF template configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")

    # Common VRF template fields - using extra="allow" to support dynamic fields
    vrf_segment_id: Optional[int] = Field(default=None, alias="vrfSegmentId")
    vrf_vlan_id: Optional[int] = Field(default=None, alias="vrfVlanId")
    mtu: Optional[int] = Field(default=None)

    # Allow any additional fields that may be present in templates
    # This is necessary because VRF templates can have many dynamic fields


class ServiceVrfTemplateConfig(BaseModel):
    """Pydantic model for Service VRF template configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")

    # Service VRF template fields - using extra="allow" for flexibility
    # Add specific fields as they are identified
