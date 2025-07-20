# MARK plugins/module_utils/vrf_attachment/models/module_result.py
"""
ModuleResult - Pydantic model for Ansible module results.
"""
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ModuleResult(BaseModel):
    """Pydantic model for VRF attachment module results."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    changed: bool = Field(default=False)
    failed: bool = Field(default=False)
    msg: str = Field(default="")
    stdout: str = Field(default="")
    stderr: str = Field(default="")
    stdout_lines: List[str] = Field(default_factory=list)
    stderr_lines: List[str] = Field(default_factory=list)
    response: Optional[List[dict[str, Any]]] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to set stdout_lines and stderr_lines."""
        if self.stdout:
            self.stdout_lines = self.stdout.splitlines()  # pylint: disable=no-member
        if self.stderr:
            self.stderr_lines = self.stderr.splitlines()  # pylint: disable=no-member
