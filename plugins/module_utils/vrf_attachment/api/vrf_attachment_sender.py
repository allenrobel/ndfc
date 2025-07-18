# MARK plugins/module_utils/vrf_attachment/api/vrf_attachment_sender.py
"""
VRF attachment sender for API operations.

This module provides the VrfAttachmentSender class that handles HTTP request
transmission for VRF attachment operations.
"""
from ansible.module_utils.basic import AnsibleModule
from ...common.classes.sender_nd import Sender


class VrfAttachmentSender(Sender):
    """Sender for VRF attachment operations."""

    def __init__(self, ansible_module: AnsibleModule):
        super().__init__(ansible_module)
        self.class_name = self.__class__.__name__