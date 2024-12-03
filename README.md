# BaSyx Security Layer

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/hadijannat/basyx-security-layer)](https://github.com/hadijannat/basyx-security-layer/issues)

A security implementation layer for the Eclipse BaSyx Python SDK, providing robust security features for Asset Administration Shell (AAS) implementations.

## Features

- **Role-Based Access Control (RBAC)**
  - Fine-grained access control for AAS components
  - Flexible role management
  - Permission inheritance

- **Security Levels**
  - Multiple security level support
  - Configurable security policies
  - Context-aware access control

- **Secure AAS Wrappers**
  - Secure Element implementation
  - Protected Submodel access
  - Controlled AAS operations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from PyPI
```bash
pip install basyx-security
```

### Install from Source
```bash
git clone https://github.com/hadijannat/basyx-security-layer.git
cd basyx-security-layer
pip install -e .
```

### Development Installation
For development, install with additional tools:
```bash
pip install -e .[dev]
```

## Quick Start

Here's a complete example showing how to secure an AAS:

```python
from basyx.aas import model
from basyx_security import SecurityManager, SecurityLevel, AccessRight, create_security_context
from basyx_security.aas_wrapper import SecureAAS, DictProvider

# Create a simple AAS with a temperature sensor
def create_example_aas():
    # Create a property for temperature
    temperature = model.Property(
        id_short='Temperature',
        value_type=model.datatypes.Double,
        value=25.5
    )
    
    # Create a submodel
    submodel = model.Submodel(
        id_='https://example.com/sensors/temperature',
        id_short='TemperatureSensor',
        submodel_element={temperature}
    )
    
    # Create the AAS
    aas = model.AssetAdministrationShell(
        id_='https://example.com/aas/sensor1',
        id_short='Sensor1',
        asset_information=model.AssetInformation(
            global_asset_id="https://example.com/assets/sensor1",
            asset_kind=model.AssetKind.INSTANCE
        ),
        submodel={model.ModelReference.from_referable(submodel)}
    )
    
    return aas, submodel

# Create AAS and security components
aas, submodel = create_example_aas()
security_manager = SecurityManager()

# Set up security policies
security_manager.set_security_policy(
    'https://example.com/aas/sensor1',
    SecurityLevel.MEDIUM
)
security_manager.set_security_policy(
    'https://example.com/sensors/temperature',
    SecurityLevel.HIGH
)

# Set up role permissions
security_manager.set_role_permissions(
    'admin',
    'https://example.com/aas/sensor1',
    AccessRight.FULL
)
security_manager.set_role_permissions(
    'operator',
    'https://example.com/sensors/temperature',
    AccessRight.READ
)

# Create a provider for submodels
provider = DictProvider({'https://example.com/sensors/temperature': submodel})

# Create secure AAS instance
secure_aas = SecureAAS(aas, security_manager, provider)

# Create security contexts for different roles
admin_context = create_security_context(
    user_id="admin1",
    roles={"admin"},
    security_level=SecurityLevel.HIGH
)

operator_context = create_security_context(
    user_id="operator1",
    roles={"operator"},
    security_level=SecurityLevel.MEDIUM
)

# Use the secure AAS
try:
    # Admin access
    submodel = secure_aas.get_submodel(admin_context, "TemperatureSensor")
    temp_element = submodel.get_element(admin_context, "Temperature")
    print(f"Current temperature: {temp_element.get_value(admin_context)}")
    
    # Update value as admin
    temp_element.set_value(admin_context, 26.5)
    print(f"Updated temperature: {temp_element.get_value(admin_context)}")
    
    # Operator access (read-only)
    submodel = secure_aas.get_submodel(operator_context, "TemperatureSensor")
    temp_element = submodel.get_element(operator_context, "Temperature")
    print(f"Temperature read by operator: {temp_element.get_value(operator_context)}")
    
except Exception as e:
    print(f"Error: {str(e)}")
```

## Documentation

For detailed documentation, please visit our [documentation page](docs/). Key topics include:

- [Core Concepts](docs/core-concepts.md)
- [Security Features](docs/security-features.md)
- [API Reference](docs/api-reference.md)
- [Advanced Examples](docs/examples.md)

## Examples

Check out our [examples directory](examples/) for more detailed examples:

- Basic AAS Security
- Role-Based Access Control
- Audit Logging
- Rate Limiting
- Session Management

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Eclipse BaSyx Python SDK](https://github.com/eclipse-basyx/basyx-python-sdk)
- [Eclipse BaSyx](https://www.eclipse.org/basyx/)
