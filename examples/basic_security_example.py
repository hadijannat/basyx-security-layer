#!/usr/bin/env python3
"""Basic example demonstrating BaSyx security features."""

from basyx.aas import model
from basyx_security.core import SecurityManager, SecurityLevel, AccessRight, create_security_context
from basyx_security.aas_wrapper.secure_aas import SecureAAS
from basyx_security.aas_wrapper.provider import DictProvider


def create_example_aas():
    """Create a simple AAS with a temperature sensor."""
    # Create a property for temperature
    temperature = model.Property(
        id_short="Temperature", value_type=model.datatypes.Double, value=25.5
    )

    # Create a submodel
    submodel = model.Submodel(
        id_="https://example.com/sensors/temperature",
        id_short="TemperatureSensor",
        submodel_element={temperature},
    )

    # Create the AAS
    aas = model.AssetAdministrationShell(
        id_="https://example.com/aas/sensor1",
        id_short="Sensor1",
        asset_information=model.AssetInformation(
            global_asset_id="https://example.com/assets/sensor1",
            asset_kind=model.AssetKind.INSTANCE,
        ),
        submodel={model.ModelReference.from_referable(submodel)},
    )

    return aas, submodel


def main():
    """Run the example."""
    # Create AAS and security components
    aas, submodel = create_example_aas()
    security_manager = SecurityManager()

    # Set up security policies
    security_manager.set_security_policy(
        "Sensor1", SecurityLevel.MEDIUM  # Using id_short instead of full URI
    )
    security_manager.set_security_policy(
        "TemperatureSensor", SecurityLevel.HIGH  # Using id_short instead of full URI
    )
    security_manager.set_security_policy(
        "Temperature", SecurityLevel.HIGH  # Property security level
    )

    # Set up role permissions for admin
    security_manager.set_role_permissions("admin", "Sensor1", AccessRight.FULL)
    security_manager.set_role_permissions("admin", "TemperatureSensor", AccessRight.FULL)
    security_manager.set_role_permissions("admin", "Temperature", AccessRight.FULL)

    # Set up role permissions for operator
    security_manager.set_role_permissions("operator", "Sensor1", AccessRight.READ)
    security_manager.set_role_permissions("operator", "TemperatureSensor", AccessRight.READ)
    security_manager.set_role_permissions("operator", "Temperature", AccessRight.READ)

    # Create a provider for submodels
    provider = DictProvider({"https://example.com/sensors/temperature": submodel})

    # Create secure AAS instance
    secure_aas = SecureAAS(aas, security_manager, provider)

    # Create security contexts for different roles
    admin_context = create_security_context(
        user_id="admin1", roles={"admin"}, security_level=SecurityLevel.HIGH
    )

    operator_context = create_security_context(
        user_id="operator1", roles={"operator"}, security_level=SecurityLevel.MEDIUM
    )

    # Demonstrate access control
    try:
        print("\nTesting admin access:")
        submodel = secure_aas.get_submodel(admin_context, "TemperatureSensor")
        temp_element = submodel.get_element(admin_context, "Temperature")
        print(f"Current temperature: {temp_element.get_value(admin_context)}")

        # Update value as admin
        temp_element.set_value(admin_context, 26.5)
        print(f"Updated temperature: {temp_element.get_value(admin_context)}")

        print("\nTesting operator access:")
        submodel = secure_aas.get_submodel(operator_context, "TemperatureSensor")
        temp_element = submodel.get_element(operator_context, "Temperature")
        print(f"Temperature read by operator: {temp_element.get_value(operator_context)}")

        # Try to update value as operator (should fail)
        print("\nTesting operator write access (should fail):")
        try:
            temp_element.set_value(operator_context, 27.0)
            print("Unexpected: Operator should not be able to write")
        except Exception as e:
            print(f"Expected error for operator write: {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
