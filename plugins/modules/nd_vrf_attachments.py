#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible module for managing VRF attachments on Nexus Dashboard
.

This module provides comprehensive VRF attachment management capabilities for NDFC including
creation, updates, deletion, and querying with optimized caching support.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # pylint: disable=invalid-name

from typing import Any
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: ndfc_vrf_attachments
short_description: Manage VRF attachments on Nexus Dashboard Fabric Controller
description:
  - This module allows you to manage VRF attachments on Nexus Dashboard Fabric Controller (NDFC).
  - It supports creating, updating, deleting, and querying VRF attachments.
  - The module uses Pydantic for data validation and follows Ansible best practices.
  - Features optimized caching using composition-based design to minimize controller requests.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  config:
    description:
      - List of VRF attachment configurations
      - Required for all states to specify at least the fabric and vrf_name
    type: list
    elements: dict
    required: true
    suboptions:
      fabric:
        description:
          - Name of the fabric where the VRF resides
          - This is the only field validated by Ansible
          - All other fields are validated by state-specific Pydantic models
        type: str
        required: true
      vrf_name:
        description:
          - Name of the VRF to attach
          - Validation handled by state-specific models
        type: str
        required: true
      lan_attach_list:
        description:
          - List of LAN attachments for the VRF
          - Each attachment specifies a switch and configuration
        type: list
        elements: dict
        suboptions:
          ip_address:
            description:
              - IP address of the switch for the attachment
              - This will be translated to serial number internally
            type: str
            required: true
          vlan_id:
            description:
              - VLAN ID for the VRF attachment
            type: int
            required: true
          deployment:
            description:
              - Whether to deploy the attachment
            type: bool
            default: false
          extension_values:
            description:
              - Extension values for VRF Lite configuration
              - Contains VRF Lite connection parameters
            type: dict
            suboptions:
              vrf_lite_conn:
                description:
                  - VRF Lite connection configuration
                type: dict
                suboptions:
                  vrf_lite_conn:
                    description:
                      - List of VRF Lite connections
                    type: list
                    elements: dict
                    suboptions:
                      auto_vrf_lite_flag:
                        description: Auto VRF Lite flag
                        type: str
                        default: "true"
                      dot1q_id:
                        description: 802.1Q VLAN ID
                        type: str
                      if_name:
                        description: Interface name
                        type: str
                      ip_mask:
                        description: IP address and mask
                        type: str
                      ipv6_mask:
                        description: IPv6 address and mask
                        type: str
                      ipv6_neighbor:
                        description: IPv6 neighbor address
                        type: str
                      neighbor_asn:
                        description: Neighbor ASN
                        type: str
                      neighbor_ip:
                        description: Neighbor IP address
                        type: str
                      peer_vrf_name:
                        description: Peer VRF name
                        type: str
                      vrf_lite_jython_template:
                        description: VRF Lite Jython template
                        type: str
                        default: "Ext_VRF_Lite_Jython"
          freeform_config:
            description:
              - Freeform configuration for the attachment
            type: str
            default: ""
          instance_values:
            description:
              - Instance values for the attachment
            type: dict
            suboptions:
              loopback_ipv6_address:
                description: Loopback IPv6 address
                type: str
                default: ""
              loopback_id:
                description: Loopback interface ID
                type: str
                default: ""
              device_support_l3_vni_no_vlan:
                description: Device support for L3 VNI without VLAN
                type: str
                default: "false"
              switch_route_target_import_evpn:
                description: Switch route target import for EVPN
                type: str
                default: ""
              loopback_ip_address:
                description: Loopback IP address
                type: str
                default: ""
              switch_route_target_export_evpn:
                description: Switch route target export for EVPN
                type: str
                default: ""
  state:
    description:
      - The state of the VRF attachment configuration
    type: str
    choices: [deleted, merged, overridden, query, replaced]
    default: merged
requirements:
  - pydantic>=2.0.0
