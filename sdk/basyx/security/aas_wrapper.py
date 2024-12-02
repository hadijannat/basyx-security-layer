"""
Security wrapper for Asset Administration Shell.

This module provides secure wrappers for AAS components, implementing:
- Access control for AAS elements
- Secure value access and modification
- Role-based access control integration
- Security context validation
"""

from typing import Optional, Dict, Any, Set
from basyx.aas import model
from .core import SecurityContext, SecurityManager, AccessRight, SecurityViolation
import logging

class SecureElement:
    """Base class for secure AAS elements"""
    
    def __init__(self, element: model.Referable, security_manager: SecurityManager):
        self._element = element
        self._security_manager = security_manager
    
    def get_value(self, context: SecurityContext) -> Any:
        """Get element value with security check"""
        if not hasattr(self._element, 'value'):
            raise ValueError(f"Element {self._element.id_short} does not support value access")
            
        # Use id_ for identifiable objects, otherwise use parent's id + id_short
        element_id = getattr(self._element, 'id_', None)
        if element_id is None:
            parent = getattr(self._element, 'parent', None)
            if parent is not None:
                parent_id = getattr(parent, 'id', getattr(parent, 'id_', None))
                if parent_id:
                    element_id = f"{parent_id}/{self._element.id_short}"
                else:
                    element_id = self._element.id_short
            else:
                element_id = self._element.id_short
            
        if self._security_manager.check_access(context, element_id, AccessRight.READ):
            logging.info(f"Value read by {context.user_id} from {element_id}")
            return self._element.value
            
        raise SecurityViolation(f"Access denied to read {element_id}")
    
    def set_value(self, context: SecurityContext, value: Any):
        """Set element value with security check"""
        if not hasattr(self._element, 'value'):
            raise ValueError(f"Element {self._element.id_short} does not support value modification")
            
        # Use id_ for identifiable objects, otherwise use parent's id + id_short
        element_id = getattr(self._element, 'id_', None)
        if element_id is None:
            parent = getattr(self._element, 'parent', None)
            if parent is not None:
                parent_id = getattr(parent, 'id', getattr(parent, 'id_', None))
                if parent_id:
                    element_id = f"{parent_id}/{self._element.id_short}"
                else:
                    element_id = self._element.id_short
            else:
                element_id = self._element.id_short
            
        if self._security_manager.check_access(context, element_id, AccessRight.WRITE):
            self._element.value = value
            logging.info(f"Value updated by {context.user_id} for {element_id}")
        else:
            raise SecurityViolation(f"Access denied to write to {element_id}")
    
    def invoke_operation(self, context: SecurityContext, params: Optional[Dict] = None) -> Any:
        """Invoke operation with security check"""
        if not isinstance(self._element, model.Operation):
            raise ValueError(f"Element {self._element.id_short} does not support operations")
            
        # Use id_ for identifiable objects, otherwise use parent's id + id_short
        element_id = getattr(self._element, 'id_', None)
        if element_id is None:
            parent = getattr(self._element, 'parent', None)
            if parent is not None:
                parent_id = getattr(parent, 'id', getattr(parent, 'id_', None))
                if parent_id:
                    element_id = f"{parent_id}/{self._element.id_short}"
                else:
                    element_id = self._element.id_short
            else:
                element_id = self._element.id_short
            
        if self._security_manager.check_access(context, element_id, AccessRight.EXECUTE):
            result = self._element.invoke(params or {})
            logging.info(f"Operation invoked by {context.user_id} on {element_id}")
            return result
            
        raise SecurityViolation(f"Access denied to execute operation on {element_id}")

class SecureSubmodel:
    """Security wrapper for Submodel"""
    
    def __init__(self, submodel: model.Submodel, security_manager: SecurityManager):
        self._submodel = submodel
        self._security_manager = security_manager
        self._secure_elements: Dict[str, SecureElement] = {}
    
    def get_element(self, context: SecurityContext, element_id: str) -> SecureElement:
        """Get secure element with security check"""
        if not self._security_manager.check_access(context, self._submodel.id, AccessRight.READ):
            raise SecurityViolation(f"Access denied to submodel {self._submodel.id}")
        
        if element_id not in self._secure_elements:
            element = next((e for e in self._submodel.submodel_element if e.id_short == element_id), None)
            if element is None:
                raise ValueError(f"Element {element_id} not found in submodel {self._submodel.id_short}")
            self._secure_elements[element_id] = SecureElement(element, self._security_manager)
        
        return self._secure_elements[element_id]
    
    def add_element(self, context: SecurityContext, element: model.SubmodelElement):
        """Add element with security check"""
        if not self._security_manager.check_access(context, self._submodel.id, AccessRight.WRITE):
            raise SecurityViolation(f"Access denied to modify submodel {self._submodel.id}")
        
        self._submodel.submodel_element.add(element)
        self._secure_elements.clear()  # Clear cache
        logging.info(f"Element {element.id_short} added to {self._submodel.id} by {context.user_id}")

class SecureAAS:
    """Security wrapper for Asset Administration Shell"""
    
    def __init__(self, aas: model.AssetAdministrationShell, security_manager: SecurityManager,
                 object_provider: Optional[model.AbstractObjectProvider] = None):
        self._aas = aas
        self._security_manager = security_manager
        self._secure_submodels: Dict[str, SecureSubmodel] = {}
        self._object_provider = object_provider or model.DictObjectStore([aas])
    
    def get_submodel(self, context: SecurityContext, submodel_id: str) -> SecureSubmodel:
        """Get secure submodel with security check"""
        if not self._security_manager.check_access(context, self._aas.id, AccessRight.READ):
            raise SecurityViolation(f"Access denied to AAS {self._aas.id}")
        
        if submodel_id not in self._secure_submodels:
            # Try to find the submodel by resolving each reference
            for submodel_ref in self._aas.submodel:
                try:
                    submodel = submodel_ref.resolve(self._object_provider)
                    if submodel.id_short == submodel_id:
                        self._secure_submodels[submodel_id] = SecureSubmodel(submodel, self._security_manager)
                        return self._secure_submodels[submodel_id]
                except Exception as e:
                    logging.warning(f"Failed to resolve submodel reference: {str(e)}")
                    continue
            
            raise ValueError(f"Submodel {submodel_id} not found in AAS {self._aas.id_short}")
        
        return self._secure_submodels[submodel_id]
    
    def add_submodel(self, context: SecurityContext, submodel: model.Submodel):
        """Add submodel with security check"""
        if not self._security_manager.check_access(context, self._aas.id, AccessRight.WRITE):
            raise SecurityViolation(f"Access denied to modify AAS {self._aas.id}")
        
        self._aas.submodel.add(model.ModelReference.from_referable(submodel))
        if isinstance(self._object_provider, model.DictObjectStore):
            self._object_provider.add(submodel)  # Add to object store for resolution
        self._secure_submodels.clear()  # Clear cache
        logging.info(f"Submodel {submodel.id_short} added to {self._aas.id} by {context.user_id}")
    
    def get_asset_information(self, context: SecurityContext) -> model.AssetInformation:
        """Get asset information with security check"""
        if not self._security_manager.check_access(context, self._aas.id, AccessRight.READ):
            raise SecurityViolation(f"Access denied to read AAS {self._aas.id}")
        
        return self._aas.asset_information