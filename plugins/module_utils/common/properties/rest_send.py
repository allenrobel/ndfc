"""property definition for rest_send"""

import inspect
from ..classes.rest_send_v2 import RestSend

class RestSendProperty:
    """
    # Summary

    A property that validates that the input is an instance of RestSend.

    ## Usage

    ```python
        class MyClass:
            def __init__(self):
                self._rest_send_attr = AttrRestSend()
            @property
            def rest_send(self):
                return self._rest_send_attr.get_value()
            @rest_send.setter
            def rest_send(self, value):
                self._rest_send_attr.set_value(value)

        params = {"check_mode": False, "state": "merged"}
        rest_send = RestSend(params=params)
        rest_send.sender = Sender()
        rest_send.response_handler = ResponseHandler()

        test_properties = TestProperties()
        test_properties.rest_send = rest_send
    ```        
    test property composition
    """
    def __init__(self):
        self.class_name = __class__.__name__
        self._value = None

    def get_value(self):
        """get the value"""
        print("Getting value...")
        if self._value is None:
            msg = f"{self.class_name}.get_value: "
            msg += "value must be set to an instance of the RestSend class before accessing it"
            raise ValueError(msg)
        return self._value

    def set_value(self, value):
        """set the value"""
        method_name = inspect.stack()[0][3]
        _class_have = None
        _class_need = "RestSend"
        msg = f"{self.class_name}.{method_name}: "
        msg += f"value must be an instance of {_class_need}. "
        msg += f"Got value {value} of type {type(value).__name__}."
        try:
            _class_have = value.class_name
        except AttributeError as error:
            msg += f" Error detail: {error}."
            raise TypeError(msg) from error
        if _class_have != _class_need:
            raise TypeError(msg)
        self._value = value


        print("Setting value...")
        if not isinstance(value, RestSend):
            raise TypeError("Value must be a string")
        self._value = value
