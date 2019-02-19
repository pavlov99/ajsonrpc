from typing import Union, Optional, Any, Iterable, Mapping
from abc import ABCMeta, abstractmethod
import json


class JSONSerializable(metaclass=ABCMeta):

    """Common functionality for json serializable objects."""

    serialize = staticmethod(json.dumps)
    deserialize = staticmethod(json.loads)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def from_str(cls, s: str):
        payload = cls.deserialize(s)

        if not isinstance(payload, dict):
            raise ValueError("Payload should be dict")

        return cls(**payload)


class JSONRPC20Request(JSONSerializable):
    def __init__(self,
                method: str,
                params: Optional[Union[Mapping[str, Any], Iterable[Any]]] = None,
                id: Optional[Union[str, int]] = None,
                is_notification: bool = False
                ) -> None:

        self.payload = {
            'jsonrpc': '2.0'
        }
        self.method = method
        self.params = params
        self.id = id

    def __repr__(self):
        return repr(self.payload)

    def __str__(self):
        return self.serialize(self.payload)

    @property
    def method(self) -> str:
        return self.payload['method']

    @method.setter
    def method(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError('"method" has to be str')
        self.payload['method'] = value

    @property
    def params(self) -> Optional[Union[Mapping[str, Any], Iterable[Any]]]:
        return self.payload.get('params')

    @params.setter
    def params(self, value: Optional[Union[Mapping[str, Any], Iterable[Any]]]) -> None:
        self.payload['params'] = value

    @property
    def id(self):
        if not self.is_notification:
            return self.payload.get('id')

    @id.setter
    def id(self, value: Optional[Union[str, int]]) -> None:
        self.payload['id'] = value

    @id.deleter
    def id(self):
        del self.payload['id']

    @property
    def is_notification(self):
        return 'id' not in self.payload

    @property
    def args(self):
        """ Method position arguments.
        :return tuple args: method position arguments.
        """
        # if not none and not mapping
        return tuple(self.params) if isinstance(self.params, list) else ()

    @property
    def kwargs(self):
        """ Method named arguments.
        :return dict kwargs: method named arguments.
        """
        # if mapping
        return self.params if isinstance(self.params, dict) else {}

class JSONRPCError(JSONSerializable):

    """ Error for JSON-RPC communication.
    When a rpc call encounters an error, the Response Object MUST contain the
    error member with a value that is a Object with the following members:
    Parameters
    ----------
    code: int
        A Number that indicates the error type that occurred.
        This MUST be an integer.
        The error codes from and including -32768 to -32000 are reserved for
        pre-defined errors. Any code within this range, but not defined
        explicitly below is reserved for future use. The error codes are nearly
        the same as those suggested for XML-RPC at the following
        url: http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
    message: str
        A String providing a short description of the error.
        The message SHOULD be limited to a concise single sentence.
    data: int or str or dict or list, optional
        A Primitive or Structured value that contains additional
        information about the error.
        This may be omitted.
        The value of this member is defined by the Server (e.g. detailed error
        information, nested errors etc.).
    """

    def __init__(self, code: int = None, message: str = None, data: Any = None):
        self.payload = {}
        self.code = getattr(self.__class__, "CODE", code)
        self.message = getattr(self.__class__, "MESSAGE", message)

        if data is not None:
            # NOTE: if not set in constructor, do not add 'data' to payload.
            # If data = null is requred, set it after object initialization.
            self.data = data

    def __repr__(self):
        return repr(self.payload)

    def __str__(self):
        return self.serialize(self.payload)

    @property
    def code(self):
        return self.payload["code"]

    @code.setter
    def code(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Error code should be integer")

        self.payload["code"] = value

    @property
    def message(self):
        return self.payload["message"]

    @message.setter
    def message(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Error message should be string")

        self.payload["message"] = value

    @property
    def data(self):
        return self.payload.get("data")

    @data.setter
    def data(self, value):
        self.payload["data"] = value

    @data.deleter
    def data(self):
        del self.payload["data"]


class JSONRPCParseError(JSONRPCError):

    """ Parse Error.
    Invalid JSON was received by the server.
    An error occurred on the server while parsing the JSON text.
    """

    CODE = -32700
    MESSAGE = "Parse error"


class JSONRPCInvalidRequest(JSONRPCError):

    """ Invalid Request.
    The JSON sent is not a valid Request object.
    """

    CODE = -32600
    MESSAGE = "Invalid Request"


class JSONRPCMethodNotFound(JSONRPCError):

    """ Method not found.
    The method does not exist / is not available.
    """

    CODE = -32601
    MESSAGE = "Method not found"


class JSONRPCInvalidParams(JSONRPCError):

    """ Invalid params.
    Invalid method parameter(s).
    """

    CODE = -32602
    MESSAGE = "Invalid params"


class JSONRPCInternalError(JSONRPCError):

    """ Internal error.
    Internal JSON-RPC error.
    """

    CODE = -32603
    MESSAGE = "Internal error"


class JSONRPCServerError(JSONRPCError):

    """ Server error.
    Reserved for implementation-defined server-errors.
    """

    CODE = -32000
    MESSAGE = "Server error"


class JSONRPC20Response(JSONSerializable):
    def __init__(self,
                result: Optional[Any] = None,
                error: Optional[JSONRPCError] = None,
                id: Optional[Union[int, str]] = None,
                ) -> None:

        self.payload = {
            'jsonrpc': '2.0'
        }

        if result is not None:
            self.payload['result'] = result

        if error is not None:
            self.payload['error'] = error

        self.id = id

    def __repr__(self):
        return repr(self.payload)

    def __str__(self):
        return self.serialize(self.payload)

    @property
    def id(self):
        return self.payload['id']

    @id.setter
    def id(self, value: Optional[Union[str, int]]) -> None:
        self.payload['id'] = value

    @property
    def result(self):
        return self.payload.get('result')

    @property
    def error(self):
        return self.payload.get('error')
