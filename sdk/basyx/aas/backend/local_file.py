# Copyright (c) 2024 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License,
# available in the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT
"""Local file backend for storing AAS objects.

This module provides a backend that stores AAS objects in local files.
The files can be in JSON or XML format.
"""

import os
from typing import Optional, Type

from .. import model
from ..adapter.json import read_aas_json_file, write_aas_json_file
from ..adapter.xml import read_aas_xml_file, write_aas_xml_file
from . import backends


class LocalFileBackend(backends.Backend):
    """Backend that stores AAS objects in local files.

    The files can be in JSON or XML format.
    """

    def __init__(
        self,
        path: str,
        file_format: str = "json",
        create_directories: bool = True,
    ):
        """Initialize the backend.

        :param path: Path to store files in
        :param file_format: Format to use ("json" or "xml")
        :param create_directories: Whether to create directories if they don't exist
        """
        super().__init__()
        self._path = path
        self._file_format = file_format.lower()
        if create_directories:
            os.makedirs(path, exist_ok=True)

    def _get_file_path(self, id_: str) -> str:
        """Get file path for object with given ID.

        :param id_: ID of object
        :return: File path
        """
        return os.path.join(
            self._path,
            f"{id_}.{self._file_format}",
        )

    def _read_file(self, path: str) -> model.DictObjectStore:
        """Read object store from file.

        :param path: Path to file
        :return: Object store
        """
        if self._file_format == "json":
            return read_aas_json_file(path)
        elif self._file_format == "xml":
            return read_aas_xml_file(path)
        else:
            raise ValueError(f"Unsupported file format: {self._file_format}")

    def _write_file(
        self,
        path: str,
        object_store: model.DictObjectStore,
    ) -> None:
        """Write object store to file.

        :param path: Path to file
        :param object_store: Object store to write
        """
        if self._file_format == "json":
            write_aas_json_file(path, object_store)
        elif self._file_format == "xml":
            write_aas_xml_file(path, object_store)
        else:
            raise ValueError(f"Unsupported file format: {self._file_format}")
