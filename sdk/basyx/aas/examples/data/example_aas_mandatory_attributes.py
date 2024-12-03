# Copyright (c) 2023 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License, available in
# the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT
"""
Example AAS with only mandatory attributes.

This module provides example AAS objects that only contain mandatory attributes according to the specification.
All optional attributes are omitted.
"""

from ... import model


def create_example_aas_mandatory_attributes():
    """Create an example AAS with only mandatory attributes."""
    # Create the AAS
    aas = model.AssetAdministrationShell(
        id_="https://example.com/aas/1",
        asset_information=model.AssetInformation(
            global_asset_id="https://example.com/assets/1",
            asset_kind=model.AssetKind.INSTANCE,
        ),
    )

    # Create a submodel
    submodel = model.Submodel(
        id_="https://example.com/submodels/1",
        semantic_id=model.ExternalReference(
            (
                model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://example.com/semantics/1",
                ),
            )
        ),
    )

    # Add the submodel to the AAS
    aas.submodel.add(submodel)

    return aas
