# MARK plugins/module_utils/vrf/models/__init__.py
"""
VRF models package.

Exports all VRF-related Pydantic models for internal use.
"""

from .controller_response import ControllerResponse, VrfControllerResponse
from .vrf_data import VrfData
from .response_builder import VrfResponseBuilder
from .module_result import ModuleResult
from .vrf_config import VrfConfig
from .vrf_payload import VrfPayload

# Re-export legacy model for backward compatibility during transition
from .vrf_response import VrfResponse

__all__ = [
    "ControllerResponse",
    "VrfControllerResponse", 
    "VrfData",
    "VrfResponseBuilder",
    "ModuleResult",
    "VrfConfig",
    "VrfPayload",
    "VrfResponse",  # Legacy - will be deprecated
]