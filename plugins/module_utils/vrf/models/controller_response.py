# MARK plugins/module_utils/vrf/models/controller_response.py
"""
Controller response models for consistent API response handling.

This module provides Pydantic models for standardizing all controller responses
with consistent DATA field format and metadata fields.
"""
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ControllerResponse(BaseModel):
    """
    Base Pydantic model for all controller responses.

    Ensures consistent response format with DATA field always as list of dict,
    plus standard controller metadata fields.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    # Standard controller response fields
    DATA: List[dict[str, Any]] = Field(default_factory=list, description="Response data as list of dictionaries (consistent format)")
    MESSAGE: str = Field(default="OK", description="Controller response message")
    METHOD: str = Field(description="HTTP method used for the request")
    REQUEST_PATH: str = Field(description="Full URL path for the request")
    RETURN_CODE: int = Field(description="HTTP return code from controller")

    # Optional fields for Results class compatibility
    sequence_number: Optional[int] = Field(default=None, description="Sequence number for tracking multiple operations")


class VrfControllerResponse(ControllerResponse):
    """
    VRF-specific controller response model.

    Extends base ControllerResponse with VRF-specific validation
    and ensures DATA field contains VRF data dictionaries.
    """

    # Override DATA field with more specific typing for VRF responses
    DATA: List[dict[str, Any]] = Field(default_factory=list, description="List of VRF data dictionaries")

    def get_vrf_data(self) -> List[dict[str, Any]]:
        """
        Get VRF data from response.

        Returns:
            List of VRF data dictionaries from DATA field
        """
        return self.DATA

    def is_empty_response(self) -> bool:
        """
        Check if this is an empty response (e.g., from delete operations).

        Returns:
            True if DATA contains only empty dictionaries
        """
        return all(not data for data in self.DATA)

    def get_vrf_count(self) -> int:
        """
        Get count of VRFs in response.

        Returns:
            Number of VRF records in DATA field
        """
        return len([data for data in self.DATA if data])
