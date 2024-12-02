"""
BaSyx Security Layer

A security implementation layer for the Eclipse BaSyx Python SDK.
"""

from .core import (
    SecurityManager,
    SecurityContext,
    create_security_context,
    SecurityLevel,
    AccessRight,
    SecurityViolation,
    AuditLog,
    AuditEvent
)
from .aas_wrapper.secure_aas import SecureAAS
from .aas_wrapper.secure_submodel import SecureSubmodel
from .aas_wrapper.secure_element import SecureElement
from .aas_wrapper.provider import SubmodelProvider, DictProvider

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
    "AuditLog",
    "AuditEvent",
    "SecureAAS",
    "SecureSubmodel",
    "SecureElement",
    "SubmodelProvider",
    "DictProvider"
] 