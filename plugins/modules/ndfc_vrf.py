#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible module for managing VRFs on Nexus Dashboard Fabric Controller.

This module provides comprehensive VRF management capabilities for NDFC including
creation, updates, deletion, and querying with optimized caching support.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # pylint: disable=invalid-name

from typing import Any
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: nexus_vrf
short_description: Manage VRFs on Nexus Dashboard Fabric Controller
description:
  - This module allows you to manage VRFs on Nexus Dashboard Fabric Controller (NDFC).
  - It supports creating, updating, deleting, and querying VRFs.
  - The module uses Pydantic for data validation and follows Ansible best practices.
  - Features optimized caching using composition-based design to minimize controller requests.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  config:
    description:
      - List of VRF configurations
      - Required for all states to specify at least the fabric
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
          - Name of the VRF
          - Validation handled by state-specific models
        type: str
      vrf_id:
        description:
          - Numerical ID of the VRF
          - Validation handled by state-specific models
        type: int
      vrf_template:
        description:
          - Template name for VRF configuration
          - Validation handled by state-specific models
        type: str
      vrf_template_config:
        description:
          - Dictionary containing VRF template configuration parameters
          - Contains nested configuration like vrfSegmentId, vrfVlanId, mtu, etc.
          - Validation handled by state-specific models
        type: dict
        suboptions:
          asn:
            description: Autonomous system number
            type: str
          mtu:
            description: Maximum transmission unit for the VRF
            type: int
          route_target_export:
            description: Route target export value
            type: str
            aliases: [routeTargetExport]
          route_target_import:
            description: Route target import value
            type: str
            aliases: [routeTargetImport]
          tag:
            description: Loopback routing tag for the VRF
            type: int
            default: 12345
            maximum: 4294967295
          vrf_description:
            description: Description for the VRF
            type: str
            aliases: [vrfDescription]
          vrf_segment_id:
            description: VRF segment ID for VXLAN
            type: int
            aliases: [vrfSegmentId]
          vrf_vlan_id:
            description: VLAN ID for the VRF
            type: int
            aliases: [vrfVlanId]
      vrf_extension_template:
        description:
          - Template name for VRF extension configuration
          - Validation handled by state-specific models
        type: str
      service_vrf_template:
        description:
          - Dictionary containing service VRF template configuration
          - Validation handled by state-specific models
        type: dict
      tenant_name:
        description:
          - Name of the tenant associated with the VRF
          - Optional field for multi-tenant deployments
        type: str
      hierarchical_key:
        description:
          - Hierarchical key for the VRF in NDFC
          - Usually matches the fabric name
        type: str
  state:
    description:
      - The state of the VRF configuration
    type: str
    choices: [deleted, merged, overridden, query, replaced]
    default: merged
requirements:
  - pydantic>=2.0.0
notes:
  - This module requires an established connection to the Nexus Dashboard.
  - The connection details (hostname, username, password) should be configured in the Ansible inventory.
  - VRF attachments are handled by a separate module.
  - The module uses composition-based caching for optimal performance and loose coupling.
  - |
    Validation approach:
    - Ansible validates only basic structure and the 'fabric' field
    - State-specific Pydantic models handle all other validation with detailed error messages
    - This provides better validation feedback and cleaner module interface
  - |
    Required fields vary by state:
    - deleted: config with fabric required (vrf_name optional - if omitted, deletes all VRFs in fabric)
    - query: config with fabric required (vrf_name optional for filtering specific VRF)
    - merged: config with fabric, vrf_name, vrf_template_config (vrf_id optional, auto-assigned)
    - replaced/overridden: config with fabric, vrf_name, vrf_id, vrf_template_config
"""

EXAMPLES = r"""
# Create or update a VRF with nested template configuration
- name: Create VRF with comprehensive configuration
  nexus_vrf:
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"
        vrf_id: 12345
        vrf_template_config:
          vrf_segment_id: 12345
          vrf_vlan_id: 100
          mtu: 9216
          vrf_description: "Test VRF for application"
          asn: "65001"
          route_target_import: "65001:12345"
          route_target_export: "65001:12345"
          advertise_default_route_flag: "true"
          max_bgp_paths: "1"
          max_ibgp_paths: "2"
    state: merged

# Delete specific VRF
- name: Delete specific VRF
  nexus_vrf:
    state: deleted
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"

# Delete all VRFs in fabric (only fabric required)
- name: Delete all VRFs in fabric
  nexus_vrf:
    state: deleted
    config:
      - fabric: "fabric1"

# Query all VRFs in fabric (fabric required)
- name: Query all VRFs in fabric
  nexus_vrf:
    state: query
    config:
      - fabric: "fabric1"

# Query specific VRF (fabric required, vrf_name optional for filtering)
- name: Query specific VRF
  nexus_vrf:
    state: query
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"

# Replace VRF with updated configuration
- name: Replace VRF with updated template config
  nexus_vrf:
    config:
      - fabric: "fabric1"
        vrf_name: "test_vrf"
        vrf_id: 12345
        tenant_name: "production"
        hierarchical_key: "fabric1"
        vrf_template_config:
          vrf_segment_id: 12345
          vrf_vlan_id: 200
          mtu: 9000
          vrf_description: "Updated production VRF"
          asn: "65001"
          route_target_import: "65001:12345"
          route_target_export: "65001:12345"
          advertise_default_route_flag: "true"
          configure_static_default_route_flag: "true"
    state: replaced

