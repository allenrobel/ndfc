# MARK plugins/module_utils/vrf/api/vrf_response_handler.py
"""
VRF response handler for API responses.

This module provides the VrfResponseHandler class that processes HTTP responses
from DCNM/NDFC for VRF operations.
"""
from typing import Any
from ...common.classes.response_handler import ResponseHandler


class VrfResponseHandler(ResponseHandler):
    """Response handler for VRF operations."""

    def __init__(self):
        super().__init__()

    def commit(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Process VRF response and return result.

        Args:
            response: Controller response dictionary

        Returns:
            Result dictionary with processed response
        """
        result = {"success": False, "changed": False, "response": None, "error": None}

        try:
            # Check if response indicates success
            if response.get("RETURN_CODE", 0) == 200:
                result["success"] = True
                result["response"] = response.get("DATA", {})
            else:
                result["error"] = response.get("MESSAGE", "Unknown error occurred")

        except Exception as e:
            result["error"] = f"Error processing response: {str(e)}"

        return result
