# MARK plugins/module_utils/vrf_attachment/states/base_state.py
"""
Base state class for VRF attachment state handlers.

This module provides the BaseState abstract base class that defines common functionality
for all VRF attachment state operations including API response handling and result building.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from ..models.module_result import ModuleResult
from ..models.vrf_attachment_config import VrfAttachmentConfig
from ..api.vrf_attachment_api import VrfAttachmentApi


# pylint: disable=too-few-public-methods
class BaseState(ABC):
    """Base class for all VRF attachment states."""

    def __init__(self, api_client: VrfAttachmentApi):
        self.api_client = api_client
        self.result = ModuleResult()

    @abstractmethod
    def execute(self, configs: list[VrfAttachmentConfig]) -> ModuleResult:
        """Execute the state operation."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _handle_api_response(self, success: bool, response: dict[str, Any], vrf_name: str, operation: str, success_list: list[str], errors: list[str]) -> bool:
        """
        Handle API response with consistent error handling.

        Args:
            success: Whether the API call succeeded
            response: API response data
            vrf_name: Name of the VRF being operated on
            operation: Operation type (attach, detach, query)
            success_list: List to append successful VRF names to
            errors: List to append error messages to

        Returns:
            True if operation succeeded, False otherwise
        """
        if success:
            success_list.append(vrf_name)
            self.result.changed = True
            return True

        errors.append(f"Failed to {operation} VRF {vrf_name}: {response.get('error', 'Unknown error')}")
        return False

    def _build_result_message(self, attached_vrfs: list[str], detached_vrfs: list[str], queried_vrfs: Optional[list[str]] = None) -> str:
        """
        Build result message from operation lists.

        Args:
            attached_vrfs: List of attached VRF names
            detached_vrfs: List of detached VRF names
            queried_vrfs: List of queried VRF names (optional)

        Returns:
            Formatted result message
        """
        messages = []
        if detached_vrfs:
            messages.append(f"Detached VRFs: {', '.join(detached_vrfs)}")
        if attached_vrfs:
            messages.append(f"Attached VRFs: {', '.join(attached_vrfs)}")
        if queried_vrfs:
            messages.append(f"Queried {len(queried_vrfs)} VRF attachments")
        if not messages:
            messages.append("No changes needed")

        return "; ".join(messages)

    def _finalize_result(self, attached_vrfs: list[str], detached_vrfs: list[str], queried_vrfs: list[str], errors: list[str]) -> None:
        """
        Finalize the module result with appropriate messages.

        Args:
            attached_vrfs: List of attached VRF names
            detached_vrfs: List of detached VRF names
            queried_vrfs: List of queried VRF names
            errors: List of error messages
        """
        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            self.result.msg = self._build_result_message(attached_vrfs, detached_vrfs, queried_vrfs)
            self.result.stdout = self.result.msg

    def _execute_vrf_attachment_operation_with_response(
        self, config: VrfAttachmentConfig, operation_type: str, success_list: list[str], errors: list[str]
    ) -> Optional[dict[str, Any]]:
        """
        Execute attach or detach operation for a VRF attachment and return the API response.

        Args:
            config: VRF attachment configuration
            operation_type: 'attach' or 'detach'
            success_list: List to append successful VRF names to
            errors: List to append error messages to

        Returns:
            API response data if successful, None if failed
        """
        payload = config.to_payload()
        
        if operation_type == "attach":
            success, response = self.api_client.attach_vrf(config.fabric, payload)
            if self._handle_api_response(success, response, config.vrf_name, "attach", success_list, errors):
                return response
        elif operation_type == "detach":
            success, response = self.api_client.detach_vrf(config.fabric, config.vrf_name, payload)
            if self._handle_api_response(success, response, config.vrf_name, "detach", success_list, errors):
                return response
        
        return None