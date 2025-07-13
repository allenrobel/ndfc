# MARK plugins/module_utils/vrf/models/template_models.py
"""
Pydantic models for VRF template configurations.

This module provides structured models for VRF template configurations,
allowing us to work with type-safe objects throughout the business logic
instead of raw dictionaries or JSON strings.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class VrfTemplateConfig(BaseModel):
    """Pydantic model for VRF template configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")

    # Core VRF identification fields
    vrf_segment_id: Optional[int] = Field(default=None, alias="vrfSegmentId")
    vrf_vlan_id: Optional[int] = Field(default=None, alias="vrfVlanId")
    vrf_name: Optional[str] = Field(default=None, alias="vrfName")
    vrf_vlan_name: Optional[str] = Field(default=None, alias="vrfVlanName")
    vrf_description: Optional[str] = Field(default=None, alias="vrfDescription")
    vrf_intf_description: Optional[str] = Field(default=None, alias="vrfIntfDescription")

    # Network configuration
    mtu: Optional[int] = Field(default=None)
    asn: Optional[str] = Field(default=None)
    nve_id: Optional[str] = Field(default=None, alias="nveId")
    loopback_number: Optional[str] = Field(default=None, alias="loopbackNumber")

    # Route target configuration
    route_target_import: Optional[str] = Field(default=None, alias="routeTargetImport")
    route_target_export: Optional[str] = Field(default=None, alias="routeTargetExport")
    route_target_import_evpn: Optional[str] = Field(default=None, alias="routeTargetImportEvpn")
    route_target_export_evpn: Optional[str] = Field(default=None, alias="routeTargetExportEvpn")
    route_target_import_mvpn: Optional[str] = Field(default=None, alias="routeTargetImportMvpn")
    route_target_export_mvpn: Optional[str] = Field(default=None, alias="routeTargetExportMvpn")
    disable_rt_auto: Optional[str] = Field(default=None, alias="disableRtAuto")

    # BGP configuration
    max_bgp_paths: Optional[str] = Field(default=None, alias="maxBgpPaths")
    max_ibgp_paths: Optional[str] = Field(default=None, alias="maxIbgpPaths")
    bgp_password: Optional[str] = Field(default=None, alias="bgpPassword")
    bgp_password_key_type: Optional[str] = Field(default=None, alias="bgpPasswordKeyType")

    # Routing configuration
    vrf_route_map: Optional[str] = Field(default=None, alias="vrfRouteMap")
    advertise_default_route_flag: Optional[str] = Field(default=None, alias="advertiseDefaultRouteFlag")
    advertise_host_route_flag: Optional[str] = Field(default=None, alias="advertiseHostRouteFlag")
    configure_static_default_route_flag: Optional[str] = Field(default=None, alias="configureStaticDefaultRouteFlag")
    ipv6_link_local_flag: Optional[str] = Field(default=None, alias="ipv6LinkLocalFlag")
    tag: int = Field(default=12345, le=4294967295)  # Loopback Routing Tag

    # Multicast configuration
    multicast_group: Optional[str] = Field(default=None, alias="multicastGroup")
    l3_vni_mcast_group: Optional[str] = Field(default=None, alias="L3VniMcastGroup")
    rp_address: Optional[str] = Field(default=None, alias="rpAddress")
    is_rp_external: Optional[str] = Field(default=None, alias="isRPExternal")
    is_rp_absent: Optional[str] = Field(default=None, alias="isRPAbsent")

    # TRM (Tenant Routed Multicast) configuration
    trm_enabled: Optional[str] = Field(default=None, alias="trmEnabled")
    trm_bgw_msite_enabled: Optional[str] = Field(default=None, alias="trmBGWMSiteEnabled")

    # NetFlow configuration
    enable_netflow: Optional[str] = Field(default=None, alias="ENABLE_NETFLOW")
    netflow_monitor: Optional[str] = Field(default=None, alias="NETFLOW_MONITOR")

    # Allow any additional fields that may be present in templates
    # This is necessary because VRF templates can have many dynamic fields


class ServiceVrfTemplateConfig(BaseModel):
    """Pydantic model for Service VRF template configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="allow")

    # Service VRF template fields - using extra="allow" for flexibility
    # Add specific fields as they are identified
