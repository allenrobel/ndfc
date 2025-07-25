# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains the Cisco NDFC (Nexus Dashboard Fabric Controller) Ansible collection. It provides modules to automate day-2 operations for VXLAN EVPN fabrics.

## Common Commands

### Linting and Code Quality

```bash
# Run all linters (black, flake8, pylint)
tox -e linters

# Run black formatter
tox -e black

# Run pylint only
tox -e pylint

# Run linters in virtual environment
tox -e linters

# Run a specific linter
flake8 <file>
black -v -l160 <file>
pylint <file>
```

### Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
ansible-test integration

# Run sanity tests
ansible-test sanity --docker
```

### Development Environment

```bash
# Install dependencies
pip install -r requirements.txt -r test-requirements.txt

# Run in development mode
tox -e venv -- <command>
```

## Architecture

### Directory Structure

- `plugins/modules/` - Ansible modules (nd_vrf, nd_fabric, nd_interface, etc.)
- `plugins/module_utils/` - Shared utility modules organized by feature
- `plugins/httpapi/` - HTTP API plugin for ND communication
- `plugins/action/` - Action plugins for complex module operations
- `tests/unit/` - Unit tests mirroring the plugins directory structure
- `tests/integration/` - Integration tests with real ND instances

### Key Components

#### Module Utils Architecture

- `plugins/module_utils/common/` - Shared utilities (API clients, logging, validation)
- `plugins/module_utils/common/cache` - Caching service
- `plugins/module_utils/vrf/` - VRF-specific utilities and models
- `plugins/module_utils/fabric/` - Fabric management utilities

#### API Layer

- `plugins/module_utils/common/api/` - Hierarchical API structure matching ND REST endpoints
- `plugins/module_utils/common/ep/`  - All endpoints in api above will move into ep eventually
- `plugins/module_utils/common/epp/` - endpoint parsers.  These classes are responsible for sending a request for the corresponding endpoint (ep) and providing properties that return the values of each of the fields in the controller response for the endpoint (ep)
- `plugins/module_utils/common/classes/log_v2.py` - Logger for the project
- `plugins/module_utils/common/classes/rest_send_v2.py` - HTTP request handling
- `plugins/module_utils/common/classes/results.py` - HTTP request results handler
- `plugins/module_utils/common/classes/sender_*.py` - Request sender implementations

#### General utilities

- `plugins/module_utils/common/classes/switch_details.py` - Returns inventory details for switches in a fabric.
- `plugins/module_utils/common/classes/conversion.py` - Provides conversion methods for several commonly-used conversions (e.g. translate mac address)
- `plugins/module_utils/common/classes/conversion.py` - The logger used by this project
- `plugins/module_utils/common/classes/rest_send_v2.py` - Send requests to the controller using injected dependencies.
- `plugins/module_utils/common/classes/sender.nd.py` - RestSend dependency that sends requests to NDFC using the nd_send()
- `plugins/module_utils/common/classes/sender_requests.py` - RestSend dependency that sends requests to NDFC using the python requests library

#### VRF Module (Active Development)

The VRF module is currently being refactored to use Pydantic models:

- `plugins/module_utils/vrf/nd_vrf_v12.py` - Main VRF module (v12 API)
- `plugins/module_utils/vrf/model_*.py` - Pydantic models for request/response data
- Working on integrating Pydantic validation throughout the VRF workflow

### Design Patterns

#### State Management

Modules follow Ansible's declarative state patterns:

- `merged` - Add/update resources
- `replaced` - Replace specific resources
- `overridden` - Replace all resources
- `deleted` - Remove resources
- `query` - Retrieve current state

**Reference**: See `plugins/module_utils/common/enums/ansible.py` for detailed descriptions of each state, including HTTP verbs used and idempotency behavior.

**HTTP Methods**: Use `RequestVerb` enum from `plugins/module_utils/common/enums/http_requests.py` for all HTTP methods (DELETE, GET, POST, PUT) instead of string literals.

#### Data Validation

- Transitioning from manual validation to Pydantic models
- Models define request/response schemas with validation
- Located in `model_*.py` files within each feature directory

#### Error Handling

- Response validation and error reporting

## Development Guidelines

### Code Standards

- Line length: 160 characters (configured in tox.ini)
- Black formatting enforced
- Type hints encouraged (mypy configuration in mypy.ini)
- Pydantic models for data validation (preferred for new code)
- Favor composition over inheritance
- Dependency injection
- Single responsibility
- Modularity
- SOLID principles

### Testing Requirements

- Unit tests required for all new functionality
- Integration tests for complex workflows
- Fixtures in `tests/unit/*/fixtures/` directories
- Mock responses for controller interactions

### Common Patterns

- Use `plugins/module_utils/common/rest_send_v2.py` for HTTP requests
- Use `RequestVerb` enum from `plugins/module_utils/common/enums/http_requests.py` for HTTP methods
- Implement proper logging using `plugins/module_utils/common/log_v2.py`
- Follow existing module structure in `plugins/modules/`
- Use Pydantic models for structured data

### Interface Versioning

Components that interact with each other should implement interface versioning to ensure compatibility and enable safe refactoring:

- **Add `implements` property** - All classes that implement an interface should declare the interface version via an `implements` property
- **Use semantic versioning** - Interface versions follow `interface_name_v{major}` format (e.g., `response_handler_v1`)
- **Validate compatibility** - Components should check the `implements` property of injected dependencies to ensure compatibility

#### Implementation Pattern

```python
class MyHandler:
    def __init__(self):
        self._implements = "my_interface_v1"
    
    @property
    def implements(self):
        """Return the interface version implemented by this class."""
        return self._implements

# Usage in component that expects the interface
def some_method(self, handler):
    if handler.implements != "my_interface_v1":
        raise ValueError(f"Expected my_interface_v1, got {handler.implements}")
```

#### Examples

- **RestSend**: Uses `response_handler_v1` interface for response handler injection
- **VrfResponseHandler**: Implements `response_handler_v1` interface for compatibility with RestSend
- **Benefits**: Enables safe dependency injection, interface evolution, and compile-time compatibility checking

### Version Compatibility

- Support NDFC 12.0+
- Ansible 2.15.0+ compatibility required
- Python 3.x support

## Notes for AI Development

### Current Focus Areas

- Pay attention to `plugins/module_utils/vrf/` for latest patterns
- Follow the model-based validation approach being implemented

### Testing Strategy

- Always run `tox -e linters` before committing
- Unit tests should mock controller responses using fixtures
- Integration tests require real ND instances

### Common Issues

- Pydantic validation errors need proper error message formatting

## Code Memory

### Module Utility Conventions

- `@plugins/module_utils/common/enums/http_requests.py` contains an enum that should be used whenever HTTP methods (DELETE, GET, POST, PUT) are used.
