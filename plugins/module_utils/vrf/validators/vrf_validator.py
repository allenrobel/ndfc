# MARK plugins/module_utils/vrf/validators/vrf_validator.py
"""
VRF data validation utilities.

This module provides validation functions for VRF-related data structures
using Pydantic models to ensure data integrity.
"""
from typing import Any
from pydantic import ValidationError
from ..models.vrf_config import VrfConfig
from ..models.vrf_payload import VrfPayload
from ..models.vrf_response import VrfResponse
from ..models.state_configs import DeletedVrfConfig, QueryVrfConfig, MergedVrfConfig, ReplacedVrfConfig, OverriddenVrfConfig


class VrfValidator:
    """Validator class for VRF-related data."""

    @staticmethod
    def validate_config(config_data: dict[str, Any]) -> VrfConfig:
        """Validate VRF configuration data."""
        try:
            return VrfConfig(**config_data)
        except ValidationError as error:
            raise ValueError(f"Invalid VRF configuration: {error}") from error

    @staticmethod
    def validate_payload(payload_data: dict[str, Any]) -> VrfPayload:
        """Validate VRF payload data."""
        try:
            return VrfPayload(**payload_data)
        except ValidationError as error:
            raise ValueError(f"Invalid VRF payload: {error}") from error

    @staticmethod
    def validate_response(response_data: dict[str, Any]) -> VrfResponse:
        """Validate VRF response data."""
        try:
            return VrfResponse(**response_data)
        except ValidationError as error:
            raise ValueError(f"Invalid VRF response: {error}") from error

    @staticmethod
    def validate_config_list(config_list: list[dict[str, Any]]) -> list[VrfConfig]:
        """Validate a list of VRF configurations (legacy method for backward compatibility)."""
        validated_configs = []
        for i, config in enumerate(config_list):
            try:
                validated_configs.append(VrfValidator.validate_config(config))
            except ValueError as error:
                raise ValueError(f"Invalid VRF configuration at index {i}: {error}") from error
        return validated_configs

    @staticmethod
    def validate_config_list_by_state(config_list: list[dict[str, Any]], state: str) -> list[VrfConfig]:
        """Validate a list of VRF configurations using state-specific models."""
        validated_configs = []
        for i, config in enumerate(config_list):
            try:
                if state == "deleted":
                    state_config = DeletedVrfConfig(**config)
                    validated_configs.append(state_config.to_vrf_config())
                elif state == "query":
                    state_config = QueryVrfConfig(**config)
                    validated_configs.append(state_config.to_vrf_config())
                elif state == "merged":
                    state_config = MergedVrfConfig(**config)
                    validated_configs.append(state_config.to_vrf_config())
                elif state == "replaced":
                    state_config = ReplacedVrfConfig(**config)
                    validated_configs.append(state_config.to_vrf_config())
                elif state == "overridden":
                    state_config = OverriddenVrfConfig(**config)
                    validated_configs.append(state_config.to_vrf_config())
                else:
                    raise ValueError(f"Unknown state: {state}")
            except ValidationError as error:
                raise ValueError(f"Invalid VRF configuration at index {i} for state '{state}': {error}") from error
            except ValueError as error:
                raise ValueError(f"Invalid VRF configuration at index {i}: {error}") from error
        return validated_configs
