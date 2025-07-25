# Copyright (c) 2024 Cisco and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=line-too-long
from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Allen Robel"

import logging

from ..rest import Rest


class Control(Rest):
    """
    ## api.v1.lan_fabric.rest.control.Control()

    ### Description
    Common methods and properties for Control() subclasses.

    ### Path
    -   ``/api/v1/lan-fabric/rest/control``
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"nd.{self.class_name}")
        self.control = f"{self.rest}/control"
        msg = f"ENTERED api.v1.lan_fabric.rest.control.{self.class_name}"
        self.log.debug(msg)
