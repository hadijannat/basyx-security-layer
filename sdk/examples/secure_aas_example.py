"""
Example demonstrating the secure AAS implementation.
"""

from basyx.aas import model

from basyx.security import (
    AccessRight,
    SecureAAS,
    SecurityLevel,
    SecurityManager,
    create_security_context,
)


def create_example_aas():
    """Create an example Asset Administration Shell"""
    # Create properties
    temperature = model.Property(
        id_short="Temperature", value_type=model.datatypes.Double, value=25.5, category="Parameter"
    )

    setpoint = model.Property(
        id_short="Setpoint", value_type=model.datatypes.Double, value=26.0, category="Parameter"
    )

    # Create operation
    def calculate_average(params):
        return (temperature.value + setpoint.value) / 2

    avg_operation = model.Operation(id_short="CalculateAverage", func=calculate_average)

    # Create a submodel
    submodel = model.Submodel(
        id_="https://example.com/sensors/temperature",
        id_short="TemperatureSensor",
        submodel_element={temperature, setpoint, avg_operation},
    )

    # Create an AAS
    aas = model.AssetAdministrationShell(
        id_="https://example.com/aas/sensor1",
        id_short="Sensor1",
        asset_information=model.AssetInformation(
            global_asset_id="https://example.com/assets/sensor1",
            asset_kind=model.AssetKind.INSTANCE,
        ),
        submodel={model.ModelReference.from_referable(submodel)},
    )

    return aas


def main():
    # Create security manager
    security_manager = SecurityManager()

    # Set up security policies
    security_manager.set_security_policy("https://example.com/aas/sensor1", SecurityLevel.MEDIUM)
    security_manager.set_security_policy(
        "https://example.com/sensors/temperature", SecurityLevel.HIGH
    )

    # Set up role permissions
    security_manager.set_role_permissions(
        "admin", "https://example.com/aas/sensor1", AccessRight.FULL
    )
    security_manager.set_role_permissions(
        "admin", "https://example.com/sensors/temperature", AccessRight.FULL
    )
    security_manager.set_role_permissions(
        "operator", "https://example.com/sensors/temperature", AccessRight.READ
    )
    security_manager.set_role_permissions(
        "technician", "https://example.com/sensors/temperature", AccessRight.WRITE
    )

    # Create AAS instance
    aas = create_example_aas()
    secure_aas = SecureAAS(aas, security_manager)

    # Create access contexts for different roles
    admin_context = create_security_context(
        user_id="admin1", roles={"admin"}, security_level=SecurityLevel.HIGH
    )

    operator_context = create_security_context(
        user_id="operator1", roles={"operator"}, security_level=SecurityLevel.MEDIUM
    )

    technician_context = create_security_context(
        user_id="tech1", roles={"technician"}, security_level=SecurityLevel.HIGH
    )

    # Demonstrate access control
    try:
        # Admin access
        print("\nTesting admin access:")
        submodel = secure_aas.get_submodel(admin_context, "TemperatureSensor")

        # Read temperature
        temp_element = submodel.get_element(admin_context, "Temperature")
        print(f"Current temperature: {temp_element.get_value(admin_context)}")

        # Update setpoint
        setpoint_element = submodel.get_element(admin_context, "Setpoint")
        setpoint_element.set_value(admin_context, 27.0)
        print(f"Updated setpoint: {setpoint_element.get_value(admin_context)}")

        # Operator access (read-only)
        print("\nTesting operator access:")
        submodel = secure_aas.get_submodel(operator_context, "TemperatureSensor")

        # Read temperature
        temp_element = submodel.get_element(operator_context, "Temperature")
        print(f"Temperature read by operator: {temp_element.get_value(operator_context)}")

        # Try to update setpoint (should fail)
        try:
            setpoint_element = submodel.get_element(operator_context, "Setpoint")
            setpoint_element.set_value(operator_context, 28.0)
            print("Unexpected: Operator should not be able to write")
        except Exception as e:
            print(f"Expected error for operator write: {str(e)}")

        # Technician access (write access)
        print("\nTesting technician access:")
        submodel = secure_aas.get_submodel(technician_context, "TemperatureSensor")

        # Update temperature
        temp_element = submodel.get_element(technician_context, "Temperature")
        temp_element.set_value(technician_context, 26.0)
        print(f"Temperature updated by technician: {temp_element.get_value(technician_context)}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
