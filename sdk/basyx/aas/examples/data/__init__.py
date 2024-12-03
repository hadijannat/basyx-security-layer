"""Example data for testing and demonstration.

This package provides example AAS objects for testing and demonstration purposes.
The examples are organized into different modules:

example_aas.py
    Complete example with all optional attributes

example_aas_mandatory_attributes.py
    Example with only mandatory attributes

example_aas_missing_attributes.py
    Example with missing attributes

example_submodel_template.py
    Example submodel template
"""

from ._helper import AASDataChecker
from .example_aas import (
    check_example_submodel,
    check_full_example,
    create_example_submodel,
    create_full_example,
)
from .example_aas_mandatory_attributes import create_example_aas_mandatory_attributes
from .example_aas_missing_attributes import create_example_aas_missing_attributes
from .example_submodel_template import create_example_submodel_template

__all__ = [
    "AASDataChecker",
    "create_example_submodel",
    "create_full_example",
    "check_example_submodel",
    "check_full_example",
    "create_example_aas_mandatory_attributes",
    "create_example_aas_missing_attributes",
    "create_example_submodel_template",
]
