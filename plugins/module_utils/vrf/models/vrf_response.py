# MARK plugins/module_utils/vrf/models/vrf_response.py
"""
VRF response model for API responses.

This module provides the VrfResponse Pydantic model for validating and structuring
VRF data received from DCNM/NDFC API responses.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VrfResponse(BaseModel):
    """Pydantic model for VRF response validation."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")  # Allow extra fields from API response

    fabric: Optional[str] = None
    vrf_name: Optional[str] = Field(default=None, alias="vrfName")
    vrf_id: Optional[int] = Field(default=None, alias="vrfId")
    vrf_template: Optional[str] = Field(default=None, alias="vrfTemplate")
    vrf_template_config: Optional[str] = Field(default=None, alias="vrfTemplateConfig")
    vrf_extension_template: Optional[str] = Field(default=None, alias="vrfExtensionTemplate")
    service_vrf_template: Optional[str] = Field(default=None, alias="serviceVrfTemplate")
    source: Optional[str] = None

    # Additional fields that might be present in response
    deployment_status: Optional[str] = Field(default=None, alias="deploymentStatus")
    created_on: Optional[str] = Field(default=None, alias="createdOn")
    modified_on: Optional[str] = Field(default=None, alias="modifiedOn")
