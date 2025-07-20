# MARK plugins/module_utils/vrf/models/response_builder.py
"""
Response builder utilities for creating consistent controller responses.

This module provides utilities to convert various controller response formats
into consistent VrfControllerResponse models with standardized DATA fields.
"""
from typing import Any, List, Dict, Optional, Union
from .controller_response import VrfControllerResponse
from .vrf_data import VrfData


class VrfResponseBuilder:
    """
    Builder class for creating consistent VRF controller responses.

    Handles conversion of various response formats (query, create, update, delete)
    into standardized VrfControllerResponse models with DATA as list of dict.
    """

    @staticmethod
    def from_query_response(
        raw_response: Union[List[dict], dict], method: str = "GET", request_path: str = "", return_code: int = 200
    ) -> VrfControllerResponse:
        """
        Build controller response from query operation.

        Query responses typically don't have controller metadata,
        so we need to wrap the VRF data in controller response format.

        Args:
            raw_response: Raw VRF data from query (list or single dict)
            method: HTTP method used
            request_path: Request URL path
            return_code: HTTP return code

        Returns:
            Standardized VrfControllerResponse
        """
        # Ensure we have a list of VRF data dictionaries
        if isinstance(raw_response, dict):
            vrf_data_list = [raw_response]
        elif isinstance(raw_response, list):
            vrf_data_list = raw_response
        else:
            vrf_data_list = []

        return VrfControllerResponse(DATA=vrf_data_list, MESSAGE="OK", METHOD=method, REQUEST_PATH=request_path, RETURN_CODE=return_code)

    @staticmethod
    def from_controller_response(raw_response: dict, force_data_as_list: bool = True) -> VrfControllerResponse:
        """
        Build controller response from raw controller response.

        Handles responses that already have controller metadata but
        ensures DATA field is consistently formatted as list.

        Args:
            raw_response: Raw controller response with metadata
            force_data_as_list: Whether to ensure DATA is a list

        Returns:
            Standardized VrfControllerResponse
        """
        # Extract controller metadata
        message = raw_response.get("MESSAGE", "OK")
        method = raw_response.get("METHOD", "POST")
        request_path = raw_response.get("REQUEST_PATH", "")
        return_code = raw_response.get("RETURN_CODE", 200)

        # Handle DATA field - ensure it's always a list
        data_field = raw_response.get("DATA", {})

        if force_data_as_list:
            if isinstance(data_field, list):
                data_list = data_field
            elif isinstance(data_field, dict):
                # Single dict becomes list with one item (or empty list if empty dict)
                data_list = [data_field] if data_field else [{}]
            else:
                data_list = [{}]  # Default empty list with empty dict
        else:
            data_list = [data_field] if data_field else [{}]

        return VrfControllerResponse(DATA=data_list, MESSAGE=message, METHOD=method, REQUEST_PATH=request_path, RETURN_CODE=return_code)

    @staticmethod
    def from_delete_response(raw_response: dict) -> VrfControllerResponse:
        """
        Build controller response from delete operation.

        Delete responses typically have controller metadata but
        empty or minimal DATA field.

        Args:
            raw_response: Raw controller response from delete

        Returns:
            Standardized VrfControllerResponse with empty DATA
        """
        message = raw_response.get("MESSAGE", "OK")
        method = raw_response.get("METHOD", "DELETE")
        request_path = raw_response.get("REQUEST_PATH", "")
        return_code = raw_response.get("RETURN_CODE", 200)

        # Delete operations always have empty DATA as [{}]
        return VrfControllerResponse(DATA=[{}], MESSAGE=message, METHOD=method, REQUEST_PATH=request_path, RETURN_CODE=return_code)

    @staticmethod
    def from_create_update_response(raw_response: dict, vrf_data: Optional[Dict[str, Any]] = None) -> VrfControllerResponse:
        """
        Build controller response from create/update operation.

        Create/update responses have controller metadata and may
        include the created/updated VRF data.

        Args:
            raw_response: Raw controller response
            vrf_data: Optional VRF data to include in response

        Returns:
            Standardized VrfControllerResponse
        """
        message = raw_response.get("MESSAGE", "OK")
        method = raw_response.get("METHOD", "POST")
        request_path = raw_response.get("REQUEST_PATH", "")
        return_code = raw_response.get("RETURN_CODE", 200)

        # Include VRF data if provided, otherwise use controller's DATA or empty
        if vrf_data:
            data_list = [vrf_data]
        else:
            controller_data = raw_response.get("DATA", {})
            if isinstance(controller_data, dict) and controller_data:
                data_list = [controller_data]
            else:
                data_list = [{}]

        return VrfControllerResponse(DATA=data_list, MESSAGE=message, METHOD=method, REQUEST_PATH=request_path, RETURN_CODE=return_code)

    @staticmethod
    def build_error_response(error_message: str, method: str = "GET", request_path: str = "", return_code: int = 500) -> VrfControllerResponse:
        """
        Build error response for failed operations.

        Args:
            error_message: Error description
            method: HTTP method that failed
            request_path: Request URL path
            return_code: HTTP error code

        Returns:
            Error VrfControllerResponse
        """
        return VrfControllerResponse(DATA=[{}], MESSAGE=error_message, METHOD=method, REQUEST_PATH=request_path, RETURN_CODE=return_code)

    @staticmethod
    def validate_and_extract_vrf_data(response: VrfControllerResponse) -> List[VrfData]:
        """
        Extract and validate VRF data from controller response.

        Args:
            response: VrfControllerResponse to process

        Returns:
            List of validated VrfData models

        Raises:
            ValidationError: If VRF data is invalid
        """
        vrf_data_list = []

        for data_dict in response.DATA:
            if data_dict:  # Skip empty dictionaries
                try:
                    vrf_data = VrfData.model_validate(data_dict)
                    vrf_data_list.append(vrf_data)
                except Exception as e:
                    # Log validation error but continue processing
                    # In production, you might want to handle this differently
                    continue

        return vrf_data_list
