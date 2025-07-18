"""test script"""
from ansible_collections.cisco.ndfc.plugins.module_utils.common.classes.rest_send_v2 import RestSend
from ansible_collections.cisco.ndfc.plugins.module_utils.common.classes.sender_nd import Sender
from ansible_collections.cisco.ndfc.plugins.module_utils.common.classes.response_handler import ResponseHandler
from ansible_collections.cisco.ndfc.plugins.module_utils.common.properties.rest_send import RestSendProperty


class MyClass:
    """class to test property composition"""
    def __init__(self):
        self._rest_send_attr = RestSendProperty()
    @property
    def rest_send(self):
        """RestSend getter/setter"""
        return self._rest_send_attr.get_value()
    @rest_send.setter
    def rest_send(self, value):
        self._rest_send_attr.set_value(value)

params = {"check_mode": False, "state": "merged"}
rest_send = RestSend(params=params)
rest_send.sender = Sender()
rest_send.response_handler = ResponseHandler()

my_class = MyClass()
my_class.rest_send = rest_send
