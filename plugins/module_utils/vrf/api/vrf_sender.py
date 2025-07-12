# MARK plugins/module_utils/vrf/api/vrf_sender.py
"""
VRF sender class for API operations.

This module provides the VrfSender class that handles HTTP communications
with DCNM/NDFC for VRF operations.
"""
from ansible.module_utils.basic import AnsibleModule
from ...common.classes.sender_dcnm import Sender


class VrfSender(Sender):
    """Sender class for VRF operations using DCNM sender."""

    def __init__(self, ansible_module: AnsibleModule):
        super().__init__()
        self.ansible_module = ansible_module
