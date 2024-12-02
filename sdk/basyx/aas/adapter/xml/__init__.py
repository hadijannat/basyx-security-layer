"""
.. _adapter.xml.__init__:

This package contains functionality for serialization and deserialization of BaSyx Python SDK objects into/from XML.

:ref:`xml_serialization <adapter.xml.xml_serialization>`: The module offers a function to write an
:class:`ObjectStore <basyx.aas.model.provider.AbstractObjectStore>` to a given file.

:ref:`xml_deserialization <adapter.xml.xml_deserialization>`: The module offers a function to create an
:class:`ObjectStore <basyx.aas.model.provider.AbstractObjectStore>` from a given xml document.
"""

from .xml_deserialization import (
    AASFromXmlDecoder,
    StrictAASFromXmlDecoder,
    StrictStrippedAASFromXmlDecoder,
    StrippedAASFromXmlDecoder,
    XMLConstructables,
    read_aas_xml_element,
    read_aas_xml_file,
    read_aas_xml_file_into,
)
from .xml_serialization import (
    object_store_to_xml_element,
    object_to_xml_element,
    write_aas_xml_element,
    write_aas_xml_file,
)

__all__ = [
    "AASFromXmlDecoder",
    "StrictAASFromXmlDecoder",
    "StrictStrippedAASFromXmlDecoder",
    "StrippedAASFromXmlDecoder",
    "XMLConstructables",
    "read_aas_xml_element",
    "read_aas_xml_file",
    "read_aas_xml_file_into",
    "object_store_to_xml_element",
    "object_to_xml_element",
    "write_aas_xml_element",
    "write_aas_xml_file",
]
