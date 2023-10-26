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

import datadog
from datadog import statsd
from typing import Union

__initialized = False

DD_OPTIONS = {"statsd_host": "127.0.0.1", "statsd_port": 8125}


def submit_datadog(metric: str, value, tags: list):
    global __initialized
    if not __initialized:
        datadog.initialize(**DD_OPTIONS)
        __initialized = True
    statsd.gauge(metric, value, tags)
    print(f"DD: {metric} = {value} / {tags}")


def _datadog(
    self, target: str, check: str, values: Union[bool, int, str, dict], *args, **kwargs
):
    if "datadog" in self._config and self._config.datadog:
        tags = [f"target:{target}"] + [
            f"{key}:{value}" for key, value in kwargs.items()
        ]
        metric_name = f"{self._config.datadog}.{check}"
        if type(values) is dict:
            for key, value in values.items():
                submit_datadog(f"{metric_name}.{key}", value, tags)
        else:
            if type(values) is bool:
                # convert to 1 for True and 0 for False
                values = [0, 1][values]
            submit_datadog(metric_name, values, tags)
