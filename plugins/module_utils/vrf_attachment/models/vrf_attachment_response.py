# MARK plugins/module_utils/vrf_attachment/models/vrf_attachment_response.py
"""
VrfAttachmentResponse - Pydantic model for VRF attachment API responses.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class VrfAttachmentResponse(BaseModel):
    """Pydantic model for VRF attachment API response validation."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")

    # Standard controller response fields
    data: Dict[str, str] = Field(..., alias="DATA")
    message: str = Field(..., alias="MESSAGE")
    method: str = Field(..., alias="METHOD")
    request_path: str = Field(..., alias="REQUEST_PATH")
    return_code: int = Field(..., alias="RETURN_CODE")
    
    # The DATA field contains attachment results in format:
    # "vrf-name-[serial-number/switch-name]": "SUCCESS" or error message