"""
Security-related enumerations for the BaSyx Security Layer.
"""

from enum import Enum, auto

class SecurityLevel(Enum):
    """Security levels for access control."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class AccessRight(Enum):
    """Access rights for AAS elements."""
    NONE = auto()
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    FULL = auto() 