# Copyright (c) 2024 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License,
# available in the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT
"""
This module implements the "Specification of the Asset Administration Shell Part 2 Application
Programming Interfaces". However, several features and routes are currently not supported:

1. Correlation ID: Not implemented because it was deemed unnecessary for this server.

2. Extent Parameter (`withBlobValue/withoutBlobValue`):
   Not implemented due to the lack of support in JSON/XML serialization.

3. Route `/shells/{aasIdentifier}/asset-information/thumbnail`:
   Not implemented because the specification lacks clarity.

4. Serialization and Description Routes:
   - `/serialization`
   - `/description`
   These routes are not implemented at this time.

5. Value, Path, and PATCH Routes:
   - All `/…/value$`, `/…/path$`, and `PATCH` routes are currently not implemented.

6. Operation Invocation Routes: The following routes are not implemented because operation invocation
   is not yet supported by the `basyx-python-sdk`:
   - `POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/invoke`
   - `POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/invoke/$value`
   - `POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/invoke-async`
   - `POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/invoke-async/$value`
   - `GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/operation-status/{handleId}`
   - `GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/operation-results/{handleId}`
   - `GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/operation-results/{handleId}/$value`
"""

import abc
import base64
import binascii
import datetime
import enum
import io
import itertools
import json
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls
import werkzeug.utils
from basyx.aas import model
from lxml import etree
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest, Conflict, NotFound, UnprocessableEntity
from werkzeug.routing import MapAdapter, Rule, Submount
from werkzeug.wrappers import Request, Response

from . import aasx
from ._generic import XML_NS_MAP
from .json import (
    AASToJsonEncoder,
    StrictAASFromJsonDecoder,
    StrictStrippedAASFromJsonDecoder,
)
from .xml import (
    XMLConstructables,
    object_to_xml_element,
    read_aas_xml_element,
    xml_serialization,
)


@enum.unique
class MessageType(enum.Enum):
    UNDEFINED = enum.auto()
    INFO = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()
    EXCEPTION = enum.auto()

    def __str__(self):
        return self.name.capitalize()


class Message:
    def __init__(
        self,
        code: str,
        text: str,
        message_type: MessageType = MessageType.UNDEFINED,
        timestamp: Optional[datetime.datetime] = None,
    ):
        self.code: str = code
        self.text: str = text
        self.message_type: MessageType = message_type
        self.timestamp: datetime.datetime = (
            timestamp if timestamp is not None else datetime.datetime.now(datetime.UTC)
        )


class Result:
    def __init__(self, success: bool, messages: Optional[List[Message]] = None):
        if messages is None:
            messages = []
        self.success: bool = success
        self.messages: List[Message] = messages


class ResultToJsonEncoder(AASToJsonEncoder):
    @classmethod
    def _result_to_json(cls, result: Result) -> Dict[str, object]:
        return {"success": result.success, "messages": result.messages}

    @classmethod
    def _message_to_json(cls, message: Message) -> Dict[str, object]:
        return {
            "messageType": message.message_type,
            "text": message.text,
            "code": message.code,
            "timestamp": message.timestamp.isoformat(),
        }

    def default(self, obj: object) -> object:
        if isinstance(obj, Result):
            return self._result_to_json(obj)
        if isinstance(obj, Message):
            return self._message_to_json(obj)
        if isinstance(obj, MessageType):
            return str(obj)
        return super().default(obj)


class StrippedResultToJsonEncoder(ResultToJsonEncoder):
    stripped = True


ResponseData = Union[Result, object, List[object]]


class APIResponse(abc.ABC, Response):
    @abc.abstractmethod
    def __init__(
        self,
        obj: Optional[ResponseData] = None,
        cursor: Optional[int] = None,
        stripped: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if obj is None:
            self.status_code = 204
        else:
            self.data = self.serialize(obj, cursor, stripped)

    @abc.abstractmethod
    def serialize(self, obj: ResponseData, cursor: Optional[int], stripped: bool) -> str:
        pass


class JsonResponse(APIResponse):
    def __init__(self, *args, content_type="application/json", **kwargs):
        super().__init__(*args, **kwargs, content_type=content_type)

    def serialize(self, obj: ResponseData, cursor: Optional[int], stripped: bool) -> str:
        if cursor is None:
            data = obj
        else:
            data = {"paging_metadata": {"cursor": str(cursor)}, "result": obj}
        return json.dumps(
            data,
            cls=StrippedResultToJsonEncoder if stripped else ResultToJsonEncoder,
            separators=(",", ":"),
        )


class XmlResponse(APIResponse):
    def __init__(self, *args, content_type="application/xml", **kwargs):
        super().__init__(*args, **kwargs, content_type=content_type)

    def serialize(self, obj: ResponseData, cursor: Optional[int], stripped: bool) -> str:
        root_elem = etree.Element("response", nsmap=XML_NS_MAP)
        if cursor is not None:
            root_elem.set("cursor", str(cursor))
        if isinstance(obj, Result):
            result_elem = result_to_xml(obj, **XML_NS_MAP)
            for child in result_elem:
                root_elem.append(child)
        elif isinstance(obj, list):
            for item in obj:
                item_elem = object_to_xml_element(item)
                root_elem.append(item_elem)
        else:
            obj_elem = object_to_xml_element(obj)
            for child in obj_elem:
                root_elem.append(child)
        etree.cleanup_namespaces(root_elem)
        xml_str = etree.tostring(root_elem, xml_declaration=True, encoding="utf-8")
        return xml_str  # type: ignore[return-value]


class XmlResponseAlt(XmlResponse):
    def __init__(self, *args, content_type="text/xml", **kwargs):
        super().__init__(*args, **kwargs, content_type=content_type)


def result_to_xml(result: Result, **kwargs) -> etree._Element:
    result_elem = etree.Element("result", **kwargs)
    success_elem = etree.Element("success")
    success_elem.text = xml_serialization.boolean_to_xml(result.success)
    messages_elem = etree.Element("messages")
    for message in result.messages:
        messages_elem.append(message_to_xml(message))

    result_elem.append(success_elem)
    result_elem.append(messages_elem)
    return result_elem


def message_to_xml(message: Message) -> etree._Element:
    message_elem = etree.Element("message")
    message_type_elem = etree.Element("messageType")
    message_type_elem.text = str(message.message_type)
    text_elem = etree.Element("text")
    text_elem.text = message.text
    code_elem = etree.Element("code")
    code_elem.text = message.code
    timestamp_elem = etree.Element("timestamp")
    timestamp_elem.text = message.timestamp.isoformat()

    message_elem.append(message_type_elem)
    message_elem.append(text_elem)
    message_elem.append(code_elem)
    message_elem.append(timestamp_elem)
    return message_elem
