"""property definition for rest_send"""

import inspect
from ..classes.results import Results

class ResultsProperty:
    """
    # Summary

    A property that validates that the input is an instance of Results.

    ## Usage

    ```python
        class MyClass:
            def __init__(self):
                self._results_property = ResultsProperty()
            @property
            def results(self):
                return self._results_property.get_value()
            @results.setter
            def results(self, value):
                self._results_property.set_value(value)

        results = Results()
        my_class = MyClass()
        my_class.results = results
    ```        
    """
    def __init__(self):
        self.class_name = __class__.__name__
        self._value = None

    def get_value(self):
        """get the value"""
        if self._value is None:
            msg = f"{self.class_name}.get_value: "
            msg += "value must be set to an instance of the Results class before accessing it"
            raise ValueError(msg)
        return self._value

    def set_value(self, value):
        """set the value"""
        method_name = inspect.stack()[0][3]
        _class_have = None
        _class_need = "Results"
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
        if not isinstance(value, Results):
            raise TypeError("Value must be a string")
        self._value = value
