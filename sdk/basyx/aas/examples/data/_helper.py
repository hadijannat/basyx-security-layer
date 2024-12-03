# Copyright (c) 2024 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License,
# available in the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT
"""Helper functions for example data."""

from typing import Type, Union

from ... import model


class AASDataChecker:
    """Helper class for checking AAS data."""

    def __init__(self):
        """Initialize the checker."""
        self._checks = []

    def check(self, expression: bool, message: str, **kwargs) -> bool:
        """Check if expression is True and store result.

        :param expression: Expression to check
        :param message: Message to show if check fails
        :param kwargs: Additional values for check result
        :return: Value of expression
        """
        self._checks.append({"result": expression, "message": message, **kwargs})
        return expression

    def check_value(self, actual: any, expected: any, message: str) -> None:
        """Check if actual value matches expected value.

        :param actual: Actual value
        :param expected: Expected value
        :param message: Message to show if check fails
        """
        assert actual == expected, f"{message} (expected {expected}, got {actual})"
