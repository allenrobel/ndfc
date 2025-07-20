# MARK plugins/module_utils/vrf/api/vrf_response_handler.py
"""
VRF response handler for API responses with Pydantic model support.

This module provides the VrfResponseHandler class that processes HTTP responses
from DCNM/NDFC for VRF operations and converts them to standardized Pydantic models.
"""
import copy
from typing import Optional, Dict, Any

from ...common.classes.response_handler import ResponseHandler
from ..models.controller_response import VrfControllerResponse
from ..models.vrf_data import VrfData
from ..models.response_builder import VrfResponseBuilder


class VrfResponseHandler:
    """
    Response handler for VRF operations using composition with Pydantic model support.

    Converts all VRF controller responses to standardized VrfControllerResponse models
    with consistent DATA field format and proper field name transformations.
    """

    def __init__(self, response_handler: Optional[ResponseHandler] = None):
        """
        Initialize VrfResponseHandler with optional injected ResponseHandler.

        Args:
            response_handler: Optional ResponseHandler instance to inject.
                            If None, creates a default ResponseHandler.
        """
        self._response_handler = response_handler or ResponseHandler()
        self._response: Optional[Dict[str, Any]] = None
        self._result: Optional[Dict[str, Any]] = None
        self._verb: Optional[str] = None
        self._request_path: str = ""
        self._implements = "response_handler_v1"

        # Store the processed VrfControllerResponse model
        self._controller_response: Optional[VrfControllerResponse] = None

    def commit(self):
        """
        Process VRF response and convert to standardized Pydantic models.

        Processes the raw controller response, converts it to a VrfControllerResponse
        model with consistent formatting, and sets the result for downstream use.
        """
        # Delegate basic processing to the composed handler for compatibility
        self._response_handler.response = self._response
        self._response_handler.verb = self._verb
        self._response_handler.commit()

        # Get the base result from the composed handler
        base_result = self._response_handler.result or {}

        try:
            if self._response:
                # Convert to standardized VrfControllerResponse model
                self._controller_response = self._convert_to_controller_response(self._response)

                # Update result with Pydantic model data
                base_result["response"] = self._controller_response.model_dump()
                base_result["success"] = self._controller_response.RETURN_CODE in (200, 201)

            self._result = base_result

        except Exception as e:
            # If conversion fails, create error response
            error_response = VrfResponseBuilder.build_error_response(
                error_message=f"Response processing error: {str(e)}", method=self._verb or "UNKNOWN", request_path=self._request_path, return_code=500
            )

            self._result = {"success": False, "changed": False, "error": str(e), "response": error_response.model_dump()}

    def _convert_to_controller_response(self, raw_response: Dict[str, Any]) -> VrfControllerResponse:
        """
        Convert raw controller response to standardized VrfControllerResponse.

        Handles different response types (query, create, update, delete) and ensures
        consistent format with DATA as list of dictionaries.

        Args:
            raw_response: Raw response from controller

        Returns:
            Standardized VrfControllerResponse model
        """
        # Check if this is already a controller response with metadata
        has_controller_metadata = all(field in raw_response for field in ["MESSAGE", "METHOD", "REQUEST_PATH", "RETURN_CODE"])

        if has_controller_metadata:
            # This is a controller response with metadata
            if self._verb == "DELETE":
                return VrfResponseBuilder.from_delete_response(raw_response)
            elif self._verb == "GET":
                # GET requests with metadata - extract the DATA and treat as query response
                vrf_data = raw_response.get("DATA", [])
                method = raw_response.get("METHOD", "GET")
                request_path = raw_response.get("REQUEST_PATH", self._request_path)
                return_code = raw_response.get("RETURN_CODE", 200)
                return VrfResponseBuilder.from_query_response(raw_response=vrf_data, method=method, request_path=request_path, return_code=return_code)
            else:
                # POST/PUT with metadata
                return VrfResponseBuilder.from_create_update_response(raw_response)
        else:
            # This is raw VRF data without metadata (legacy format)
            return VrfResponseBuilder.from_query_response(raw_response=raw_response, method=self._verb or "GET", request_path=self._request_path)

    def get_vrf_data_models(self) -> list[VrfData]:
        """
        Extract validated VrfData models from the processed response.

        Returns:
            List of VrfData Pydantic models
        """
        if not self._controller_response:
            return []

        return VrfResponseBuilder.validate_and_extract_vrf_data(self._controller_response)

    def get_controller_response(self) -> Optional[VrfControllerResponse]:
        """
        Get the processed VrfControllerResponse model.

        Returns:
            VrfControllerResponse model or None if not processed
        """
        return self._controller_response

    @property
    def implements(self) -> str:
        """
        The interface implemented by this class.

        Returns:
            str: The interface version identifier
        """
        return self._implements

    @property
    def response(self) -> Optional[Dict[str, Any]]:
        """Get the raw controller response."""
        return self._response

    @response.setter
    def response(self, value: Dict[str, Any]):
        """Set the raw controller response."""
        self._response = value

    @property
    def result(self) -> Optional[Dict[str, Any]]:
        """Get the processed result."""
        return self._result

    @property
    def verb(self) -> Optional[str]:
        """Get the request verb."""
        return self._verb

    @verb.setter
    def verb(self, value: str):
        """Set the request verb."""
        self._verb = value

    @property
    def request_path(self) -> str:
        """Get the request path."""
        return self._request_path

    @request_path.setter
    def request_path(self, value: str):
        """Set the request path for building controller responses."""
        self._request_path = value
