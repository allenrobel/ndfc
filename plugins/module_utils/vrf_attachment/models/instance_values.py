# MARK plugins/module_utils/vrf_attachment/models/instance_values.py
"""
InstanceValues - Pydantic model for VRF attachment instance values.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InstanceValues(BaseModel):
    """Pydantic model for VRF attachment instance values configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    # Loopback interface configuration
    loopback_ipv6_address: Optional[str] = Field(default="", alias="loopbackIpV6Address")
    loopback_id: Optional[str] = Field(default="", alias="loopbackId")
    device_support_l3_vni_no_vlan: Optional[str] = Field(default="false", alias="deviceSupportL3VniNoVlan")
    switch_route_target_import_evpn: Optional[str] = Field(default="", alias="switchRouteTargetImportEvpn")
    loopback_ip_address: Optional[str] = Field(default="", alias="loopbackIpAddress")
    switch_route_target_export_evpn: Optional[str] = Field(default="", alias="switchRouteTargetExportEvpn")