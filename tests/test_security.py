"""
Tests for the BaSyx Security Layer.
"""

import pytest
from datetime import datetime, UTC
from typing import Dict
from basyx.aas import model
from basyx_security import (
    SecurityManager,
    SecurityContext,
    SecurityLevel,
    AccessRight,
    create_security_context,
    SecureAAS,
    AuditLog,
    AuditEvent
)
from basyx_security.aas_wrapper.provider import DictProvider

def create_test_aas():
    """Create a test AAS for testing."""
    # Create a simple property
    temp = model.Property(
        id_short='Temperature',
        value_type=model.datatypes.Double,
        value=25.5
    )
    
    # Create a submodel
    submodel = model.Submodel(
        id_='https://example.com/sensors/temp',
        id_short='TempSensor',
        submodel_element={temp}
    )
    
    # Create an AAS
    aas = model.AssetAdministrationShell(
        id_='https://example.com/aas/sensor1',
        id_short='Sensor1',
        asset_information=model.AssetInformation(
            global_asset_id="https://example.com/assets/sensor1",
            asset_kind=model.AssetKind.INSTANCE
        ),
        submodel={model.ModelReference.from_referable(submodel)}
    )
    
    return aas, {'https://example.com/sensors/temp': submodel}

def test_security_manager():
    """Test basic security manager functionality."""
    manager = SecurityManager()
    
    # Set up policies
    manager.set_security_policy('resource1', SecurityLevel.MEDIUM)
    manager.set_role_permissions('admin', 'resource1', AccessRight.FULL)
    
    # Create contexts
    admin_context = create_security_context(
        'admin1',
        {'admin'},
        SecurityLevel.HIGH
    )
    user_context = create_security_context(
        'user1',
        {'user'},
        SecurityLevel.LOW
    )
    
    # Test access
    assert manager.check_access(admin_context, 'resource1', AccessRight.WRITE)
    with pytest.raises(Exception):
        manager.check_access(user_context, 'resource1', AccessRight.READ)

def test_audit_logging():
    """Test audit logging functionality."""
    audit_log = AuditLog()
    
    # Create test event
    event = AuditEvent(
        timestamp=datetime.now(UTC),
        event_type='access_attempt',
        user_id='test_user',
        resource_id='test_resource',
        action='read',
        status='success'
    )
    
    # Log event
    audit_log.log_event(event)
    
    # Test retrieval
    events = audit_log.get_events(user_id='test_user')
    assert len(events) == 1
    assert events[0].user_id == 'test_user'
    assert events[0].event_type == 'access_attempt'
    
    # Test filtering
    events = audit_log.get_events(event_type='other_type')
    assert len(events) == 0

def test_secure_aas():
    """Test secure AAS wrapper."""
    aas, submodels = create_test_aas()
    manager = SecurityManager()
    provider = DictProvider(submodels)
    
    # Set up security for AAS and submodel
    manager.set_security_policy('Sensor1', SecurityLevel.MEDIUM)
    manager.set_security_policy('TempSensor', SecurityLevel.MEDIUM)
    manager.set_role_permissions('admin', 'Sensor1', AccessRight.FULL)
    manager.set_role_permissions('operator', 'Sensor1', AccessRight.READ)
    manager.set_role_permissions('admin', 'TempSensor', AccessRight.FULL)
    manager.set_role_permissions('operator', 'TempSensor', AccessRight.READ)
    
    # Set up security for submodel elements
    manager.set_security_policy('Temperature', SecurityLevel.MEDIUM)
    manager.set_role_permissions('admin', 'Temperature', AccessRight.FULL)
    manager.set_role_permissions('operator', 'Temperature', AccessRight.READ)
    
    secure_aas = SecureAAS(aas, manager, provider)
    
    # Create contexts
    admin_context = create_security_context(
        'admin1',
        {'admin'},
        SecurityLevel.HIGH
    )
    operator_context = create_security_context(
        'operator1',
        {'operator'},
        SecurityLevel.MEDIUM
    )
    
    # Test admin access
    submodel = secure_aas.get_submodel(admin_context, 'TempSensor')
    assert submodel is not None
    
    temp_element = submodel.get_element(admin_context, 'Temperature')
    assert temp_element is not None
    assert temp_element.get_value(admin_context) == 25.5
    
    # Test operator access (read-only)
    submodel = secure_aas.get_submodel(operator_context, 'TempSensor')
    assert submodel is not None
    
    temp_element = submodel.get_element(operator_context, 'Temperature')
    assert temp_element is not None
    assert temp_element.get_value(operator_context) == 25.5
    
    # Test operator write access (should fail)
    with pytest.raises(Exception):
        temp_element.set_value(operator_context, 26.0) 