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

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Allen Robel"

import logging

from ..federation import Federation


class V4(Federation):
    """
    ## v1 API enpoints - Api().V1()

    ### Description
    Common methods and properties for API v1 subclasses.

    ### Path
    ``/nexus/api/federation/v4``
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"nd.{self.class_name}")
        self.v4 = f"{self.federation}/v4"

        msg = "ENTERED ep.nexus.api.federation.v4.V4()"
        self.log.debug(msg)
