# MARK plugins/module_utils/vrf/models/module_result.py
"""
Module result model for VRF operations.

This module provides the ModuleResult Pydantic model for validating and structuring
the results returned by VRF modules.
"""
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class ModuleResult(BaseModel):
    """Pydantic model for module result validation."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")

    changed: bool = False
    failed: bool = False
    msg: str = ""
    stdout: str = ""
    stderr: str = ""
    response: Optional[list[dict[str, Any]]] = None
    diff: Optional[dict[str, Any]] = None