# Override all VRFs in fabric with proper nested structure
- name: Override VRFs with comprehensive configuration
  nexus_vrf:
    config:
      - fabric: "fabric1"
        vrf_name: "prod_vrf"
        vrf_id: 10001
        vrf_template_config:
          vrf_segment_id: 10001
          vrf_vlan_id: 101
          mtu: 9216
          vrf_description: "Production VRF"
          asn: "65001"
      - fabric: "fabric1"
        vrf_name: "dev_vrf"
        vrf_id: 10002
        vrf_template_config:
          vrf_segment_id: 10002
          vrf_vlan_id: 102
          mtu: 9216
          vrf_description: "Development VRF"
          asn: "65001"
    state: overridden

# Multiple VRFs across different fabrics with optimized caching
- name: Manage multiple VRFs efficiently
  nexus_vrf:
    config:
      # These 5 VRFs will result in only 2 API calls (one per fabric)
      - fabric: "fabric1"
        vrf_name: "vrf1"
        vrf_id: 1001
        vrf_template_config:
          vrf_segment_id: 1001
          vrf_vlan_id: 101
          mtu: 9216
      - fabric: "fabric1"
        vrf_name: "vrf2"
        vrf_id: 1002
        vrf_template_config:
          vrf_segment_id: 1002
          vrf_vlan_id: 102
          mtu: 9216
      - fabric: "fabric1"
        vrf_name: "vrf3"
        vrf_id: 1003
        vrf_template_config:
          vrf_segment_id: 1003
          vrf_vlan_id: 103
          mtu: 9216
      - fabric: "fabric2"
        vrf_name: "vrf4"
        vrf_id: 2001
        vrf_template_config:
          vrf_segment_id: 2001
          vrf_vlan_id: 201
          mtu: 9216
      - fabric: "fabric2"
        vrf_name: "vrf5"
        vrf_id: 2002
        vrf_template_config:
          vrf_segment_id: 2002
          vrf_vlan_id: 202
          mtu: 9216
    state: merged

# Example showing Pydantic validation catching errors
# This would fail with detailed error message about missing vrf_name
- name: Invalid merged config (missing vrf_name)
  nexus_vrf:
    config:
      - fabric: "fabric1"
        vrf_template_config:
          vrf_segment_id: 1001
          vrf_vlan_id: 101
    state: merged
  # Error: "Invalid VRF configuration at index 0 for state 'merged': Field required [type=missing, input={'fabric': 'fabric1', 'vrf_template_config': {...}}]"
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
  sample: "Created VRFs: test_vrf"
stdout:
  description: Standard output from the operation
  type: str
  returned: always
  sample: "Created VRFs: test_vrf"
stderr:
  description: Standard error from the operation
  type: str
  returned: when failed
  sample: "Failed to create VRF test_vrf: Invalid configuration"
response:
  description: Response data from the controller
  type: list
  returned: when state is query
  sample: [{"vrfName": "test_vrf", "vrfId": 12345, "fabric": "fabric1"}]
"""

# Import our custom modules
try:
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.enums.ansible_states import AnsibleStates
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.cache.cache_manager import CacheManager
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.cache.cached_resource_service import CachedResourceService
    from ansible_collections.cisco.ndfc.plugins.module_utils.vrf.validators.vrf_validator import VrfValidator
    from ansible_collections.cisco.ndfc.plugins.module_utils.vrf.api.vrf_api import VrfApi
    from ansible_collections.cisco.ndfc.plugins.module_utils.vrf.states.state_factory import StateFactory
    from ansible_collections.cisco.ndfc.plugins.module_utils.common.classes.log_v2 import Log

    # from ansible_collections.cisco.ndfc.plugins.module_utils.vrf.models.module_result import ModuleResult
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
            validated_configs = VrfValidator.validate_config_list_by_state(config, ansible_state.value)

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
                    "required": False,
                },
                "vrf_id": {
                    "type": "int",
                    "required": False,
                },
                "vrf_template": {
                    "type": "str",
                    "required": False,
                },
                "vrf_template_config": {
                    "type": "dict",
                    "required": False,
                },
                "vrf_extension_template": {
                    "type": "str",
                    "required": False,
                },
                "service_vrf_template": {
                    "type": "dict",
                    "required": False,
                },
                "tenant_name": {
                    "type": "str",
                    "required": False,
                },
                "hierarchical_key": {
                    "type": "str",
                    "required": False,
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
        # Create cache manager with 5-minute default TTL for VRF data
        cache_manager = CacheManager(default_ttl_seconds=300)

        # Create cached resource service for VRF resources
        cached_service = CachedResourceService[dict[str, Any]](cache_manager, "vrf")

        # Initialize VRF API with injected caching service
        api_client = VrfApi(ansible_module=module, check_mode=module.check_mode, cached_service=cached_service)
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
