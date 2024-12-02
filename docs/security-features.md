# Security Features

The BaSyx Security Layer provides comprehensive security features to protect your Asset Administration Shell implementations.

## Core Security Features

### Role-Based Access Control (RBAC)

RBAC allows you to define and manage access rights based on user roles:

```python
# Set up role permissions
security_manager.set_role_permissions('admin', 'resource1', AccessRight.FULL)
security_manager.set_role_permissions('operator', 'resource1', AccessRight.READ)
```

### Security Levels

Define different security levels for resources:

```python
# Set security levels
security_manager.set_security_policy('resource1', SecurityLevel.HIGH)
security_manager.set_security_policy('resource2', SecurityLevel.MEDIUM)
```

## Advanced Security Features

### Rate Limiting

Protect your resources from abuse with rate limiting:

```python
from basyx_security import RateLimiter, RateLimit

# Create rate limiter
rate_limiter = RateLimiter()

# Add rate limits
rate_limiter.add_limit(
    'resource1',
    RateLimit(
        requests=100,      # Maximum requests
        window_seconds=60, # Time window
        block_seconds=300  # Block duration if exceeded
    )
)

# Check rate limit
try:
    rate_limiter.check_rate_limit('resource1', 'client1')
    # Process request
except RateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
```

### Session Management

Manage user sessions with automatic expiration:

```python
from basyx_security import SessionManager
from datetime import timedelta

# Create session manager
session_manager = SessionManager(
    session_timeout_minutes=30,
    cleanup_interval_minutes=5
)

# Create a session
session = session_manager.create_session(
    user_id='user1',
    roles={'admin'},
    session_duration=timedelta(hours=1)  # Optional custom duration
)

# Validate and use session
if active_session := session_manager.get_session(session.session_id):
    print(f"Active session for user: {active_session.user_id}")
else:
    print("Session expired or invalid")

# Invalidate session
session_manager.invalidate_session(session.session_id)
```

### Audit Logging

Track security events with comprehensive audit logging:

```python
from basyx_security import SecurityAuditor

# Create auditor
auditor = SecurityAuditor(log_file="security_audit.log")

# Log security events
auditor.log_access_attempt(
    context=security_context,
    resource_id="resource1",
    action="read",
    status="success"
)
```

## Best Practices

1. **Rate Limiting**
   - Set appropriate rate limits based on resource sensitivity
   - Use shorter time windows for sensitive operations
   - Implement gradual blocking (increase block duration for repeat offenders)

2. **Session Management**
   - Use shorter session timeouts for sensitive operations
   - Implement session rotation for long-lived sessions
   - Invalidate all sessions when changing user permissions

3. **Audit Logging**
   - Log all security-relevant events
   - Include sufficient context in log entries
   - Regularly review audit logs
   - Set up alerts for security violations

4. **General Security**
   - Use HTTPS for all communications
   - Implement proper authentication before authorization
   - Regularly review and update security policies
   - Follow the principle of least privilege

## Configuration Examples

### Complete Security Setup

```python
from basyx_security import (
    SecurityManager,
    RateLimiter,
    SessionManager,
    SecurityAuditor
)

# Initialize security components
security_manager = SecurityManager()
rate_limiter = RateLimiter()
session_manager = SessionManager()
auditor = SecurityAuditor()

# Configure rate limits
rate_limiter.add_limit(
    'api',
    RateLimit(requests=1000, window_seconds=3600)  # 1000 requests per hour
)
rate_limiter.add_limit(
    'admin_api',
    RateLimit(requests=100, window_seconds=3600)   # 100 requests per hour
)

# Set up security policies
security_manager.set_security_policy('user_data', SecurityLevel.HIGH)
security_manager.set_role_permissions('admin', 'user_data', AccessRight.FULL)
security_manager.set_role_permissions('user', 'user_data', AccessRight.READ)

# Create and manage sessions
session = session_manager.create_session('user1', {'user'})
``` 