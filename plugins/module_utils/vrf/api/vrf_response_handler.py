# MARK plugins/module_utils/vrf/api/vrf_response_handler.py
"""
VRF response handler for API responses.

This module provides the VrfResponseHandler class that processes HTTP responses
from DCNM/NDFC for VRF operations.
"""
from ...common.classes.response_handler import ResponseHandler


class VrfResponseHandler(ResponseHandler):
    """Response handler for VRF operations."""

    def __init__(self):
        super().__init__()

    def commit(self):
        """
        Process VRF response and set result.
        
        Follows the parent class interface - calls parent commit() for validation,
        then adds VRF-specific processing.
        """
        # Call parent commit for validation and basic processing
        super().commit()
        
        # Add VRF-specific processing to the existing result
        try:
            if self.response and self.response.get("RETURN_CODE", 0) == 200:
                # Keep the parent's result structure and add VRF-specific data
                current_result = self.result or {}
                current_result["response"] = self.response.get("DATA", {})
                self.result = current_result
                
        except Exception as e:
            # If something goes wrong, update the result with error info
            current_result = self.result or {}
            current_result["success"] = False
            current_result["changed"] = False
            current_result["error"] = f"VRF processing error: {str(e)}"
            self.result = current_result
