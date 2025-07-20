# MARK plugins/module_utils/vrf/models/vrf_data.py
"""
VRF data model for internal business logic.

This module provides the VrfData Pydantic model for handling VRF data
throughout the application with proper field validation and transformations.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class VrfData(BaseModel):
    """
    Comprehensive Pydantic model for VRF data.

    This model represents VRF data as it appears in controller responses,
    with proper field aliasing and validation. Used internally throughout
    the VRF module for type-safe operations.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",  # Allow extra fields from controller
        populate_by_name=True,  # Allow both field names and aliases
    )

    # Core VRF identification fields
    fabric: Optional[str] = None
    vrf_name: Optional[str] = Field(default=None, alias="vrfName")
    vrf_id: Optional[int] = Field(default=None, alias="vrfId")

    # Template and configuration fields
    vrf_template: Optional[str] = Field(default=None, alias="vrfTemplate")
    vrf_template_config: Optional[str] = Field(default=None, alias="vrfTemplateConfig")
    vrf_extension_template: Optional[str] = Field(default=None, alias="vrfExtensionTemplate")
    service_vrf_template: Optional[str] = Field(default=None, alias="serviceVrfTemplate")

    # Status and metadata fields
    vrf_status: Optional[str] = Field(default=None, alias="vrfStatus")
    source: Optional[str] = None
    tenant_name: Optional[str] = Field(default=None, alias="tenantName")
    hierarchical_key: Optional[str] = Field(default=None, alias="hierarchicalKey")

    # Database/system fields
    id: Optional[int] = None
    default_sg_tag: Optional[str] = Field(default=None, alias="defaultSGTag")
    enforce: Optional[Any] = None  # Can be bool, string, or null

    # Lifecycle tracking
    deployment_status: Optional[str] = Field(default=None, alias="deploymentStatus")
    created_on: Optional[str] = Field(default=None, alias="createdOn")
    modified_on: Optional[str] = Field(default=None, alias="modifiedOn")

    @property
    def display_name(self) -> str:
        """Get display name for logging and messages."""
        return self.vrf_name or "Unknown VRF"

    @property
    def is_deployed(self) -> bool:
        """Check if VRF is deployed based on status."""
        return self.vrf_status not in [None, "NA", "NOT_DEPLOYED"]

    def to_cache_key(self, fabric: str) -> str:
        """Generate cache key for this VRF."""
        return f"{fabric}:{self.vrf_name}"

    def to_controller_format(self) -> dict[str, Any]:
        """
        Convert to controller format for API requests.

        Returns:
            Dictionary with controller field names (aliases)
        """
        return self.model_dump(by_alias=True, exclude_none=True)

    def get_field_value(self, field_name: str) -> Any:
        """
        Get field value by either internal name or alias.

        Args:
            field_name: Field name or alias to retrieve

        Returns:
            Field value or None if not found
        """
        # Try direct field access first
        if hasattr(self, field_name):
            return getattr(self, field_name)

        # Try by alias mapping
        field_mapping = {
            "vrfName": "vrf_name",
            "vrfId": "vrf_id",
            "vrfTemplate": "vrf_template",
            "vrfTemplateConfig": "vrf_template_config",
            "vrfExtensionTemplate": "vrf_extension_template",
            "serviceVrfTemplate": "service_vrf_template",
            "vrfStatus": "vrf_status",
            "tenantName": "tenant_name",
            "hierarchicalKey": "hierarchical_key",
            "defaultSGTag": "default_sg_tag",
            "deploymentStatus": "deployment_status",
            "createdOn": "created_on",
            "modifiedOn": "modified_on",
        }

        internal_name = field_mapping.get(field_name)
        if internal_name and hasattr(self, internal_name):
            return getattr(self, internal_name)

        return None
