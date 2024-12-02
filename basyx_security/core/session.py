"""
Session management implementation for BaSyx Security Layer.
"""

import time
import uuid
from typing import Dict, Optional, Set
from dataclasses import dataclass
from threading import Lock, Thread
from datetime import datetime, timedelta

@dataclass
class Session:
    """
    Represents a user session.
    
    Attributes:
        session_id: Unique session identifier
        user_id: User identifier
        roles: User roles
        created_at: Session creation time
        expires_at: Session expiration time
        last_accessed: Last session access time
    """
    session_id: str
    user_id: str
    roles: Set[str]
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime

class SessionManager:
    """
    Manages user sessions with automatic cleanup.
    """
    
    def __init__(
        self,
        session_timeout_minutes: int = 30,
        cleanup_interval_minutes: int = 5
    ):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Session timeout in minutes
            cleanup_interval_minutes: Cleanup interval in minutes
        """
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, Set[str]] = {}
        self._session_timeout = timedelta(minutes=session_timeout_minutes)
        self._cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        self._lock = Lock()
        
        # Start cleanup thread
        self._cleanup_thread = Thread(
            target=self._cleanup_expired_sessions,
            daemon=True
        )
        self._cleanup_thread.start()
        
    def create_session(
        self,
        user_id: str,
        roles: Set[str],
        session_duration: Optional[timedelta] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            user_id: User identifier
            roles: User roles
            session_duration: Optional custom session duration
            
        Returns:
            New session object
        """
        now = datetime.utcnow()
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            roles=roles,
            created_at=now,
            expires_at=now + (session_duration or self._session_timeout),
            last_accessed=now
        )
        
        with self._lock:
            self._sessions[session.session_id] = session
            if user_id not in self._user_sessions:
                self._user_sessions[user_id] = set()
            self._user_sessions[user_id].add(session.session_id)
            
        return session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get and validate a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if valid, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
                
            now = datetime.utcnow()
            if now > session.expires_at:
                self._remove_session(session)
                return None
                
            # Update last access time and expiration
            session.last_accessed = now
            session.expires_at = now + self._session_timeout
            return session
            
    def invalidate_session(self, session_id: str) -> None:
        """
        Invalidate a specific session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session := self._sessions.get(session_id):
                self._remove_session(session)
                
    def invalidate_user_sessions(self, user_id: str) -> None:
        """
        Invalidate all sessions for a user.
        
        Args:
            user_id: User identifier
        """
        with self._lock:
            if session_ids := self._user_sessions.get(user_id):
                for session_id in session_ids.copy():
                    if session := self._sessions.get(session_id):
                        self._remove_session(session)
                        
    def _remove_session(self, session: Session) -> None:
        """Remove a session and its references."""
        session_id = session.session_id
        user_id = session.user_id
        
        if session_id in self._sessions:
            del self._sessions[session_id]
            
        if user_id in self._user_sessions:
            self._user_sessions[user_id].discard(session_id)
            if not self._user_sessions[user_id]:
                del self._user_sessions[user_id]
                
    def _cleanup_expired_sessions(self) -> None:
        """Periodically clean up expired sessions."""
        while True:
            time.sleep(self._cleanup_interval.total_seconds())
            
            with self._lock:
                now = datetime.utcnow()
                expired = [
                    session for session in self._sessions.values()
                    if now > session.expires_at
                ]
                for session in expired:
                    self._remove_session(session) 