# MARK plugins/module_utils/vrf_attachment/validators/vrf_attachment_validator.py
"""
VRF attachment data validation utilities.

This module provides validation functions for VRF attachment-related data structures
using Pydantic models to ensure data integrity.
"""
from typing import Any
from pydantic import ValidationError
from ..models.vrf_attachment_config import VrfAttachmentConfig
from ..models.vrf_attachment_payload import VrfAttachmentPayload
from ..models.vrf_attachment_response import VrfAttachmentResponse
from ..models.state_configs import (
    DeletedVrfAttachmentConfig,
    QueryVrfAttachmentConfig,
    MergedVrfAttachmentConfig,
    ReplacedVrfAttachmentConfig,
    OverriddenVrfAttachmentConfig
)


class VrfAttachmentValidator:
    """Validator class for VRF attachment-related data."""

    @staticmethod
    def validate_config(config_data: dict[str, Any]) -> VrfAttachmentConfig:
        """Validate VRF attachment configuration data."""
        try:
            return VrfAttachmentConfig(**config_data)
        except ValidationError as error:
            raise ValueError(f"Invalid VRF attachment configuration: {error}") from error

    @staticmethod
    def validate_payload(payload_data: dict[str, Any]) -> VrfAttachmentPayload:
        """Validate VRF attachment payload data."""
        try:
            return VrfAttachmentPayload(**payload_data)
        except ValidationError as error:
            raise ValueError(f"Invalid VRF attachment payload: {error}") from error

    @staticmethod
    def validate_response(response_data: dict[str, Any]) -> VrfAttachmentResponse:
        """Validate VRF attachment response data."""
        try:
            return VrfAttachmentResponse(**response_data)
        except ValidationError as error:
            raise ValueError(f"Invalid VRF attachment response: {error}") from error

    @staticmethod
    def validate_config_list(config_list: list[dict[str, Any]]) -> list[VrfAttachmentConfig]:
        """Validate a list of VRF attachment configurations (legacy method for backward compatibility)."""
        validated_configs = []
        for i, config in enumerate(config_list):
            try:
                validated_configs.append(VrfAttachmentValidator.validate_config(config))
            except ValueError as error:
                raise ValueError(f"Invalid VRF attachment configuration at index {i}: {error}") from error
        return validated_configs

    @staticmethod
    def validate_config_list_by_state(config_list: list[dict[str, Any]], state: str) -> list[VrfAttachmentConfig]:
        """Validate a list of VRF attachment configurations using state-specific models."""
        validated_configs = []
        for i, config in enumerate(config_list):
            try:
                if state == "deleted":
                    state_config = DeletedVrfAttachmentConfig(**config)
                    validated_configs.append(state_config.to_vrf_attachment_config())
                elif state == "query":
                    state_config = QueryVrfAttachmentConfig(**config)
                    validated_configs.append(state_config.to_vrf_attachment_config())
                elif state == "merged":
                    state_config = MergedVrfAttachmentConfig(**config)
                    validated_configs.append(state_config.to_vrf_attachment_config())
                elif state == "replaced":
                    state_config = ReplacedVrfAttachmentConfig(**config)
                    validated_configs.append(state_config.to_vrf_attachment_config())
                elif state == "overridden":
                    state_config = OverriddenVrfAttachmentConfig(**config)
                    validated_configs.append(state_config.to_vrf_attachment_config())
                else:
                    raise ValueError(f"Unknown state: {state}")
            except ValidationError as error:
                raise ValueError(f"Invalid VRF attachment configuration at index {i} for state '{state}': {error}") from error
            except ValueError as error:
                raise ValueError(f"Invalid VRF attachment configuration at index {i}: {error}") from error
        return validated_configs