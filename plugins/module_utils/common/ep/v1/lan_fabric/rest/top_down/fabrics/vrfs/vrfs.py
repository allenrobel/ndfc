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

import inspect
import logging

from ..fabrics import Fabrics
from .........common.enums.http_requests import RequestVerb


class Vrfs(Fabrics):
    """
    ## api.v1.lan-fabric.rest.top-down.fabrics.Vrfs()

    ### Description
    Common methods and properties for top-down.fabrics.Vrfs() subclasses.

    ### Path
    -   ``/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/vrfs``
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"nd.{self.class_name}")
        self.fabrics = f"{self.top_down}/fabrics"
        msg = f"ENTERED api.v1.lan_fabric.rest.top_down.fabrics.vrfs.{self.class_name}"
        self.log.debug(msg)
        self._build_properties()

    def _build_properties(self):
        """
        - Set the fabric_name property.
        """
        self.properties["fabric_name"] = None
        self.properties["ticket_id"] = None

    @property
    def fabric_name(self):
        """
        - getter: Return the fabric_name.
        - setter: Set the fabric_name.
        - setter: Raise ``ValueError`` if fabric_name is not valid.
        """
        return self.properties["fabric_name"]

    @fabric_name.setter
    def fabric_name(self, value):
        method_name = inspect.stack()[0][3]
        try:
            self.conversion.validate_fabric_name(value)
        except (TypeError, ValueError) as error:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"{error}"
            raise ValueError(msg) from error
        self.properties["fabric_name"] = value

    @property
    def path_fabric_name(self):
        """
        -   Endpoint path property, including fabric_name.
        -   Raise ``ValueError`` if fabric_name is not set and
            ``self.required_properties`` contains "fabric_name".
        """
        method_name = inspect.stack()[0][3]
        if self.fabric_name is None and "fabric_name" in self.required_properties:
            msg = f"{self.class_name}.{method_name}: "
            msg += "fabric_name must be set prior to accessing path."
            raise ValueError(msg)
        return f"{self.fabrics}/{self.fabric_name}"

    @property
    def ticket_id(self):
        """
        - getter: Return the ticket_id.
        - setter: Set the ticket_id.
        - setter: Raise ``ValueError`` if ticket_id is not a string.
        - Default: None
        - Note: ticket_id is optional unless Change Control is enabled.
        """
        return self.properties["ticket_id"]

    @ticket_id.setter
    def ticket_id(self, value):
        method_name = inspect.stack()[0][3]
        if not isinstance(value, str):
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Expected string for {method_name}. "
            msg += f"Got {value} with type {type(value).__name__}."
            raise ValueError(msg)
        self.properties["ticket_id"] = value


class EpVrfGet(Fabrics):
    """
    ## V1 API - Vrfs().EpVrfGet()

    ### Description
    Return endpoint information.

    ### Raises
    -   ``ValueError``: If fabric_name is not set.
    -   ``ValueError``: If fabric_name is invalid.

    ### Path
    -   ``/rest/top-down/fabrics/{fabric_name}/vrfs``

    ### Verb
    -   GET

    ### Parameters
    - fabric_name: string
        - set the ``fabric_name`` to be used in the path
        - required
    -   path: retrieve the path for the endpoint
    -   verb: retrieve the verb for the endpoint

    ### Usage
    ```python
    instance = EpVrfGet()
    instance.fabric_name = "MyFabric"
    path = instance.path
    verb = instance.verb
    ```
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"nd.{self.class_name}")
        self.required_properties.add("fabric_name")
        self._build_properties()
        msg = "ENTERED api.v1.lan_fabric.rest.top_down.fabrics.vrfs."
        msg += f"Vrfs.{self.class_name}"
        self.log.debug(msg)

    def _build_properties(self):
        super()._build_properties()
        self.properties["verb"] = RequestVerb.GET

    @property
    def path(self):
        """
        - Endpoint for VRF GET request.
        - Raise ``ValueError`` if fabric_name is not set.
        """
        return f"{self.path_fabric_name}/vrfs"


class EpVrfPost(Fabrics):
    """
    ## V1 API - Vrfs().EpVrfPost()

    ### Description
    Return endpoint information.

    ### Raises
    -   ``ValueError``: If fabric_name is not set.
    -   ``ValueError``: If fabric_name is invalid.

    ### Path
    -   ``/rest/top-down/fabrics/{fabric_name}/vrfs``

    ### Verb
    -   POST

    ### Parameters
    - fabric_name: string
        - set the ``fabric_name`` to be used in the path
        - required
    -   path: retrieve the path for the endpoint
    -   verb: retrieve the verb for the endpoint

    ### Usage
    ```python
    instance = EpVrfPost()
    instance.fabric_name = "MyFabric"
    path = instance.path
    verb = instance.verb
    ```
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"nd.{self.class_name}")
        self.required_properties.add("fabric_name")
        self._build_properties()
        msg = "ENTERED api.v1.lan_fabric.rest.top_down.fabrics.vrfs."
        msg += f"Vrfs.{self.class_name}"
        self.log.debug(msg)

    def _build_properties(self):
        super()._build_properties()
        self.properties["verb"] = RequestVerb.POST

    @property
    def path(self):
        """
        - Endpoint for VRF POST request.
        - Raise ``ValueError`` if fabric_name is not set.
        """
        return f"{self.path_fabric_name}/vrfs"
