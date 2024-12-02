"""
Advanced security example demonstrating additional features of the BaSyx Security Layer.
"""

from datetime import datetime, timedelta
import jwt
from basyx.aas import model
from basyx_security import (
    SecurityManager,
    SecurityLevel,
    AccessRight,
    create_security_context
)
from basyx_security.aas_wrapper import SecureAAS

# Secret key for JWT tokens (in production, use a secure key management system)
SECRET_KEY = "your-secret-key"

def create_jwt_token(user_id: str, roles: list[str], expiry_minutes: int = 30) -> str:
    """Create a JWT token for authentication."""
    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> tuple[str, set[str]]:
    """Verify JWT token and extract user information."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"], set(payload["roles"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def create_complex_aas():
    """Create a more complex AAS for demonstration."""
    # Create properties
    temp = model.Property(
        id_short='Temperature',
        value_type=model.datatypes.Double,
        value=25.5
    )
    
    humidity = model.Property(
        id_short='Humidity',
        value_type=model.datatypes.Double,
        value=60.0
    )
    
    status = model.Property(
        id_short='Status',
        value_type=model.datatypes.String,
        value="operational"
    )
    
    # Create submodels
    sensor_submodel = model.Submodel(
        id_='https://example.com/sensors/environmental',
        id_short='EnvironmentalSensor',
        submodel_element={temp, humidity}
    )
    
    status_submodel = model.Submodel(
        id_='https://example.com/status',
        id_short='SystemStatus',
        submodel_element={status}
    )
    
    # Create AAS
    aas = model.AssetAdministrationShell(
        id_='https://example.com/aas/system1',
        id_short='System1',
        asset_information=model.AssetInformation(
            global_asset_id="https://example.com/assets/system1",
            asset_kind=model.AssetKind.INSTANCE
        ),
        submodel={
            model.ModelReference.from_referable(sensor_submodel),
            model.ModelReference.from_referable(status_submodel)
        }
    )
    
    return aas

def main():
    # Create security manager with hierarchical permissions
    security_manager = SecurityManager()
    
    # Set up security policies with different levels
    security_manager.set_security_policy('System1', SecurityLevel.MEDIUM)
    security_manager.set_security_policy('EnvironmentalSensor', SecurityLevel.HIGH)
    security_manager.set_security_policy('SystemStatus', SecurityLevel.CRITICAL)
    
    # Set up role permissions with hierarchy
    # Admin has full access to everything
    security_manager.set_role_permissions('admin', 'System1', AccessRight.FULL)
    security_manager.set_role_permissions('admin', 'EnvironmentalSensor', AccessRight.FULL)
    security_manager.set_role_permissions('admin', 'SystemStatus', AccessRight.FULL)
    
    # Operator has read/write access to sensors, read-only to status
    security_manager.set_role_permissions('operator', 'System1', AccessRight.READ)
    security_manager.set_role_permissions('operator', 'EnvironmentalSensor', AccessRight.WRITE)
    security_manager.set_role_permissions('operator', 'SystemStatus', AccessRight.READ)
    
    # Viewer has read-only access to sensors only
    security_manager.set_role_permissions('viewer', 'System1', AccessRight.READ)
    security_manager.set_role_permissions('viewer', 'EnvironmentalSensor', AccessRight.READ)
    
    # Create AAS instance
    aas = create_complex_aas()
    secure_aas = SecureAAS(aas, security_manager)
    
    # Demonstrate JWT-based authentication
    try:
        # Create tokens for different roles
        admin_token = create_jwt_token("admin1", ["admin"])
        operator_token = create_jwt_token("operator1", ["operator"])
        viewer_token = create_jwt_token("viewer1", ["viewer"])
        
        # Create security contexts with JWT verification
        admin_id, admin_roles = verify_jwt_token(admin_token)
        admin_context = create_security_context(
            admin_id,
            admin_roles,
            SecurityLevel.CRITICAL,
            admin_token
        )
        
        operator_id, operator_roles = verify_jwt_token(operator_token)
        operator_context = create_security_context(
            operator_id,
            operator_roles,
            SecurityLevel.HIGH,
            operator_token
        )
        
        viewer_id, viewer_roles = verify_jwt_token(viewer_token)
        viewer_context = create_security_context(
            viewer_id,
            viewer_roles,
            SecurityLevel.MEDIUM,
            viewer_token
        )
        
        # Demonstrate different access patterns
        print("\nAdmin Access:")
        sensor_submodel = secure_aas.get_submodel(admin_context, 'EnvironmentalSensor')
        temp_element = sensor_submodel.get_element(admin_context, 'Temperature')
        print(f"Temperature: {temp_element.get_value(admin_context)}")
        temp_element.set_value(admin_context, 26.0)
        print(f"Updated temperature: {temp_element.get_value(admin_context)}")
        
        print("\nOperator Access:")
        sensor_submodel = secure_aas.get_submodel(operator_context, 'EnvironmentalSensor')
        temp_element = sensor_submodel.get_element(operator_context, 'Temperature')
        print(f"Temperature: {temp_element.get_value(operator_context)}")
        temp_element.set_value(operator_context, 26.5)
        print(f"Updated temperature: {temp_element.get_value(operator_context)}")
        
        # Try to modify status (should fail)
        status_submodel = secure_aas.get_submodel(operator_context, 'SystemStatus')
        status_element = status_submodel.get_element(operator_context, 'Status')
        print(f"Status: {status_element.get_value(operator_context)}")
        try:
            status_element.set_value(operator_context, "maintenance")
            print("Unexpected: Operator should not be able to modify status")
        except Exception as e:
            print(f"Expected error: {str(e)}")
        
        print("\nViewer Access:")
        sensor_submodel = secure_aas.get_submodel(viewer_context, 'EnvironmentalSensor')
        temp_element = sensor_submodel.get_element(viewer_context, 'Temperature')
        print(f"Temperature: {temp_element.get_value(viewer_context)}")
        
        # Try to access status submodel (should fail)
        try:
            status_submodel = secure_aas.get_submodel(viewer_context, 'SystemStatus')
            print("Unexpected: Viewer should not be able to access status submodel")
        except Exception as e:
            print(f"Expected error: {str(e)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 