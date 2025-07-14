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
        then adds VRF-specific processing including field name conversion.
        """
        # Call parent commit for validation and basic processing
        super().commit()
        
        # Add VRF-specific processing to the existing result
        try:
            if self.response and self.response.get("RETURN_CODE", 0) == 200:
                # Keep the parent's result structure and add VRF-specific data
                current_result = self.result or {}
                
                # Convert controller field names to standard format
                transformed_response = self._transform_controller_response(self.response)
                current_result["response"] = transformed_response
                self.result = current_result
                
        except Exception as e:
            # If something goes wrong, update the result with error info
            current_result = self.result or {}
            current_result["success"] = False
            current_result["changed"] = False
            current_result["error"] = f"VRF processing error: {str(e)}"
            self.result = current_result

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
        import copy
        
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
