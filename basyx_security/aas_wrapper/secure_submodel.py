"""
Secure submodel wrapper implementation for BaSyx Security Layer.
"""

from typing import Dict, Optional

from basyx.aas import model

from ..core import AccessRight, SecurityContext, SecurityManager, SecurityViolation
from .secure_element import SecureElement


class SecureSubmodel:
    """
    Security wrapper for AAS submodels.
    """

    def __init__(self, submodel: model.Submodel, security_manager: SecurityManager):
        self._submodel = submodel
        self._security_manager = security_manager
        self._secure_elements: Dict[str, SecureElement] = {}

        # Wrap all submodel elements
        for element in submodel.submodel_element:
            self._secure_elements[element.id_short] = SecureElement(element, security_manager)

    def get_element(self, context: SecurityContext, element_id: str) -> Optional[SecureElement]:
        """
        Get a secure element by ID with security check.

        Args:
            context: Security context for the request
            element_id: ID of the element to retrieve

        Returns:
            SecureElement if found and accessible, None otherwise

        Raises:
            SecurityViolation: If access is denied
        """
        if not self._security_manager.check_access(
            context, self._submodel.id_short, AccessRight.READ
        ):
            raise SecurityViolation(f"Access denied to read submodel {self._submodel.id_short}")

        return self._secure_elements.get(element_id)

    def add_element(self, context: SecurityContext, element: model.Referable) -> None:
        """
        Add a new element with security check.

        Args:
            context: Security context for the request
            element: Element to add

        Raises:
            SecurityViolation: If access is denied
        """
        if not self._security_manager.check_access(
            context, self._submodel.id_short, AccessRight.WRITE
        ):
            raise SecurityViolation(f"Access denied to modify submodel {self._submodel.id_short}")

        self._submodel.submodel_element.add(element)
        self._secure_elements[element.id_short] = SecureElement(element, self._security_manager)

    @property
    def submodel(self) -> model.Submodel:
        """Get the wrapped submodel."""
        return self._submodel
