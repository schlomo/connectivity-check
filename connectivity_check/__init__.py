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

from __future__ import annotations
from box import Box


class ConnectivityChecks(object):
    """
    Run various network and HTTP connectivity checks

    Run given command for single check.
    Use checks command with YAML file for batch mode.

    --datadog PREFIX        Enable DogstatsD mode (UDP localhost:8125) and set prefix for metrics reporting

    """

    from .check_cert import check_cert
    from .check_content import check_content
    from .check_routing import check_routing
    from .check_latency import check_latency
    from .check_speed_ookla import check_speed_ookla
    from .check_speed_cloudflare import check_speed_cloudflare
    from .checks import checks

    from .datadog import _datadog

    def _update_config(self, **kwargs):
        self._config.update(kwargs)

    def __init__(self, datadog: str = None) -> ConnectivityChecks:
        self._config = Box()
        self._update_config(datadog=datadog)