notes:
  - This module requires an established connection to the Nexus Dashboard.
  - The connection details (hostname, username, password) should be configured in the Ansible inventory.
  - The module uses composition-based caching for optimal performance and loose coupling.
  - "|"
    Validation approach:
    - Ansible validates only basic structure and the 'fabric' and 'vrf_name' fields
    - State-specific Pydantic models handle all other validation with detailed error messages
    - This provides better validation feedback and cleaner module interface
  - "|"
    Required fields vary by state:
    - deleted: config with fabric and vrf_name required (lan_attach_list optional - if omitted, deletes all attachments)
    - query: config with fabric and vrf_name required (lan_attach_list optional for filtering)
    - merged: config with fabric, vrf_name, and lan_attach_list required
    - replaced/overridden: config with fabric, vrf_name, and lan_attach_list required
"""

EXAMPLES = r"""
# Attach VRF to switches with basic configuration
- name: Attach VRF to switches
  ndfc_vrf_attachments:
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"
        lan_attach_list:
          - ip_address: "192.168.1.1"
            vlan_id: 100
            deployment: true
          - ip_address: "192.168.1.2"
            vlan_id: 100
            deployment: true
    state: merged

# Attach VRF with VRF Lite configuration
- name: Attach VRF with VRF Lite
  ndfc_vrf_attachments:
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"
        lan_attach_list:
          - ip_address: "192.168.1.1"
            vlan_id: 100
            deployment: true
            extension_values:
              vrf_lite_conn:
                vrf_lite_conn:
                  - dot1q_id: "2"
                    if_name: "Ethernet2/10"
                    ip_mask: "10.33.0.2/30"
                    ipv6_mask: "2010::10:34:0:7/64"
                    ipv6_neighbor: "2010::10:34:0:3"
                    neighbor_asn: "65002"
                    neighbor_ip: "10.33.0.1"
                    peer_vrf_name: "test_vrf"
    state: merged

# Query VRF attachments
- name: Query VRF attachments
  ndfc_vrf_attachments:
    state: query
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"

# Delete specific VRF attachments
- name: Delete specific VRF attachments
  ndfc_vrf_attachments:
    state: deleted
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"
        lan_attach_list:
          - ip_address: "192.168.1.1"
            vlan_id: 100

# Delete all VRF attachments
- name: Delete all VRF attachments
  ndfc_vrf_attachments:
    state: deleted
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"

# Replace VRF attachments
- name: Replace VRF attachments
  ndfc_vrf_attachments:
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"
        lan_attach_list:
          - ip_address: "192.168.1.1"
            vlan_id: 200
            deployment: true
    state: replaced
"""

RETURN = r"""
changed:
  description: Whether the module made any changes
  type: bool
  returned: always
  sample: true
failed:
  description: Whether the module failed
  type: bool
  returned: always
  sample: false
msg:
  description: Human readable message about what the module did
  type: str
  returned: always
  sample: "Attached VRFs: test_vrf"
stdout:
  description: Standard output from the operation
  type: str
  returned: always
  sample: "Attached VRFs: test_vrf"
stderr:
  description: Standard error from the operation
  type: str
  returned: when failed
  sample: "Failed to attach VRF test_vrf: Invalid configuration"
response:
  description: Response data from the controller
  type: list
  returned: when state is query or when operations are performed
  sample: [{"DATA": {"test_vrf-[FOX2109PGCS/switch-1]": "SUCCESS"}, "MESSAGE": "OK", "RETURN_CODE": 200}]
