# MARK plugins/module_utils/vrf/enums/vrf_templates.py
"""
VRF Template enumerations.

This module contains enumerations for VRF templates used in DCNM/NDFC.
"""
from enum import Enum


class VrfTemplates(str, Enum):
    """VRF templates supported by NDFC."""

    DEFAULT_VRF_UNIVERSAL = "Default_VRF_Universal"
    DEFAULT_VRF_EXTENSION_UNIVERSAL = "Default_VRF_Extension_Universal"
