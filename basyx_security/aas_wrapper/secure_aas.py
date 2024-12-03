"""
Secure AAS wrapper implementation for BaSyx Security Layer.
"""

from typing import Dict, Optional

from basyx.aas import model

from ..core import AccessRight, SecurityContext, SecurityManager, SecurityViolation
from .provider import SubmodelProvider
from .secure_submodel import SecureSubmodel


class SecureAAS:
    """Security wrapper for Asset Administration Shells."""

    def __init__(
        self,
        aas: model.AssetAdministrationShell,
        security_manager: SecurityManager,
        provider: SubmodelProvider,
    ):
        self._aas = aas
        self._security_manager = security_manager
        self._secure_submodels: Dict[str, SecureSubmodel] = {}
        self._provider = provider

        # Wrap all submodels
        for submodel_ref in aas.submodel:
            if isinstance(submodel_ref, model.ModelReference):
                key = submodel_ref.key
                if isinstance(key, tuple):
                    key = key[0]
                submodel = provider.get_submodel(key.value)
                if submodel:
                    self._secure_submodels[submodel.id_short
                                           ] = SecureSubmodel(submodel, security_manager)

    def get_submodel(self, context: SecurityContext, submodel_id: str) -> Optional[SecureSubmodel]:
        """
        Get a secure submodel by ID with security check.

        Args:
            context: Security context for the request
            submodel_id: ID of the submodel to retrieve

        Returns:
            SecureSubmodel if found and accessible, None otherwise

        Raises:
            SecurityViolation: If access is denied
        """
        if not self._security_manager.check_access(context, self._aas.id_short, AccessRight.READ):
            raise SecurityViolation(f"Access denied to read AAS {self._aas.id_short}")

        return self._secure_submodels.get(submodel_id)

    def add_submodel(self, context: SecurityContext, submodel: model.Submodel) -> None:
        """
        Add a new submodel with security check.

        Args:
            context: Security context for the request
            submodel: Submodel to add

        Raises:
            SecurityViolation: If access is denied
        """
        if not self._security_manager.check_access(context, self._aas.id_short, AccessRight.WRITE):
            raise SecurityViolation(f"Access denied to modify AAS {self._aas.id_short}")

        self._aas.submodel.add(model.ModelReference.from_referable(submodel))
        self._secure_submodels[submodel.id_short] = SecureSubmodel(submodel, self._security_manager)

    @property
    def aas(self) -> model.AssetAdministrationShell:
        """Get the wrapped AAS."""
        return self._aas
