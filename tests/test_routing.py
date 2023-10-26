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

import pytest
from socket import gaierror
from connectivity_check import ConnectivityChecks
from connectivity_check.check_routing import Route
from connectivity_check.exceptions import ConnectivityCheckException

# some test consts

LOCAL_IP = "1.2.1.1"
DESTINATION = "example.com"
DESTINATION_IP = "1.2.3.4"
GATEWAY_IP = "1.2.0.1"
DEVICE_ID = 42
DEVICE = "eth0"


@pytest.fixture
def mock_gethostbyname(mocker):
    return mocker.patch(
        "connectivity_check.check_routing.gethostbyname", return_value=DESTINATION_IP
    )


@pytest.fixture
def mock_routing(mocker):
    linux = mocker.patch("pyroute2.IPRoute")
    linux().route.return_value = [
        {
            "attrs": {
                "RTA_DST": DESTINATION_IP,
                "RTA_PREFSRC": LOCAL_IP,
                "RTA_OIF": DEVICE_ID,
                "RTA_GATEWAY": GATEWAY_IP,
            }
        }
    ]
    linux().get_links().__getitem__().get_attr.return_value = DEVICE
    other = mocker.patch(
        "scapy.all.conf.route.route", return_value=[DEVICE, LOCAL_IP, GATEWAY_IP]
    )
    return {"linux": linux, "other": other}


@pytest.fixture
def mock_platform_system(mocker):
    return mocker.patch("platform.system")


@pytest.fixture(params=["Linux", "Other"])
def platform_system(request, mock_platform_system):
    mock_platform_system.return_value = request.param
    return request.param


def test_route_init_ip(mock_gethostbyname, mock_routing, platform_system):
    route = Route(DESTINATION_IP)
    assert route.ip == DESTINATION_IP
    assert route.destination == DESTINATION_IP
    assert route.local_ip == LOCAL_IP
    assert route.gateway_ip == GATEWAY_IP
    assert route.device == DEVICE


def test_route_init_dns(mock_gethostbyname, mock_routing, platform_system):
    route = Route(DESTINATION)
    assert route.ip == DESTINATION_IP
    assert route.destination == f"{DESTINATION} ({DESTINATION_IP})"


def test_route_dns_error(mock_gethostbyname, platform_system):
    mock_gethostbyname.side_effect = gaierror("foobar")
    with pytest.raises(ConnectivityCheckException, match="foobar"):
        Route(DESTINATION)


def test_check_same_routing(mock_gethostbyname, mock_routing, platform_system):
    connectivity_checks = ConnectivityChecks()
    result = connectivity_checks.check_routing(DESTINATION, "target.com", same=True)
    assert (
        result
        == "Routing to example.com via 1.2.0.1/eth0 is same as route to target.com"
    )


def test_check_different_routing(mock_gethostbyname, mock_routing, platform_system):
    connectivity_checks = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="Expecting difference"):
        connectivity_checks.check_routing(DESTINATION, "target.com", same=False)
