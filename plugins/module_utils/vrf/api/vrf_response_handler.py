# MARK plugins/module_utils/vrf/api/vrf_response_handler.py
"""
VRF response handler for API responses.

This module provides the VrfResponseHandler class that processes HTTP responses
from DCNM/NDFC for VRF operations.
"""
import copy

from ...common.classes.response_handler import ResponseHandler


class VrfResponseHandler:
    """Response handler for VRF operations using composition."""

    def __init__(self, response_handler=None):
        """Initialize VrfResponseHandler with optional injected ResponseHandler.

        Args:
            response_handler: Optional ResponseHandler instance to inject.
                            If None, creates a default ResponseHandler.
        """
        self._response_handler = response_handler or ResponseHandler()
        self._response = None
        self._result = None
        self._verb = None
        self._implements = "response_handler_v1"

    def commit(self):
        """
        Process VRF response and set result.

        Delegates basic processing to the composed ResponseHandler,
        then adds VRF-specific processing including field name conversion.
        """
        # Delegate basic processing to the composed handler
        self._response_handler.response = self._response
        self._response_handler.verb = self._verb
        self._response_handler.commit()

        # Get the base result from the composed handler
        base_result = self._response_handler.result or {}

        # Add VRF-specific processing to the existing result
        try:
            if self._response and self._response.get("RETURN_CODE", 0) in (200, 201):
                # Convert controller field names to standard format
                transformed_response = self._transform_controller_response(self._response)
                base_result["response"] = transformed_response
            self._result = base_result

        except (TypeError, ValueError, KeyError) as e:
            # If something goes wrong, update the result with error info
            self._result = {
                "success": False,
                "changed": False,
                "error": f"VRF processing error: {str(e)}"
            }

    def _transform_controller_response(self, response):
        """
        Transform controller response field names to match Pydantic model aliases.

        Converts controller field names to standard format:
        - "VRF Id" -> "vrfId"
        - "VRF Name" -> "vrfName"

        Args:
            response: Controller response dict

        Returns:
            Transformed response dict with standardized field names
        """
        # Create a deep copy to avoid modifying the original response
        transformed_response = copy.deepcopy(response)

        # Transform DATA field if present (where controller VRF data typically resides)
        if "DATA" in transformed_response:
            data = transformed_response["DATA"]

            # Handle single dict or list of dicts
            if isinstance(data, dict):
                self._transform_vrf_fields(data)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        self._transform_vrf_fields(item)

        return transformed_response

    @property
    def implements(self):
        """
        The interface implemented by this class.

        Returns:
            str: The interface version identifier
        """
        return self._implements

    @property
    def response(self):
        """Get the controller response."""
        return self._response

    @response.setter
    def response(self, value):
        """Set the controller response."""
        self._response = value

    @property
    def result(self):
        """Get the processed result."""
        return self._result

    @property
    def verb(self):
        """Get the request verb."""
        return self._verb

    @verb.setter
    def verb(self, value):
        """Set the request verb."""
        self._verb = value

    def _transform_vrf_fields(self, vrf_dict):
        """
        Transform VRF field names in a single VRF dictionary.

        Args:
            vrf_dict: Dictionary containing VRF data to transform (modified in place)
        """
        # Field name mappings from controller format to standard format
        field_mappings = {
            "VRF Id": "vrfId",
            "VRF Name": "vrfName"
        }

        # Transform field names
        for old_field, new_field in field_mappings.items():
            if old_field in vrf_dict:
                vrf_dict[new_field] = vrf_dict.pop(old_field)
