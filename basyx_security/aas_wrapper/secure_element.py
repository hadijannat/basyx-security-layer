"""
Secure element wrapper implementation for BaSyx Security Layer.
"""

from typing import Any, Optional
from basyx.aas import model
from ..core import SecurityContext, SecurityManager, AccessRight, SecurityViolation


class SecureElement:
    """
    Security wrapper for AAS elements.
    """

    def __init__(self, element: model.Referable, security_manager: SecurityManager):
        self._element = element
        self._security_manager = security_manager

    def get_value(self, context: SecurityContext) -> Any:
        """
        Get the value of the element with security check.

        Args:
            context: Security context for the request

        Returns:
            The element's value

        Raises:
            SecurityViolation: If access is denied
        """
        if not self._security_manager.check_access(
            context, self._element.id_short, AccessRight.READ
        ):
            raise SecurityViolation(f"Access denied to read {self._element.id_short}")
        return self._element.value

    def set_value(self, context: SecurityContext, value: Any) -> None:
        """
        Set the value of the element with security check.

        Args:
            context: Security context for the request
            value: New value to set

        Raises:
            SecurityViolation: If access is denied
        """
        if not self._security_manager.check_access(
            context, self._element.id_short, AccessRight.WRITE
        ):
            raise SecurityViolation(f"Access denied to write to {self._element.id_short}")
        self._element.value = value

    @property
    def element(self) -> model.Referable:
        """Get the wrapped element."""
        return self._element
