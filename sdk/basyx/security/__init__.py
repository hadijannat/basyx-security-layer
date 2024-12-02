"""
BaSyx Security Module

This module provides security features for the BaSyx Python SDK, including:
- Role-Based Access Control (RBAC)
- Security Levels
- Access Rights Management
- JWT-based Authentication
- Secure AAS Wrappers
"""

from .aas_wrapper import SecureAAS, SecureElement, SecureSubmodel
from .core import (
    AccessRight,
    SecurityContext,
    SecurityLevel,
    SecurityManager,
    SecurityViolation,
    create_security_context,
)

__version__ = "0.1.0"
