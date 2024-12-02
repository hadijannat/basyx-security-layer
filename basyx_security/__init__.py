"""
BaSyx Security Layer

A security implementation layer for the Eclipse BaSyx Python SDK.
"""

from .aas_wrapper.provider import DictProvider, SubmodelProvider
from .aas_wrapper.secure_aas import SecureAAS
from .aas_wrapper.secure_element import SecureElement
from .aas_wrapper.secure_submodel import SecureSubmodel
from .core import (
    AccessRight,
    AuditEvent,
    AuditLog,
    SecurityContext,
    SecurityLevel,
    SecurityManager,
    SecurityViolation,
    create_security_context,
)

__version__ = "0.1.0"
__author__ = "Hadi Jannat"
__email__ = "h.jannat@example.com"

__all__ = [
    "AccessRight",
    "AuditEvent",
    "AuditLog",
    "DictProvider",
    "SecureAAS",
    "SecureElement",
    "SecureSubmodel",
    "SecurityContext",
    "SecurityLevel",
    "SecurityManager",
    "SecurityViolation",
    "SubmodelProvider",
    "create_security_context",
]
