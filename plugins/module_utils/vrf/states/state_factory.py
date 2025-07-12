# MARK plugins/module_utils/vrf/states/state_factory.py
"""
Factory class for creating VRF state handlers.

This module provides the StateFactory class that creates appropriate state handler
instances based on the requested Ansible state (merged, overridden, deleted, etc.).
"""
from typing import Type
from ...common.enums.ansible_states import AnsibleStates
from ..api.vrf_api import VrfApi
from .base_state import BaseState
from .deleted import Deleted
from .merged import Merged
from .overridden import Overridden
from .query import Query
from .replaced import Replaced


# pylint: disable=too-few-public-methods
class StateFactory:
    """Factory class to create state handlers."""

    _state_classes: dict[AnsibleStates, Type[BaseState]] = {
        AnsibleStates.DELETED: Deleted,
        AnsibleStates.MERGED: Merged,
        AnsibleStates.OVERRIDDEN: Overridden,
        AnsibleStates.QUERY: Query,
        AnsibleStates.REPLACED: Replaced,
    }

    @classmethod
    def create_state(cls, state: AnsibleStates, api_client: VrfApi) -> BaseState:
        """Create a state handler instance."""
        state_class = cls._state_classes.get(state)
        if not state_class:
            raise ValueError(f"Unsupported state: {state}")

        return state_class(api_client)
