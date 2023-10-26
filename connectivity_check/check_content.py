#     Copyright 2023 Forto Logistics AG & Co. KG.
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

import re

import requests
from requests_toolbelt.utils import dump

from .exceptions import ConnectivityCheckException


def check_content(
    self, target: str, content: str = None, ca: str = None, timeout=10
) -> str:
    """
    Check the content of remote location

    Check the content found at given TARGET against CONTENT regex or plain string.
    Show request details and content without validation pattern.

    Will validate also certificates for HTTPS TARGET, using the system key store.

    Use --ca parameter to load custom CA certificates bundle (PEM) or specify a CA
    certificates directory to lookup certificates by hash.
    """
    response = requests.get(target, timeout=timeout, verify=ca if ca else True)

    request_dump = dump.dump_all(response).decode(response.encoding)
    if content:
        content = str(content)
        check_result = re.search(content, response.text, re.IGNORECASE) is not None
        self._datadog(target=target, check="content", values=check_result)
        if check_result:
            return f"Content from {target} matches »{content}«"
        else:
            raise ConnectivityCheckException(
                f"Content from {target} fails content match »{content}«\n\n"
                + response.text
            )
    else:
        return request_dump
