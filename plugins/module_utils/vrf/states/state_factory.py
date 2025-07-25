# MARK plugins/module_utils/vrf/states/state_factory.py
"""
State factory for VRF operations with Pydantic model support.

This module provides the StateFactory class that creates appropriate state handlers
using VrfApiV2 and Pydantic models for type safety and consistent responses.
"""
from ...common.enums.ansible_states import AnsibleStates
from ..api.vrf_api_v2 import VrfApiV2
from .merged import Merged
from .deleted import Deleted
from .query import Query
from .replaced import Replaced
from .overridden import Overridden


class StateFactory:
    """
    Factory class for creating VRF state handlers with Pydantic model support.

    Creates appropriate state handler instances based on Ansible state,
    all using VrfApiV2 for type-safe operations with VrfData models.
    """

    # Mapping of Ansible states to their corresponding handler classes
    _STATE_CLASSES = {
        AnsibleStates.MERGED: Merged,
        AnsibleStates.DELETED: Deleted,
        AnsibleStates.QUERY: Query,
        AnsibleStates.REPLACED: Replaced,
        AnsibleStates.OVERRIDDEN: Overridden,
    }

    @classmethod
    def create_state(cls, state: AnsibleStates, api_client: VrfApiV2):
        """
        Create appropriate state handler for the given Ansible state.

        Args:
            state: The Ansible state to handle
            api_client: VrfApiV2 instance with Pydantic model support

        Returns:
            State handler instance configured for the specified state

        Raises:
            ValueError: If the state is not supported
        """
        state_class = cls._STATE_CLASSES.get(state)
        if not state_class:
            raise ValueError(f"Unsupported state: {state}")

        return state_class(api_client)

    @classmethod
    def get_supported_states(cls) -> list[AnsibleStates]:
        """
        Get list of supported Ansible states.

        Returns:
            List of supported AnsibleStates
        """
        return list(cls._STATE_CLASSES.keys())