"""

# Import our custom modules
try:
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.enums.ansible_states import AnsibleStates
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.cache.cache_manager import CacheManager
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.cache.cached_resource_service import CachedResourceService
    from ansible_collections.cisco.ndfc.plugins.module_utils.vrf_attachment.validators.vrf_attachment_validator import VrfAttachmentValidator
    from ansible_collections.cisco.ndfc.plugins.module_utils.vrf_attachment.api.vrf_attachment_api import VrfAttachmentApi
    from ansible_collections.cisco.ndfc.plugins.module_utils.vrf_attachment.states.state_factory import StateFactory
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.classes.log_v2 import Log
except ImportError:
    # This will be caught by the module and reported as an error
    pass


def validate_parameters(module: AnsibleModule) -> tuple[list[Any], AnsibleStates]:
    """Validate and process module parameters."""
    config = module.params.get("config", [])
    state = module.params.get("state", "merged")

    try:
        # Validate state
        ansible_state = AnsibleStates(state)

        # Config is required for all states
        if not config:
            module.fail_json(msg="config parameter is required for all states")

        # Validate configurations if provided
        validated_configs = []
        if config:
            validated_configs = VrfAttachmentValidator.validate_config_list_by_state(config, ansible_state.value)

        return validated_configs, ansible_state

    except ValueError as e:
        module.fail_json(msg=f"Parameter validation failed: {e}")
        return [], AnsibleStates.MERGED  # This line will never execute but satisfies pylint
    except Exception as e:  # pylint: disable=broad-exception-caught
        module.fail_json(msg=f"Unexpected error during validation: {e}")
        return [], AnsibleStates.MERGED  # This line will never execute but satisfies pylint


def main():
    """Main module execution."""

    # Define module arguments
    module_args = {
        "config": {
            "type": "list",
            "elements": "dict",
            "required": True,
            "options": {
                "fabric": {
                    "type": "str",
                    "required": True,
                },
                "vrf_name": {
                    "type": "str",
                    "required": True,
                },
                "lan_attach_list": {
                    "type": "list",
                    "elements": "dict",
                    "required": False,
                    "options": {
                        "ip_address": {
                            "type": "str",
                            "required": True,
                        },
                        "vlan_id": {
                            "type": "int",
                            "required": True,
                        },
                        "deployment": {
                            "type": "bool",
                            "default": False,
                        },
                        "extension_values": {
                            "type": "dict",
                            "required": False,
                        },
                        "freeform_config": {
                            "type": "str",
                            "default": "",
                        },
                        "instance_values": {
                            "type": "dict",
                            "required": False,
                        },
                    },
                },
            },
        },
        "state": {
            "type": "str",
            "choices": ["deleted", "merged", "overridden", "query", "replaced"],
            "default": "merged",
        },
    }

    # Create module instance
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Initialize logging
    try:
        log = Log()
        log.commit()
    except ValueError as error:
        module.fail_json(msg=str(error))

    # Validate parameters
    try:
        validated_configs, state = validate_parameters(module)
    except Exception as e:  # pylint: disable=broad-exception-caught
        module.fail_json(msg=f"Failed to validate parameters: {e}")

    # Initialize cache service and API client using composition
    try:
        # Create cache manager with 5-minute default TTL for VRF attachment data
        cache_manager = CacheManager(default_ttl_seconds=300)

        # Create cached resource service for VRF attachment resources
        cached_service = CachedResourceService[dict[str, Any]](cache_manager, "vrf_attachment")

        # Initialize VRF attachment API with injected caching service
        api_client = VrfAttachmentApi(ansible_module=module, check_mode=module.check_mode, cached_service=cached_service)
    except Exception as e:  # pylint: disable=broad-exception-caught
        module.fail_json(msg=f"Failed to initialize API client: {e}")

    # Create and execute state handler
    try:
        state_handler = StateFactory.create_state(state, api_client)
        result = state_handler.execute(validated_configs)

        # Convert Pydantic result to dict for Ansible
        result_dict = result.model_dump()

        # Handle check mode
        if module.check_mode and result_dict["changed"]:
            result_dict["msg"] = f"Would have executed {state} operation"

        # Exit with results
        if result_dict["failed"]:
            module.fail_json(**result_dict)
        else:
            module.exit_json(**result_dict)

    except Exception as e:  # pylint: disable=broad-exception-caught
        module.fail_json(msg=f"Module execution failed: {e}")


if __name__ == "__main__":
    main()