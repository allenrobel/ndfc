# MARK plugins/module_utils/vrf_attachment/states/state_factory.py
"""
State factory for VRF attachment state handlers.

This module provides the StateFactory class that creates appropriate state handlers
based on the requested Ansible state.
"""
from ...common.enums.ansible_states import AnsibleStates
from ..api.vrf_attachment_api import VrfAttachmentApi
from .base_state import BaseState
from .deleted import Deleted
from .merged import Merged
from .overridden import Overridden
from .query import Query
from .replaced import Replaced


class StateFactory:
    """Factory class for creating VRF attachment state handlers."""

    @staticmethod
    def create_state(state: AnsibleStates, api_client: VrfAttachmentApi) -> BaseState:
        """
        Create a state handler based on the requested state.
        
        Args:
            state: The Ansible state to handle
            api_client: The VRF attachment API client
            
        Returns:
            The appropriate state handler instance
            
        Raises:
            ValueError: If the state is not supported
        """
        state_handlers = {
            AnsibleStates.DELETED: Deleted,
            AnsibleStates.MERGED: Merged,
            AnsibleStates.OVERRIDDEN: Overridden,
            AnsibleStates.QUERY: Query,
            AnsibleStates.REPLACED: Replaced,
        }
        
        if state not in state_handlers:
            raise ValueError(f"Unsupported state: {state}")
            
        return state_handlers[state](api_client)