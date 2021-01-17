from typing import Union, Optional, Any, Iterable, Mapping, List, Dict
from types import FunctionType
from numbers import Number
import warnings
import json
import collections


class JSONRPC20RequestIdWarning(UserWarning):
    pass

class JSONRPC20Request:
    """JSON-RPC 2.0 Request object.

    A rpc call is represented by sending a Request object to a Server.
    The Request object has the following members:

    jsonrpc
        A String specifying the version of the JSON-RPC protocol. MUST be
        exactly "2.0".
    method
        A String containing the name of the method to be invoked. Method names
        that begin with the word rpc followed by a period character (U+002E or
        ASCII 46) are reserved for rpc-internal methods and extensions and MUST
        NOT be used for anything else.
    params
        A Structured value that holds the parameter values to be used during
        the invocation of the method. This member MAY be omitted.
    id
        An identifier established by the Client that MUST contain a String,
        Number, or NULL value if included. If it is not included it is assumed
        to be a notification. The value SHOULD normally not be Null [1] and
        Numbers SHOULD NOT contain fractional parts [2].

        The Server MUST reply with the same value in the Response object if
        included. This member is used to correlate the context between the two
        objects.

        [1] The use of Null as a value for the id member in a Request object
        is discouraged, because this specification uses a value of Null for
        Responses with an unknown id. Also, because JSON-RPC 1.0 uses an id
        value of Null for Notifications this could cause confusion in handling.

        [2] Fractional parts may be problematic, since many decimal fractions
        cannot be represented exactly as binary fractions.

    Notification
        A Notification is a Request object without an "id" member. A Request
        object that is a Notification signifies the Client's lack of interest
        in the corresponding Response object, and as such no Response object
        needs to be returned to the client. The Server MUST NOT reply to a
        Notification, including those that are within a batch request.

        Notifications are not confirmable by definition, since they do not have
        a Response object to be returned. As such, the Client would not be
        aware of any errors (like e.g. "Invalid params","Internal error").

    Parameter Structures
        If present, parameters for the rpc call MUST be provided as a
        Structured value. Either by-position through an Array or by-name
        through an Object.

        by-position: params MUST be an Array, containing the values in the
            Server expected order.
        by-name: params MUST be an Object, with member names that match the
            Server expected parameter names. The absence of expected names MAY
            result in an error being generated. The names MUST match exactly,
            including case, to the method's expected parameters.

    Note:
        Design principles:
        * if an object is created or modified without exceptions, its state is
        valid.
        * There is a signle source of truth (see Attributes), modification should
        be done via setters.

    Args:
        method (str):
            method to call.
        params (:obj:dict, optional):
            a mapping of method argument values or a list of positional arguments.
        id:
            an id of the request. By default equals to None and raises warning.
            For notifications set is_notification=True so id would not be
            included in the body.
        is_notification:
            a boolean flag indicating whether to include id in the body or not.

    Attributes:
        _body (dict): body of the request. It should always contain valid data and
        should be modified via setters to ensure validity.

    Examples:
        modification via self.body["method"] vs self.method
        modifications via self._body
    """
    def __init__(self,
                method: str,
                params: Optional[Union[Mapping[str, Any], Iterable[Any]]] = None,
                id: Optional[Union[str, int]] = None,
                is_notification: bool = False
                ) -> None:
        request_body = {
            "jsonrpc": "2.0",
            "method": method,
        }

        if params is not None:
            # If params are not present, they should not be in body
            request_body["params"] = params

        if not is_notification:
            # For non-notifications "id" has to be in body, even if null
            request_body["id"] = id

        self.body = request_body

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: Mapping[str, Any]) -> None:
        self._body = value

        # Call validators via value assigning
        self.method = value["method"]

        if "params" in value:
            self.params = value["params"]
        
        if "id" in value:
            self.id = value["id"]

    @property
    def method(self) -> str:
        return self.body["method"]
    
    @method.setter
    def method(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Method should be string")

        if value.startswith("rpc."):
            raise ValueError(
                "Method names that begin with the word rpc followed by a " +
                "period character (U+002E or ASCII 46) are reserved for " +
                "rpc-internal methods and extensions and MUST NOT be used " +
                "for anything else.")

        self._body["method"] = value

    @property
    def params(self) -> Optional[Union[Mapping[str, Any], Iterable[Any]]]:
        return self.body.get("params")

    @params.setter
    def params(self, value: Optional[Union[Mapping[str, Any], Iterable[Any]]]) -> None:
        """
        Note: params has to be None, dict or iterable. In the latter case it would be
        converted to a list. It is possible to set param as tuple or even string as they
        are iterables, they would be converted to lists, e.g. ["h", "e", "l", "l", "o"]
        """
        if value is None:
            if "params" in self._body:
                del self._body["params"]
            return

        if not isinstance(value, (Mapping, Iterable)):
            raise ValueError("Incorrect params {0}".format(value))

        self._body["params"] = value
    
    @params.deleter
    def params(self):
        del self._body["params"]

    @property
    def id(self):
        return self.body["id"]

    @id.setter
    def id(self, value: Optional[Union[str, Number]]) -> None:
        if value is None:
            warnings.warn(
                "The use of Null as a value for the id member in a Request "
                "object is discouraged, because this specification uses a "
                "value of Null for Responses with an unknown id. Also, because"
                " JSON-RPC 1.0 uses an id value of Null for Notifications this"
                " could cause confusion in handling.",
                JSONRPC20RequestIdWarning
            )
            self._body["id"] = value
            return
        
        if not isinstance(value, (str, Number)):
            raise ValueError("id MUST contain a String, Number, or NULL value")

        if isinstance(value, Number) and not isinstance(value, int):
            warnings.warn(
                "Fractional parts may be problematic, since many decimal "
                "fractions cannot be represented exactly as binary fractions.",
                JSONRPC20RequestIdWarning
            )

        self._body["id"] = value

    @id.deleter
    def id(self):
        del self._body["id"]

    @property
    def is_notification(self):
        """Check if request is a notification.
        There is no API to make a request notification as this has to remove
        "id" from body and might cause confusion. To make a request
        notification delete "id" explicitly.
        """
        return "id" not in self.body

    @property
    def args(self) -> List:
        """ Method position arguments.
        :return list args: method position arguments.
        note: dict is also iterable, so exclude it from args.
        """
        # if not none and not mapping
        return list(self.params) if isinstance(self.params, Iterable) and not isinstance(self.params, Mapping) else []

    @property
    def kwargs(self) -> Dict:
        """ Method named arguments.
        :return dict kwargs: method named arguments.
        """
        # if mapping
        return dict(self.params) if isinstance(self.params, Mapping) else {}


class JSONRPC20BatchRequest(collections.MutableSequence):
    def __init__(self, requests: List[JSONRPC20Request] = None):
        self.requests = requests or []
    
    def __getitem__(self, index):
        return self.requests[index]

    def __setitem__(self, index, value: JSONRPC20Request):
        self.requests[index] = value

    def __delitem__(self, index):
        del self.requests[index]

    def __len__(self):
        return len(self.requests)
    
    def insert(self, index, value: JSONRPC20Request):
        self.requests.insert(index, value)


# class JSONRPCError(JSONSerializable):

#     """ Error for JSON-RPC communication.
#     When a rpc call encounters an error, the Response Object MUST contain the
#     error member with a value that is a Object with the following members:
#     Parameters
#     ----------
#     code: int
#         A Number that indicates the error type that occurred.
#         This MUST be an integer.
#         The error codes from and including -32768 to -32000 are reserved for
#         pre-defined errors. Any code within this range, but not defined
#         explicitly below is reserved for future use. The error codes are nearly
#         the same as those suggested for XML-RPC at the following
#         url: http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
#     message: str
#         A String providing a short description of the error.
#         The message SHOULD be limited to a concise single sentence.
#     data: int or str or dict or list, optional
#         A Primitive or Structured value that contains additional
#         information about the error.
#         This may be omitted.
#         The value of this member is defined by the Server (e.g. detailed error
#         information, nested errors etc.).
#     """

#     def __init__(self, code: int = None, message: str = None, data: Any = None):
#         self.payload = {}
#         self.code = getattr(self.__class__, "CODE", code)
#         self.message = getattr(self.__class__, "MESSAGE", message)

#         if data is not None:
#             # NOTE: if not set in constructor, do not add 'data' to payload.
#             # If data = null is requred, set it after object initialization.
#             self.data = data

#     def __repr__(self):
#         return repr(self.payload)

#     def __str__(self):
#         return self.serialize(self.payload)

#     @property
#     def code(self):
#         return self.payload["code"]

#     @code.setter
#     def code(self, value: int):
#         if not isinstance(value, int):
#             raise ValueError("Error code should be integer")

#         self.payload["code"] = value

#     @property
#     def message(self):
#         return self.payload["message"]

#     @message.setter
#     def message(self, value: str):
#         if not isinstance(value, str):
#             raise ValueError("Error message should be string")

#         self.payload["message"] = value

#     @property
#     def data(self):
#         return self.payload.get("data")

#     @data.setter
#     def data(self, value):
#         self.payload["data"] = value

#     @data.deleter
#     def data(self):
#         del self.payload["data"]


# class JSONRPCParseError(JSONRPCError):

#     """ Parse Error.
#     Invalid JSON was received by the server.
#     An error occurred on the server while parsing the JSON text.
#     """

#     CODE = -32700
#     MESSAGE = "Parse error"


# class JSONRPCInvalidRequest(JSONRPCError):

#     """ Invalid Request.
#     The JSON sent is not a valid Request object.
#     """

#     CODE = -32600
#     MESSAGE = "Invalid Request"


# class JSONRPCMethodNotFound(JSONRPCError):

#     """ Method not found.
#     The method does not exist / is not available.
#     """

#     CODE = -32601
#     MESSAGE = "Method not found"


# class JSONRPCInvalidParams(JSONRPCError):

#     """ Invalid params.
#     Invalid method parameter(s).
#     """

#     CODE = -32602
#     MESSAGE = "Invalid params"


# class JSONRPCInternalError(JSONRPCError):

#     """ Internal error.
#     Internal JSON-RPC error.
#     """

#     CODE = -32603
#     MESSAGE = "Internal error"


# class JSONRPCServerError(JSONRPCError):

#     """ Server error.
#     Reserved for implementation-defined server-errors.
#     """

#     CODE = -32000
#     MESSAGE = "Server error"


# class JSONRPC20Response(JSONSerializable):
#     def __init__(self,
#                 result: Optional[Any] = None,
#                 error: Optional[JSONRPCError] = None,
#                 id: Optional[Union[int, str]] = None,
#                 ) -> None:

#         self.payload = {
#             'jsonrpc': '2.0'
#         }

#         if result is not None:
#             self.payload['result'] = result

#         if error is not None:
#             self.payload['error'] = error

#         self.id = id

#     def __repr__(self):
#         return repr(self.payload)

#     def __str__(self):
#         return self.serialize(self.payload)

#     @property
#     def id(self):
#         return self.payload['id']

#     @id.setter
#     def id(self, value: Optional[Union[str, int]]) -> None:
#         self.payload['id'] = value

#     @property
#     def result(self):
#         return self.payload.get('result')

#     @property
#     def error(self):
#         return self.payload.get('error')
