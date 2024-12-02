"""
Security manager implementation for BaSyx Security Layer.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Set

from .audit import AuditEvent, AuditLog
from .enums import AccessRight, SecurityLevel
from .security_context import SecurityContext


class SecurityViolation(Exception):
    """Raised when a security check fails."""

    pass


class SecurityManager:
    """
    Manages security policies and access control.
    """

    def __init__(self):
        """Initialize the security manager."""
        self._security_policies: Dict[str, SecurityLevel] = {}
        self._role_permissions: Dict[str, Dict[str, AccessRight]] = {}
        self._audit_log = AuditLog()

    def set_security_policy(self, resource_id: str, level: SecurityLevel) -> None:
        """
        Set the security level required for a resource.

        Args:
            resource_id: ID of the resource
            level: Required security level
        """
        self._security_policies[resource_id] = level

        self._audit_log.log_event(
            AuditEvent(
                timestamp=datetime.now(timezone.utc),
                event_type="policy_change",
                user_id="SYSTEM",
                resource_id=resource_id,
                action="set_security_level",
                status="success",
                details={"level": level.name},
            )
        )

    def set_role_permissions(self, role: str, resource_id: str, access: AccessRight) -> None:
        """
        Set permissions for a role on a resource.

        Args:
            role: Role name
            resource_id: ID of the resource
            access: Access rights to grant
        """
        if role not in self._role_permissions:
            self._role_permissions[role] = {}

        self._role_permissions[role][resource_id] = access

        self._audit_log.log_event(
            AuditEvent(
                timestamp=datetime.now(timezone.utc),
                event_type="policy_change",
                user_id="SYSTEM",
                resource_id=resource_id,
                action="set_role_permissions",
                status="success",
                details={"role": role, "access": access.name},
            )
        )

    def check_access(
        self, context: SecurityContext, resource_id: str, required_access: AccessRight
    ) -> bool:
        """
        Check if a security context has the required access to a resource.

        Args:
            context: Security context to check
            resource_id: ID of the resource
            required_access: Required access level

        Returns:
            True if access is granted

        Raises:
            SecurityViolation: If access is denied
        """
        # Check security level
        required_level = self._security_policies.get(resource_id, SecurityLevel.LOW)

        if context.security_level.value < required_level.value:
            self._audit_log.log_event(
                AuditEvent(
                    timestamp=datetime.now(timezone.utc),
                    event_type="access_denied",
                    user_id=context.user_id,
                    resource_id=resource_id,
                    action=required_access.name,
                    status="failure",
                    details={"reason": "insufficient_security_level"},
                )
            )
            raise SecurityViolation(f"Insufficient security level for {resource_id}")

        # Check role permissions
        has_permission = False
        for role in context.roles:
            if role in self._role_permissions:
                role_access = self._role_permissions[role].get(resource_id, AccessRight.NONE)
                if role_access == AccessRight.FULL or role_access == required_access:
                    has_permission = True
                    break

        if not has_permission:
            self._audit_log.log_event(
                AuditEvent(
                    timestamp=datetime.now(timezone.utc),
                    event_type="access_denied",
                    user_id=context.user_id,
                    resource_id=resource_id,
                    action=required_access.name,
                    status="failure",
                    details={"reason": "insufficient_permissions"},
                )
            )
            raise SecurityViolation(f"Insufficient permissions for {resource_id}")

        # Log successful access
        self._audit_log.log_event(
            AuditEvent(
                timestamp=datetime.now(timezone.utc),
                event_type="access_granted",
                user_id=context.user_id,
                resource_id=resource_id,
                action=required_access.name,
                status="success",
            )
        )

        return True

    @property
    def audit_log(self) -> AuditLog:
        """Get the audit log."""
        return self._audit_log
