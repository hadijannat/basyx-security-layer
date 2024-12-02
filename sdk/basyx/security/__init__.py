"""
BaSyx Security Module

This module provides security features for the BaSyx Python SDK, including:
- Role-Based Access Control (RBAC)
- Security Levels
- Access Rights Management
- JWT-based Authentication
- Secure AAS Wrappers
"""

from .core import (
    SecurityLevel,
    AccessRight,
    SecurityContext,
    SecurityViolation,
    SecurityManager,
    create_security_context,
)

from .aas_wrapper import SecureElement, SecureSubmodel, SecureAAS

__version__ = "0.1.0"
