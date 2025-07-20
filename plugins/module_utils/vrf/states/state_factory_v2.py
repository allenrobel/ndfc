# MARK plugins/module_utils/vrf/states/state_factory_v2.py
"""
State factory for VRF operations with Pydantic model support.

This module provides the StateFactoryV2 class that creates appropriate state handlers
using VrfApiV2 and Pydantic models for type safety and consistent responses.
"""
from ...common.enums.ansible_states import AnsibleStates
from ..api.vrf_api_v2 import VrfApiV2
from .merged_v2 import MergedV2
from .deleted_v2 import DeletedV2
from .query_v2 import QueryV2
from .replaced_v2 import ReplacedV2
from .overridden_v2 import OverriddenV2


class StateFactoryV2:
    """
    Factory class for creating VRF state handlers with Pydantic model support.

    Creates appropriate state handler instances based on Ansible state,
    all using VrfApiV2 for type-safe operations with VrfData models.
    """

    # Mapping of Ansible states to their corresponding V2 handler classes
    _STATE_CLASSES = {
        AnsibleStates.MERGED: MergedV2,
        AnsibleStates.DELETED: DeletedV2,
        AnsibleStates.QUERY: QueryV2,
        AnsibleStates.REPLACED: ReplacedV2,
        AnsibleStates.OVERRIDDEN: OverriddenV2,
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
