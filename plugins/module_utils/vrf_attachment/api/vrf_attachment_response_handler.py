# MARK plugins/module_utils/vrf_attachment/api/vrf_attachment_response_handler.py
"""
VRF attachment response handler for API responses.

This module provides the VrfAttachmentResponseHandler class that processes HTTP responses
from DCNM/NDFC for VRF attachment operations.
"""
from ...common.classes.response_handler import ResponseHandler


class VrfAttachmentResponseHandler(ResponseHandler):
    """Response handler for VRF attachment operations."""

    def __init__(self):
        super().__init__()

    def commit(self):
        """
        Process VRF attachment response and set result.
        
        Follows the parent class interface - calls parent commit() for validation,
        then adds VRF attachment-specific processing.
        """
        # Call parent commit for validation and basic processing
        super().commit()
        
        # Add VRF attachment-specific processing to the existing result
        try:
            if self.response and self.response.get("RETURN_CODE", 0) == 200:
                # Keep the parent's result structure and add VRF attachment-specific data
                current_result = self.result or {}
                
                # Return the full raw controller response for VRF attachments
                current_result["response"] = self.response
                self.result = current_result
                
        except Exception as e:
            # If something goes wrong, update the result with error info
            current_result = self.result or {}
            current_result["success"] = False
            current_result["changed"] = False
            current_result["error"] = f"VRF attachment processing error: {str(e)}"
            self.result = current_result