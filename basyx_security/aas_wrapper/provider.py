"""
Provider interface for resolving references.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from basyx.aas import model

class SubmodelProvider(ABC):
    """Interface for resolving submodel references."""
    
    @abstractmethod
    def get_submodel(self, id_: str) -> Optional[model.Submodel]:
        """
        Get a submodel by ID.
        
        Args:
            id_: ID of the submodel to retrieve
            
        Returns:
            The submodel if found, None otherwise
        """
        pass

class DictProvider(SubmodelProvider):
    """Simple dictionary-based provider for testing."""
    
    def __init__(self, submodels: Dict[str, model.Submodel]):
        """
        Initialize the provider.
        
        Args:
            submodels: Dictionary mapping submodel IDs to submodels
        """
        self._submodels = submodels
        
    def get_submodel(self, id_: str) -> Optional[model.Submodel]:
        """Get a submodel by ID."""
        return self._submodels.get(id_) 