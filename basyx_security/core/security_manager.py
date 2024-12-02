"""
Security manager implementation for BaSyx Security Layer.
"""

from typing import Dict, Set, Optional, Any
from .enums import SecurityLevel, AccessRight
from .security_context import SecurityContext
from .audit import SecurityAuditor

class SecurityViolation(Exception):
    """Raised when a security violation occurs."""
    pass

class SecurityManager:
    """
    Manages security policies and access control for AAS elements.
    """
    
    def __init__(self, audit_log_file: Optional[str] = None):
        self._security_policies: Dict[str, SecurityLevel] = {}
        self._role_permissions: Dict[str, Dict[str, AccessRight]] = {}
        self._auditor = SecurityAuditor(
            audit_log_file or "security_audit.log"
        )
        
    def set_security_policy(
        self,
        resource_id: str,
        level: SecurityLevel,
        admin_context: Optional[SecurityContext] = None
    ) -> None:
        """
        Set the security level required for a resource.
        
        Args:
            resource_id: Identifier of the resource
            level: Required security level
            admin_context: Optional context of the admin making the change
        """
        self._security_policies[resource_id] = level
        
        # Audit the policy change
        self._auditor.log_policy_change(
            user_id=admin_context.user_id if admin_context else "SYSTEM",
            resource_id=resource_id,
            action="set_security_policy",
            details={
                "security_level": level.name
            }
        )
        
    def set_role_permissions(
        self,
        role: str,
        resource_id: str,
        access_right: AccessRight,
        admin_context: Optional[SecurityContext] = None
    ) -> None:
        """
        Set permissions for a role on a specific resource.
        
        Args:
            role: Role name
            resource_id: Identifier of the resource
            access_right: Access right to grant
            admin_context: Optional context of the admin making the change
        """
        if role not in self._role_permissions:
            self._role_permissions[role] = {}
        self._role_permissions[role][resource_id] = access_right
        
        # Audit the permission change
        self._auditor.log_policy_change(
            user_id=admin_context.user_id if admin_context else "SYSTEM",
            resource_id=resource_id,
            action="set_role_permissions",
            details={
                "role": role,
                "access_right": access_right.name
            }
        )
        
    def check_access(
        self,
        context: SecurityContext,
        resource_id: str,
        required_right: AccessRight
    ) -> bool:
        """
        Check if the security context has sufficient access rights.
        
        Args:
            context: Security context of the request
            resource_id: Identifier of the resource
            required_right: Required access right
            
        Returns:
            bool: True if access is granted, False otherwise
            
        Raises:
            SecurityViolation: If security requirements are not met
        """
        try:
            # Check security level
            if resource_id in self._security_policies:
                required_level = self._security_policies[resource_id]
                if context.security_level.value < required_level.value:
                    raise SecurityViolation(
                        f"Insufficient security level. Required: {required_level}, "
                        f"Provided: {context.security_level}"
                    )
            
            # Check role permissions
            for role in context.roles:
                if role in self._role_permissions:
                    role_perms = self._role_permissions[role]
                    if resource_id in role_perms:
                        granted_right = role_perms[resource_id]
                        if granted_right == AccessRight.FULL:
                            self._audit_access_attempt(
                                context, resource_id, required_right, "success"
                            )
                            return True
                        if granted_right.value >= required_right.value:
                            self._audit_access_attempt(
                                context, resource_id, required_right, "success"
                            )
                            return True
            
            # Access denied
            self._audit_access_attempt(
                context, resource_id, required_right, "failure",
                {"reason": "insufficient_permissions"}
            )
            return False
            
        except SecurityViolation as e:
            # Audit the security violation
            self._audit_access_attempt(
                context, resource_id, required_right, "failure",
                {"reason": "insufficient_security_level"}
            )
            raise e
        
    def _audit_access_attempt(
        self,
        context: SecurityContext,
        resource_id: str,
        required_right: AccessRight,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an access attempt to the audit log."""
        self._auditor.log_access_attempt(
            context=context,
            resource_id=resource_id,
            action=required_right.name,
            status=status,
            details=details
        )
        
    def get_security_level(self, resource_id: str) -> Optional[SecurityLevel]:
        """Get the security level required for a resource."""
        return self._security_policies.get(resource_id)
        
    def get_role_permissions(
        self,
        role: str,
        resource_id: str
    ) -> Optional[AccessRight]:
        """Get the permissions granted to a role for a resource."""
        return self._role_permissions.get(role, {}).get(resource_id) 