# MARK plugins/module_utils/vrf/states/base_state_v2.py
"""
Base state class for VRF state handlers with Pydantic model support.

This module provides the BaseStateV2 abstract base class that uses the new
VrfApiV2 and works exclusively with Pydantic models for type safety.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from ..models.module_result import ModuleResult
from ..models.vrf_config import VrfConfig
from ..models.vrf_data import VrfData
from ..models.controller_response import VrfControllerResponse
from ..api.vrf_api_v2 import VrfApiV2


class BaseStateV2(ABC):
    """
    Base class for all VRF states using Pydantic models and VrfApiV2.

    Provides common functionality for state operations with type-safe
    VrfData models and consistent VrfControllerResponse handling.
    """

    def __init__(self, api_client: VrfApiV2):
        """
        Initialize base state with VrfApiV2 client.

        Args:
            api_client: VrfApiV2 instance with Pydantic model support
        """
        self.api_client = api_client
        self.result = ModuleResult()

    @abstractmethod
    def execute(self, configs: List[VrfConfig]) -> ModuleResult:
        """Execute the state operation."""

    def _populate_all_fabric_caches(self, configs: List[VrfConfig]) -> None:
        """
        Pre-populate cache for all fabrics mentioned in configs.

        Uses VrfApiV2 to cache VrfData models for all fabrics.

        Args:
            configs: List of VRF configurations to get fabric names from
        """
        fabrics = set(config.fabric for config in configs)
        for fabric in fabrics:
            # This will cache all VRFs as VrfData models for the fabric
            self.api_client.get_all_vrfs_cached(fabric)

    def _vrf_exists(self, fabric: str, vrf_name: str) -> tuple[bool, Optional[VrfData]]:
        """
        Check if VRF exists using cache with VrfData model.

        Args:
            fabric: The fabric name
            vrf_name: The VRF name

        Returns:
            Tuple of (exists, VrfData_model_or_None)
        """
        return self.api_client.vrf_exists_cached(fabric, vrf_name)

    def _get_all_fabric_vrfs(self, fabric: str) -> Dict[str, VrfData]:
        """
        Get all VRFs for a fabric as VrfData models.

        Args:
            fabric: The fabric name

        Returns:
            Dictionary mapping VRF names to VrfData models
        """
        return self.api_client.get_all_vrfs_cached(fabric)

    def _vrfs_equal(self, current_vrf: VrfData, desired_config: VrfConfig) -> bool:
        """
        Compare current VRF model with desired configuration.

        Args:
            current_vrf: Current VrfData model from cache/API
            desired_config: Desired VrfConfig configuration

        Returns:
            True if VRFs are equal, False otherwise
        """
        desired_payload = desired_config.to_payload()

        # Compare key fields using VrfData model properties
        return (
            current_vrf.vrf_name == desired_payload.vrf_name
            and current_vrf.vrf_id == desired_payload.vrf_id
            and current_vrf.vrf_template == desired_payload.vrf_template
            and current_vrf.vrf_template_config == desired_payload.vrf_template_config
            and current_vrf.vrf_extension_template == desired_payload.vrf_extension_template
        )

    def _handle_api_response(
        self,
        success: bool,
        controller_response: VrfControllerResponse,
        vrf_name: str,
        operation: str,
        success_list: List[str],
        errors: List[str],
    ) -> bool:
        """
        Handle VrfControllerResponse with consistent error handling.

        Args:
            success: Whether the API call succeeded
            controller_response: VrfControllerResponse from API
            vrf_name: Name of the VRF being operated on
            operation: Operation type (create, update, delete)
            success_list: List to append successful VRF names to
            errors: List to append error messages to

        Returns:
            True if operation succeeded, False otherwise
        """
        if success and controller_response.RETURN_CODE in (200, 201):
            success_list.append(vrf_name)
            self.result.changed = True
            return True

        # Extract error message from controller response
        error_msg = controller_response.MESSAGE if not success else f"HTTP {controller_response.RETURN_CODE}"
        errors.append(f"Failed to {operation} VRF {vrf_name}: {error_msg}")
        return False

    def _build_result_message(
        self,
        created_vrfs: List[str],
        updated_vrfs: List[str],
        deleted_vrfs: Optional[List[str]] = None,
    ) -> str:
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

    def _finalize_result(self, created_vrfs: List[str], updated_vrfs: List[str], deleted_vrfs: List[str], errors: List[str]) -> None:
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

    def _execute_vrf_operation(
        self,
        config: VrfConfig,
        operation_type: str,
        created_vrfs: List[str],
        updated_vrfs: List[str],
        errors: List[str],
    ) -> None:
        """
        Execute create or update operation for a VRF using VrfApiV2.

        Args:
            config: VRF configuration
            operation_type: 'create' or 'update'
            created_vrfs: List to append created VRF names to
            updated_vrfs: List to append updated VRF names to
            errors: List to append error messages to
        """
        if operation_type == "create":
            success, controller_response = self.api_client.create_vrf(config.to_payload())
            self._handle_api_response(success, controller_response, config.vrf_name, "create", created_vrfs, errors)
        elif operation_type == "update":
            success, controller_response = self.api_client.update_vrf(config.to_payload())
            self._handle_api_response(success, controller_response, config.vrf_name, "update", updated_vrfs, errors)

    def _execute_vrf_operation_with_response(
        self,
        config: VrfConfig,
        operation_type: str,
        created_vrfs: List[str],
        updated_vrfs: List[str],
        errors: List[str],
    ) -> Optional[VrfControllerResponse]:
        """
        Execute create or update operation and return VrfControllerResponse.

        Args:
            config: VRF configuration
            operation_type: 'create' or 'update'
            created_vrfs: List to append created VRF names to
            updated_vrfs: List to append updated VRF names to
            errors: List to append error messages to

        Returns:
            VrfControllerResponse if successful, None if failed
        """
        if operation_type == "create":
            success, controller_response = self.api_client.create_vrf(config.to_payload())
            if self._handle_api_response(success, controller_response, config.vrf_name, "create", created_vrfs, errors):
                return controller_response
        elif operation_type == "update":
            success, controller_response = self.api_client.update_vrf(config.to_payload())
            if self._handle_api_response(success, controller_response, config.vrf_name, "update", updated_vrfs, errors):
                return controller_response
        return None

    def _convert_controller_responses_to_data_list(self, controller_responses: List[VrfControllerResponse]) -> List[Dict[str, any]]:
        """
        Convert list of VrfControllerResponse models to data list for module response.

        Maintains compatibility with existing module result format while using
        Pydantic models internally.

        Args:
            controller_responses: List of VrfControllerResponse models

        Returns:
            List of response dictionaries for module result
        """
        response_data = []
        for controller_response in controller_responses:
            # Convert Pydantic model to dict for module response
            response_data.append(controller_response.model_dump())
        return response_data
