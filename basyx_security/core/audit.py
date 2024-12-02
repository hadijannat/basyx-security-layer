"""
Audit logging implementation for BaSyx Security Layer.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class AuditEvent:
    """
    Represents a security-related audit event.
    
    Attributes:
        timestamp: When the event occurred
        event_type: Type of security event
        user_id: ID of the user who triggered the event
        resource_id: ID of the resource being accessed
        action: Action being performed
        roles: Roles of the user
        security_level: Security level of the context
        status: Success or failure
        details: Additional event details
    """
    timestamp: datetime
    event_type: str
    user_id: str
    resource_id: str
    action: str
    roles: set[str]
    security_level: str
    status: str
    details: Optional[Dict[str, Any]] = None

class SecurityAuditor:
    """
    Handles security audit logging.
    """
    
    def __init__(self, log_file: str = "security_audit.log"):
        """Initialize the security auditor."""
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_event(self, event: AuditEvent) -> None:
        """
        Log a security event.
        
        Args:
            event: The security event to log
        """
        event_dict = asdict(event)
        event_dict["timestamp"] = event.timestamp.isoformat()
        event_dict["roles"] = list(event.roles)
        
        self.logger.info(json.dumps(event_dict))
        
        # Also log to console if it's a failure
        if event.status == "failure":
            self.logger.warning(
                f"Security violation: {event.event_type} by {event.user_id} "
                f"on {event.resource_id}"
            )
            
    def log_access_attempt(
        self,
        context: "SecurityContext",
        resource_id: str,
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an access attempt.
        
        Args:
            context: Security context of the attempt
            resource_id: ID of the resource being accessed
            action: Action being attempted
            status: Success or failure
            details: Additional details about the attempt
        """
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            event_type="access_attempt",
            user_id=context.user_id,
            resource_id=resource_id,
            action=action,
            roles=context.roles,
            security_level=context.security_level.name,
            status=status,
            details=details
        )
        self.log_event(event)
        
    def log_policy_change(
        self,
        user_id: str,
        resource_id: str,
        action: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log a security policy change.
        
        Args:
            user_id: ID of the user making the change
            resource_id: ID of the resource being modified
            action: Type of policy change
            details: Details of the policy change
        """
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            event_type="policy_change",
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            roles=set(),  # Not applicable for policy changes
            security_level="SYSTEM",
            status="success",
            details=details
        )
        self.log_event(event) 