"""
Core security module for BaSyx Python SDK.

This module provides the core security functionality including:
- Security Levels
- Access Rights
- Security Context
- Security Manager
"""

import datetime
import enum
import logging
from typing import Any, Dict, Optional, Set

import jwt


class SecurityLevel(enum.Enum):
    """Security levels for access control"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class AccessRight(enum.IntEnum):
    """Access rights for resources"""

    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    FULL = 4


class SecurityViolation(Exception):
    """Exception raised for security violations"""

    pass


class SecurityContext:
    """Security context containing user information and credentials"""

    def __init__(
        self,
        user_id: str,
        roles: Set[str],
        security_level: SecurityLevel,
        token: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        self.user_id = user_id
        self.roles = roles
        self.security_level = security_level
        self.token = token
        self.metadata = metadata or {}


def create_security_context(
    user_id: str, roles: Set[str], security_level: SecurityLevel, metadata: Optional[Dict] = None
) -> SecurityContext:
    """Create a new security context"""
    return SecurityContext(user_id, roles, security_level, metadata=metadata)


class SecurityManager:
    """Manages security policies and access control"""

    def __init__(self, jwt_secret: str = "your-secret-key"):
        self._security_policies: Dict[str, SecurityLevel] = {}
        self._role_permissions: Dict[str, Dict[str, AccessRight]] = {}
        self._jwt_secret = jwt_secret

    def set_security_policy(self, resource_id: str, level: SecurityLevel):
        """Set security level for a resource"""
        self._security_policies[resource_id] = level
        logging.info(f"Security policy set for {resource_id}: {level}")

    def set_role_permissions(self, role: str, resource_id: str, access: AccessRight):
        """Set role permissions for a resource"""
        if role not in self._role_permissions:
            self._role_permissions[role] = {}
        self._role_permissions[role][resource_id] = access
        logging.info(
            f"Role permissions set - Role: {role}, Resource: {resource_id}, Access: {access}"
        )

    def check_access(
        self, context: SecurityContext, resource_id: str, required_access: AccessRight
    ) -> bool:
        """Check if access is allowed based on security context"""
        # Verify security level
        required_level = self._security_policies.get(resource_id, SecurityLevel.LOW)
        if context.security_level.value < required_level.value:
            logging.warning(
                f"Security level violation - User: {context.user_id}, " f"Resource: {resource_id}"
            )
            return False

        # Check role permissions
        for role in context.roles:
            role_perms = self._role_permissions.get(role, {})
            access_right = role_perms.get(resource_id, AccessRight.NONE)

            if access_right == AccessRight.FULL:
                return True

            if required_access == AccessRight.READ and access_right.value >= AccessRight.READ.value:
                return True

            if (
                required_access == AccessRight.WRITE
                and access_right.value >= AccessRight.WRITE.value
            ):
                return True

            if (
                required_access == AccessRight.EXECUTE
                and access_right.value >= AccessRight.EXECUTE.value
            ):
                return True

        logging.warning(
            f"Access denied - User: {context.user_id}, Resource: {resource_id}, "
            f"Required: {required_access}"
        )
        return False

    def create_token(
        self, context: SecurityContext, expiry: datetime.timedelta = datetime.timedelta(hours=1)
    ) -> str:
        """Create JWT token from security context"""
        payload = {
            "sub": context.user_id,
            "roles": list(context.roles),
            "security_level": context.security_level.value,
            "metadata": context.metadata,
            "exp": datetime.datetime.now(datetime.UTC) + expiry,
            "iat": datetime.datetime.now(datetime.UTC),
        }
        return jwt.encode(payload, self._jwt_secret, algorithm="HS256")

    def verify_token(self, token: str) -> SecurityContext:
        """Verify JWT token and return security context"""
        try:
            payload = jwt.decode(token, self._jwt_secret, algorithms=["HS256"])
            return SecurityContext(
                user_id=payload["sub"],
                roles=set(payload["roles"]),
                security_level=SecurityLevel(payload["security_level"]),
                token=token,
                metadata=payload.get("metadata", {}),
            )
        except jwt.InvalidTokenError as e:
            raise SecurityViolation(f"Invalid token: {str(e)}")
