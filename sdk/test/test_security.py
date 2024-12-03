"""
Test cases for the BaSyx security implementation.
"""

import unittest

from basyx.aas import model
from basyx.security import (
    AccessRight,
    SecureAAS,
    SecurityLevel,
    SecurityManager,
    SecurityViolation,
    create_security_context,
)


class TestBaSyxSecurity(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        # Create a simple AAS for testing
        self.temperature = model.Property(
            id_short="Temperature", value_type=model.datatypes.Double, value=25.5
        )

        self.submodel = model.Submodel(
            id_="https://test.com/sensors/temp",
            id_short="TempSensor",
            submodel_element={self.temperature},
        )

        self.aas = model.AssetAdministrationShell(
            id_="https://test.com/aas/sensor1",
            id_short="TestSensor",
            asset_information=model.AssetInformation(
                global_asset_id="https://test.com/assets/sensor1",
                asset_kind=model.AssetKind.INSTANCE,
            ),
            submodel={model.ModelReference.from_referable(self.submodel)},
        )

        # Create object store for reference resolution
        self.object_store = model.DictObjectStore([self.aas, self.submodel])

        # Set up security manager
        self.security_manager = SecurityManager()

        # Set security policies
        self.security_manager.set_security_policy(
            "https://test.com/aas/sensor1", SecurityLevel.MEDIUM
        )
        self.security_manager.set_security_policy(
            "https://test.com/sensors/temp", SecurityLevel.MEDIUM
        )
        self.security_manager.set_security_policy(
            "https://test.com/sensors/temp/Temperature", SecurityLevel.MEDIUM
        )

        # Set role permissions
        # Admin has full access to everything
        self.security_manager.set_role_permissions(
            "admin", "https://test.com/aas/sensor1", AccessRight.FULL
        )
        self.security_manager.set_role_permissions(
            "admin", "https://test.com/sensors/temp", AccessRight.FULL
        )
        self.security_manager.set_role_permissions(
            "admin", "https://test.com/sensors/temp/Temperature", AccessRight.FULL
        )

        # Operator has read access to AAS and submodel
        self.security_manager.set_role_permissions(
            "operator", "https://test.com/aas/sensor1", AccessRight.READ
        )
        self.security_manager.set_role_permissions(
            "operator", "https://test.com/sensors/temp", AccessRight.READ
        )
        self.security_manager.set_role_permissions(
            "operator", "https://test.com/sensors/temp/Temperature", AccessRight.READ
        )

        # Create secure AAS with object store
        self.secure_aas = SecureAAS(self.aas, self.security_manager, self.object_store)

        # Create security contexts
        self.admin_context = create_security_context(
            user_id="admin1", roles={"admin"}, security_level=SecurityLevel.HIGH
        )

        self.operator_context = create_security_context(
            user_id="operator1", roles={"operator"}, security_level=SecurityLevel.MEDIUM
        )

        self.unauthorized_context = create_security_context(
            user_id="guest1", roles={"guest"}, security_level=SecurityLevel.LOW
        )

    def test_admin_full_access(self):
        """Test admin role has full access"""
        # Get submodel
        submodel = self.secure_aas.get_submodel(self.admin_context, "TempSensor")
        self.assertIsNotNone(submodel)

        # Get and read temperature
        temp_element = submodel.get_element(self.admin_context, "Temperature")
        self.assertEqual(temp_element.get_value(self.admin_context), 25.5)

        # Update temperature
        temp_element.set_value(self.admin_context, 26.5)
        self.assertEqual(temp_element.get_value(self.admin_context), 26.5)

    def test_operator_read_only(self):
        """Test operator role has read-only access"""
        # Get submodel
        submodel = self.secure_aas.get_submodel(self.operator_context, "TempSensor")
        self.assertIsNotNone(submodel)

        # Read temperature
        temp_element = submodel.get_element(self.operator_context, "Temperature")
        self.assertEqual(temp_element.get_value(self.operator_context), 25.5)

        # Try to update temperature (should fail)
        with self.assertRaises(SecurityViolation):
            temp_element.set_value(self.operator_context, 27.0)

    def test_unauthorized_access(self):
        """Test unauthorized access is blocked"""
        # Try to access submodel (should fail)
        with self.assertRaises(SecurityViolation):
            self.secure_aas.get_submodel(self.unauthorized_context, "TempSensor")

    def test_security_levels(self):
        """Test security level enforcement"""
        # Create context with insufficient security level
        low_level_admin = create_security_context(
            user_id="admin2", roles={"admin"}, security_level=SecurityLevel.LOW
        )

        # Try to access high-security resource (should fail)
        with self.assertRaises(SecurityViolation):
            self.secure_aas.get_submodel(low_level_admin, "TempSensor")

    def test_token_authentication(self):
        """Test JWT token authentication"""
        # Create token
        token = self.security_manager.create_token(self.admin_context)
        self.assertIsNotNone(token)

        # Verify token
        verified_context = self.security_manager.verify_token(token)
        self.assertEqual(verified_context.user_id, self.admin_context.user_id)
        self.assertEqual(verified_context.roles, self.admin_context.roles)
        self.assertEqual(verified_context.security_level, self.admin_context.security_level)


if __name__ == "__main__":
    unittest.main()
