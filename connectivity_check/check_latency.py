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

from .exceptions import ConnectivityCheckException
import tcp_latency

from urllib.parse import urlparse


def check_latency(
    self,
    target: str,
    latency: int,
    timeout: float = 5,
    runs: int = 3,
    wait: float = 1,
    verbose: bool = False,
) -> str:
    """
    Check latency based on TCP connections

    Check that the TCP connection time to target is at most LATENCY milliseconds.
    TARGET can be HOST:PORT, port defaults to 443.
    target can also be a http(s) URL with a port, we only use the host and port.
    """

    url = urlparse(target)  # try to decode arg as URL
    if len(url.netloc) > 0:
        target = url.netloc

    try:
        host, port = target.split(":")
        port = int(port)
    except:
        host = target
        port = 443

    display_dest = f"{host}:{port}"

    measures = tcp_latency.measure_latency(host, port, timeout, runs, wait, verbose)

    if len(measures) > 0:
        average = int(tcp_latency.mean(measures))
        minimum = int(min(measures))
        maximum = int(max(measures))

        check_result = average <= latency
        self._datadog(
            target=target,
            check="latency",
            values={"average": average, "minimum": minimum, "maximum": maximum},
        )
        if check_result:
            return f"TCP connection latency to {display_dest} is {average} (limit {latency})"
        else:
            raise ConnectivityCheckException(
                f"TCP connection latency to {display_dest} is {average} exceeding the limit of {latency}"
            )
    else:
        raise ConnectivityCheckException(f"TCP connection to {display_dest} failed")
