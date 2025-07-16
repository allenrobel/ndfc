# MARK plugins/module_utils/vrf_attachment/models/extension_values.py
"""
ExtensionValues - Pydantic model for VRF attachment extension values.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class VrfLiteConnection(BaseModel):
    """Pydantic model for VRF Lite connection configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    auto_vrf_lite_flag: Optional[str] = Field(default="true", alias="AUTO_VRF_LITE_FLAG")
    dot1q_id: Optional[str] = Field(default="", alias="DOT1Q_ID")
    if_name: Optional[str] = Field(default="", alias="IF_NAME")
    ip_mask: Optional[str] = Field(default="", alias="IP_MASK")
    ipv6_mask: Optional[str] = Field(default="", alias="IPV6_MASK")
    ipv6_neighbor: Optional[str] = Field(default="", alias="IPV6_NEIGHBOR")
    neighbor_asn: Optional[str] = Field(default="", alias="NEIGHBOR_ASN")
    neighbor_ip: Optional[str] = Field(default="", alias="NEIGHBOR_IP")
    peer_vrf_name: Optional[str] = Field(default="", alias="PEER_VRF_NAME")
    vrf_lite_jython_template: Optional[str] = Field(default="Ext_VRF_Lite_Jython", alias="VRF_LITE_JYTHON_TEMPLATE")


class VrfLiteConnections(BaseModel):
    """Container for VRF Lite connections."""
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    
    vrf_lite_conn: List[VrfLiteConnection] = Field(default_factory=list, alias="VRF_LITE_CONN")


class MultisiteConnections(BaseModel):
    """Container for multisite connections."""
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    
    multisite_conn: List[Dict[str, Any]] = Field(default_factory=list, alias="MULTISITE_CONN")


class ExtensionValues(BaseModel):
    """Pydantic model for VRF attachment extension values configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    # VRF Lite connections
    vrf_lite_conn: Optional[VrfLiteConnections] = Field(default_factory=VrfLiteConnections, alias="VRF_LITE_CONN")
    
    # Multisite connections
    multisite_conn: Optional[MultisiteConnections] = Field(default_factory=MultisiteConnections, alias="MULTISITE_CONN")