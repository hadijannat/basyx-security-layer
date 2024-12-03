"""
.. _adapter.json.__init__:

This package contains functionality for serialization and deserialization of BaSyx Python SDK objects into/from JSON.
"""

from .json_deserialization import (
    AASFromJsonDecoder,
    StrictAASFromJsonDecoder,
    StrictStrippedAASFromJsonDecoder,
    StrippedAASFromJsonDecoder,
    read_aas_json_file,
    read_aas_json_file_into,
)
from .json_serialization import (
    AASToJsonEncoder,
    StrippedAASToJsonEncoder,
    object_store_to_json,
    write_aas_json_file,
)

__all__ = [
    "AASFromJsonDecoder",
    "StrictAASFromJsonDecoder",
    "StrictStrippedAASFromJsonDecoder",
    "StrippedAASFromJsonDecoder",
    "read_aas_json_file",
    "read_aas_json_file_into",
    "AASToJsonEncoder",
    "StrippedAASToJsonEncoder",
    "object_store_to_json",
    "write_aas_json_file",
]
