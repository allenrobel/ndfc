# MARK plugins/module_utils/vrf/states/base_state.py
"""
Base state class for VRF state handlers.

This module provides the BaseState abstract base class that defines common functionality
for all VRF state operations including caching, API response handling, and result building.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from ..api.vrf_api import VrfApi


# pylint: disable=too-few-public-methods
class BaseState(ABC):
    """Base class for all VRF states using generic caching."""

    def __init__(self, api_client: VrfApi):
        self.api_client = api_client
        self.result = ModuleResult()

    @abstractmethod
    def execute(self, configs: list[VrfConfig]) -> ModuleResult:
        """Execute the state operation."""

    def _populate_all_fabric_caches(self, configs: list[VrfConfig]) -> None:
        """
        Pre-populate cache for all fabrics mentioned in configs.
        This method makes one API call per fabric to cache all VRFs.
        """
        fabrics = set(config.fabric for config in configs)
        for fabric in fabrics:
            # This will cache all VRFs for the fabric
            self.api_client.get_all_cached(fabric)

    def _vrf_exists(self, fabric: str, vrf_name: str) -> tuple[bool, Optional[dict[str, Any]]]:
        """
        Check if VRF exists using generic cache.

        Args:
            fabric: The fabric name
            vrf_name: The VRF name

        Returns:
            Tuple of (exists, vrf_data)
        """
        return self.api_client.exists_cached(fabric, vrf_name)

    def _get_all_fabric_vrfs(self, fabric: str) -> dict[str, dict[str, Any]]:
        """
        Get all VRFs for a fabric using generic cache.

        Args:
            fabric: The fabric name

        Returns:
            Dictionary mapping VRF names to VRF data
        """
        return self.api_client.get_all_cached(fabric)

    def _vrfs_equal(self, current: dict[str, Any], desired: VrfConfig) -> bool:
        """Compare current VRF with desired configuration."""
        current_payload = desired.to_payload()

        # Compare key fields
        return (
            current.get("vrfName") == current_payload.vrf_name
            and current.get("vrfId") == current_payload.vrf_id
            and current.get("vrfTemplate") == current_payload.vrf_template
            and current.get("vrfTemplateConfig") == current_payload.vrf_template_config
            and current.get("vrfExtensionTemplate") == current_payload.vrf_extension_template
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _handle_api_response(self, success: bool, response: dict[str, Any], vrf_name: str, operation: str, success_list: list[str], errors: list[str]) -> bool:
        """
        Handle API response with consistent error handling.

        Args:
            success: Whether the API call succeeded
            response: API response data
            vrf_name: Name of the VRF being operated on
            operation: Operation type (create, update, delete)
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

    def _build_result_message(self, created_vrfs: list[str], updated_vrfs: list[str], deleted_vrfs: Optional[list[str]] = None) -> str:
        """
        Build result message from operation lists.

        Args:
            created_vrfs: List of created VRF names
            updated_vrfs: List of updated/replaced VRF names
            deleted_vrfs: List of deleted VRF names (optional)

        Returns:
            Formatted result message
        """
        messages = []
        if deleted_vrfs:
            messages.append(f"Deleted VRFs: {', '.join(deleted_vrfs)}")
        if created_vrfs:
            messages.append(f"Created VRFs: {', '.join(created_vrfs)}")
        if updated_vrfs:
            # Check if this is being called from replaced state by looking at the stack
            import inspect

            caller = inspect.stack()[2].function if len(inspect.stack()) > 2 else ""
            if "replace" in caller.lower():
                messages.append(f"Replaced VRFs: {', '.join(updated_vrfs)}")
            else:
                messages.append(f"Updated VRFs: {', '.join(updated_vrfs)}")
        if not messages:
            messages.append("No changes needed")

        return "; ".join(messages)

    def _finalize_result(self, created_vrfs: list[str], updated_vrfs: list[str], deleted_vrfs: list[str], errors: list[str]) -> None:
        """
        Finalize the module result with appropriate messages.

        Args:
            created_vrfs: List of created VRF names
            updated_vrfs: List of updated VRF names
            deleted_vrfs: List of deleted VRF names
            errors: List of error messages
        """
        if errors:
            self.result.failed = True
            self.result.msg = "; ".join(errors)
            self.result.stderr = self.result.msg
        else:
            self.result.msg = self._build_result_message(created_vrfs, updated_vrfs, deleted_vrfs)
            self.result.stdout = self.result.msg

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _execute_vrf_operation(self, config: VrfConfig, operation_type: str, created_vrfs: list[str], updated_vrfs: list[str], errors: list[str]) -> None:
        """
        Execute create or update operation for a VRF.

        Args:
            config: VRF configuration
            operation_type: 'create' or 'update'
            created_vrfs: List to append created VRF names to
            updated_vrfs: List to append updated VRF names to
            errors: List to append error messages to
        """
        if operation_type == "create":
            success, response = self.api_client.create_vrf(config.to_payload())
            self._handle_api_response(success, response, config.vrf_name, "create", created_vrfs, errors)
        elif operation_type == "update":
            success, response = self.api_client.update_vrf(config.to_payload())
            self._handle_api_response(success, response, config.vrf_name, "update", updated_vrfs, errors)
