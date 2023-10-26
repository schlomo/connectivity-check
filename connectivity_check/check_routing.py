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
from .exceptions import ConnectivityCheckException
import tcp_latency

import platform
import re
from socket import gethostbyname, gaierror
from urllib.parse import urlparse


class Route:
    "Determine and IPv4 route to a destination"

    def __init__(self, dest: str) -> Route:
        if re.fullmatch("[\d.]+", dest):
            # got IP
            self.ip = dest
            self.destination = dest
        else:
            # got DNS name
            try:
                self.ip = gethostbyname(dest)
            except gaierror as e:
                raise ConnectivityCheckException(
                    f"Could not convert {dest} to IP address: {e}"
                )
            self.destination = f"{dest} ({self.ip})"

        if platform.system() == "Linux":
            # Scapy doesn't support policy routing, see https://github.com/secdev/scapy/issues/836
            # we therefore use Linux-only pyroute2 here
            from pyroute2 import IPRoute

            ipr = IPRoute()

            route_attrs = dict(ipr.route("get", dst=self.ip)[0]["attrs"])
            assert (
                route_attrs["RTA_DST"] == self.ip
            ), f"Route lookup destination mismatch {self.ip} != {route_attrs['RTA_DST']}"
            self.local_ip = route_attrs["RTA_PREFSRC"]
            self.gateway_ip = route_attrs.get("RTA_GATEWAY", "direct")
            device_id = route_attrs["RTA_OIF"]
            self.device = ipr.get_links(device_id)[0].get_attr("IFLA_IFNAME")
        else:
            # use scapy on all non-Linux OS
            # lazy-load scapy as it does a lot upon initialisation and can also print warnings if not disabled via logging
            import logging

            logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
            from scapy.all import conf as scapy_conf

            route_info = scapy_conf.route.route(self.ip)
            self.device = route_info[0]
            self.local_ip = route_info[1]
            self.gateway_ip = route_info[2]

    def compare(self, other: Route, same: bool = True) -> bool:
        return self == other if same else self != other

    def __eq__(self, other: Route) -> bool:
        return (
            self.device == other.device
            and self.local_ip == other.local_ip
            and self.gateway_ip == other.gateway_ip
        )

    def __ne__(self, other: Route) -> bool:
        return not self == other

    def __str__(self) -> str:
        return f"Route to {self.destination} from {self.local_ip} via {self.gateway_ip}/{self.device}"

    __repr__ = __str__


def check_routing(self, target: str, reference: str, same: bool = False):
    """
    Compare IPv4 routing between two destinations

    Compare that the route to TARGET differs from route to REFERENCE.
    Compares gateway IP and local device/IP used to reach the destination

    Check for equality via --same
    """

    # Not dealing with IPv6 as of now because IPv6 might be optional and only one of the two given destinations might
    # be reachable via IPv6. We therefore should determine first what is available for both and then compare that.
    # Will implement when actually needed.

    target_route = Route(target)
    reference_route = Route(reference)

    check_result = reference_route.compare(target_route, same)
    self._datadog(
        target=target, check="routing", values=check_result, device=target_route.device
    )
    if check_result:
        return f"Routing to {target} via {target_route.gateway_ip}/{target_route.device} {'is same as' if same else 'differs from'} route to {reference}"
    else:
        raise ConnectivityCheckException(
            f"Expecting {'equality' if same else 'difference'}, but routing to {target} {'differs from' if same else 'is same as'} route to {reference}.\n"
            + str(reference_route)
            + "\n"
            + str(target_route)
        )
