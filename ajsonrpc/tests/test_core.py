import unittest
import warnings

from ..core import JSONRPC20Request, JSONRPC20RequestIdWarning, JSONRPC20BatchRequest


class TestJSONRPC20Request(unittest.TestCase):

    """Test JSONRPC20Request.

    On creation and after modification the request object has to be valid. As
    these scenarios are almost identical, test both in test cases.

    """

    #############################################
    # "method" tests
    #############################################

    def test_method_validation_correct(self):
        r = JSONRPC20Request(method="valid", id=0)
        self.assertEqual(r.method, "valid")
        r.method = "also_valid"
        self.assertEqual(r.method, "also_valid")

    def test_method_validation_not_str(self):
        r = JSONRPC20Request(method="valid", id=0)

        with self.assertRaises(ValueError):
            JSONRPC20Request(method=[], id=0)
        
        with self.assertRaises(ValueError):
            r.method=[]

        with self.assertRaises(ValueError):
            JSONRPC20Request(method={}, id=0)
        
        with self.assertRaises(ValueError):
            r.method={}
    
    def test_method_validation_invalid_rpc_prefix(self):
        """ Test method SHOULD NOT starts with rpc."""
        r = JSONRPC20Request(method="valid", id=0)

        with self.assertRaises(ValueError):
            JSONRPC20Request(method="rpc.", id=0)
        
        with self.assertRaises(ValueError):
            r.method = "rpc."

        with self.assertRaises(ValueError):
            JSONRPC20Request(method="rpc.test", id=0)
        
        with self.assertRaises(ValueError):
            r.method = "rpc.test"

        JSONRPC20Request(method="rpcvalid", id=0)
        JSONRPC20Request(method="rpc", id=0)
    
    #############################################
    # "params" tests
    #############################################
    
    def test_params_validation_none(self):
        r1 = JSONRPC20Request("null_params", params=None, id=1)
        self.assertFalse("params" in r1.body)

        # Set params to None
        r2 = JSONRPC20Request("null_params", params=[], id=2)
        self.assertTrue("params" in r2.body)
        r2.params = None
        self.assertFalse("params" in r2.body)

        # Remove params
        r3 = JSONRPC20Request("null_params", params=[], id=3)
        self.assertTrue("params" in r3.body)
        del r3.params
        self.assertFalse("params" in r3.body)

    def test_params_validation_list(self):
        r = JSONRPC20Request("list", params=[], id=0)
        self.assertEqual(r.params, [])
        r.params = [0, 1]
        self.assertEqual(r.params, [0, 1])

    def test_params_validation_tuple(self):
        r = JSONRPC20Request("tuple", params=(), id=0)
        self.assertEqual(r.params, ())  # keep the same iterable
        r.params=(0, 1)
        self.assertEqual(r.params, (0, 1))
    
    def test_params_validation_iterable(self):
        r1 = JSONRPC20Request("string_params", params="string", id=1)
        self.assertEqual(r1.params, "string")
        r1.params = "another string"
        self.assertEqual(r1.params, "another string")

        r2 = JSONRPC20Request("range_params", params=range(1), id=2)
        self.assertEqual(r2.params, range(1))
        r2.params = range(2)
        self.assertEqual(r2.params, range(2))

    def test_params_validation_dict(self):
        r1 = JSONRPC20Request("dict_params", params={}, id=1)
        self.assertEqual(r1.params, {})
        r1.params = {"a": 0}
        self.assertEqual(r1.params, {"a": 0})

        r2 = JSONRPC20Request("dict_params", params={"a": 0}, id=2)
        self.assertEqual(r2.params, {"a": 0})
        r2.params={"a": {}}
        self.assertEqual(r2.params, {"a": {}})

    def test_params_validation_invalid(self):
        with self.assertRaises(ValueError):
            JSONRPC20Request("invalid_params", params=0, id=0)

    #############################################
    # "id" tests
    #############################################

    def test_id_validation_valid(self):
        r1 = JSONRPC20Request("string_id", id="id")
        self.assertEqual(r1.id, "id")
        r1.id = "another_id"
        self.assertEqual(r1.id, "another_id")

        r2 = JSONRPC20Request("int_id", id=0)
        self.assertEqual(r2.id, 0)
        r2.id = 1
        self.assertEqual(r2.id, 1)

        # Null ids are possible but discouraged. Omit id for notifications.
        with warnings.catch_warnings(record=True) as _warnings:
            warnings.simplefilter("always")
            JSONRPC20Request("null_id", id=None)
            assert len(_warnings) == 1
            assert issubclass(_warnings[-1].category, JSONRPC20RequestIdWarning)
            assert "Null as a value" in str(_warnings[-1].message)
        
        # Float ids are possible but discouraged
        with warnings.catch_warnings(record=True) as _warnings:
            warnings.simplefilter("always")
            JSONRPC20Request("float_id", id=0.1)

            assert len(_warnings) == 1
            assert issubclass(_warnings[-1].category, JSONRPC20RequestIdWarning)
            assert "Fractional parts" in str(_warnings[-1].message)


    def test_id_validation_invalid(self):
        with self.assertRaises(ValueError):
            JSONRPC20Request("list_id", id=[])

        with self.assertRaises(ValueError):
            JSONRPC20Request("dict_id", id={})
    
    #############################################
    # Notification tests
    #############################################

    def test_notification_init(self):
        r = JSONRPC20Request("notification", is_notification=True)
        self.assertTrue(r.is_notification)
        with self.assertRaises(KeyError):
            r.id
    
    def test_notification_conversion(self):
        r = JSONRPC20Request("notification", id=0)
        self.assertFalse(r.is_notification)
        del r.id
        self.assertTrue(r.is_notification)

    #############################################
    # Auxiliary methods tests
    #############################################

    def test_request_args(self):
        self.assertEqual(JSONRPC20Request("add", id=0).args, [])
        self.assertEqual(JSONRPC20Request("add", [], id=0).args, [])
        self.assertEqual(JSONRPC20Request("add", "str", id=0).args, ["s", "t", "r"])
        self.assertEqual(JSONRPC20Request("add", {"a": 1}, id=0).args, [])
        self.assertEqual(JSONRPC20Request("add", [1, 2], id=0).args, [1, 2])

    def test_request_kwargs(self):
        self.assertEqual(JSONRPC20Request("add", id=0).kwargs, {})
        self.assertEqual(JSONRPC20Request("add", [1, 2], id=0).kwargs, {})
        self.assertEqual(JSONRPC20Request("add", {}, id=0).kwargs, {})
        self.assertEqual(JSONRPC20Request("add", {"a": 1}, id=0).kwargs, {"a": 1})


class TestJSONRPC20BatchRequest(unittest.TestCase):
    def test_init(self):
        br = JSONRPC20BatchRequest()
        self.assertEqual(len(br), 0)

        br.append(JSONRPC20Request("first", id=1))
        br.extend([JSONRPC20Request("second", id=2)])
        self.assertEqual(len(br), 2)
        self.assertEqual(br[-1].method, "second")