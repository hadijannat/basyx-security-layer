"""
BaSyx Security Layer

A security implementation layer for the Eclipse BaSyx Python SDK.
"""

from .core.security_manager import SecurityManager, SecurityViolation
from .core.security_context import SecurityContext, create_security_context
from .core.enums import SecurityLevel, AccessRight
from .core.audit import SecurityAuditor, AuditEvent
from .aas_wrapper.secure_aas import SecureAAS
from .aas_wrapper.secure_submodel import SecureSubmodel
from .aas_wrapper.secure_element import SecureElement

__version__ = "0.1.0"
__author__ = "Hadi Jannat"
__email__ = "h.jannat@example.com"

__all__ = [
    "SecurityManager",
    "SecurityContext",
    "create_security_context",
    "SecurityLevel",
    "AccessRight",
    "SecurityViolation",
    "SecurityAuditor",
    "AuditEvent",
    "SecureAAS",
    "SecureSubmodel",
    "SecureElement"
] 