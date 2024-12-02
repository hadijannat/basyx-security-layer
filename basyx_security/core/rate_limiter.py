"""
Rate limiting implementation for BaSyx Security Layer.
"""

import time
from dataclasses import dataclass
from typing import Dict, Optional
from collections import defaultdict
from threading import Lock

@dataclass
class RateLimit:
    """
    Rate limit configuration.
    
    Attributes:
        requests: Maximum number of requests
        window_seconds: Time window in seconds
        block_seconds: Time to block if limit exceeded
    """
    requests: int
    window_seconds: int
    block_seconds: int = 300  # 5 minutes default block

class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, wait_time: float):
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded. Try again in {wait_time:.1f} seconds.")

class RateLimiter:
    """
    Implements rate limiting for API access.
    """
    
    def __init__(self):
        self._limits: Dict[str, RateLimit] = {}
        self._requests: Dict[str, Dict[str, list[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self._blocks: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._lock = Lock()
        
    def add_limit(self, resource_id: str, limit: RateLimit) -> None:
        """
        Add a rate limit for a resource.
        
        Args:
            resource_id: Resource identifier
            limit: Rate limit configuration
        """
        self._limits[resource_id] = limit
        
    def check_rate_limit(
        self,
        resource_id: str,
        client_id: str,
        current_time: Optional[float] = None
    ) -> None:
        """
        Check if a request is within rate limits.
        
        Args:
            resource_id: Resource being accessed
            client_id: Client making the request
            current_time: Current time (for testing)
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        if resource_id not in self._limits:
            return
            
        current_time = current_time or time.time()
        limit = self._limits[resource_id]
        
        with self._lock:
            # Check if client is blocked
            if client_id in self._blocks[resource_id]:
                block_until = self._blocks[resource_id][client_id]
                if current_time < block_until:
                    wait_time = block_until - current_time
                    raise RateLimitExceeded(wait_time)
                else:
                    del self._blocks[resource_id][client_id]
            
            # Clean old requests
            window_start = current_time - limit.window_seconds
            requests = self._requests[resource_id][client_id]
            requests = [t for t in requests if t > window_start]
            self._requests[resource_id][client_id] = requests
            
            # Check limit
            if len(requests) >= limit.requests:
                # Block the client
                self._blocks[resource_id][client_id] = current_time + limit.block_seconds
                raise RateLimitExceeded(limit.block_seconds)
            
            # Record request
            requests.append(current_time)
            
    def get_remaining_requests(
        self,
        resource_id: str,
        client_id: str
    ) -> Optional[int]:
        """
        Get remaining requests allowed in current window.
        
        Args:
            resource_id: Resource identifier
            client_id: Client identifier
            
        Returns:
            Number of remaining requests or None if no limit
        """
        if resource_id not in self._limits:
            return None
            
        limit = self._limits[resource_id]
        current_time = time.time()
        
        with self._lock:
            if client_id in self._blocks[resource_id]:
                return 0
                
            window_start = current_time - limit.window_seconds
            requests = self._requests[resource_id][client_id]
            recent_requests = len([t for t in requests if t > window_start])
            
            return max(0, limit.requests - recent_requests) 