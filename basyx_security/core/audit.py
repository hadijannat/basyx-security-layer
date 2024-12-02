"""
Audit logging implementation for BaSyx Security Layer.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class AuditEvent:
    """
    Represents a security-related event that should be logged.

    Attributes:
        timestamp: When the event occurred
        event_type: Type of the event (e.g., 'access_denied', 'login_attempt')
        user_id: ID of the user who triggered the event
        resource_id: ID of the resource being accessed
        action: The action being performed
        status: Outcome of the event (e.g., 'success', 'failure')
        details: Additional event details
    """

    timestamp: datetime
    event_type: str
    user_id: str
    resource_id: str
    action: str
    status: str
    details: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert the event to a dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "status": self.status,
            "details": self.details or {},
        }


class AuditLog:
    """
    Handles security audit logging.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the audit log.

        Args:
            log_file: Optional path to the log file
        """
        self.events: List[AuditEvent] = []
        self.log_file = log_file

        if log_file:
            self.logger = logging.getLogger("security_audit")
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_event(self, event: AuditEvent) -> None:
        """
        Log a security event.

        Args:
            event: The event to log
        """
        self.events.append(event)

        if self.log_file:
            event_dict = event.to_dict()
            self.logger.info(json.dumps(event_dict))

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AuditEvent]:
        """
        Get filtered audit events.

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_time: Filter events after this time
            end_time: Filter events before this time

        Returns:
            List of matching audit events
        """
        filtered_events = self.events

        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]

        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]

        return filtered_events

    def clear(self) -> None:
        """Clear all audit events."""
        self.events.clear()
