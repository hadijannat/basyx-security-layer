"""
Security context implementation for BaSyx Security Layer.
"""

from dataclasses import dataclass
from typing import Set, Optional
from datetime import datetime

from .enums import SecurityLevel

@dataclass
class SecurityContext:
    """
    Represents the security context for access control decisions.
    
    Attributes:
        user_id: Unique identifier of the user
        roles: Set of roles assigned to the user
        security_level: Security clearance level of the user
        timestamp: When the context was created
        token: Optional authentication token
    """
    user_id: str
    roles: Set[str]
    security_level: SecurityLevel
    timestamp: datetime
    token: Optional[str] = None

def create_security_context(
    user_id: str,
    roles: Set[str],
    security_level: SecurityLevel,
    token: Optional[str] = None
) -> SecurityContext:
    """
    Create a new security context.

    Args:
        user_id: Unique identifier of the user
        roles: Set of roles assigned to the user
        security_level: Security clearance level
        token: Optional authentication token

    Returns:
        SecurityContext: A new security context instance
    """
    return SecurityContext(
        user_id=user_id,
        roles=roles,
        security_level=security_level,
        timestamp=datetime.utcnow(),
        token=token
    ) 