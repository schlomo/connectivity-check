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

import socket

from box import Box

from connectivity_check import ConnectivityChecks
from connectivity_check.exceptions import ConnectivityCheckException


@pytest.fixture
def cloudflare_result():
    return Box(
        # this is the result of the cloudflarepycli.cloudflareclass.cloudflare.runalltests function:
        {
            "version": {
                "time": 1678374189.9180028,
                "value": "1.7.0"
            },
            "your_ip": {
                "time": 1678374189.966999,
                "value": "37.44.7.130"
            },
            "your_ISP": {
                "time": 1678374190.3239229,
                "value": "SysEleven"
            },
            "test_location_code": {
                "time": 1678374190.323925,
                "value": "FRA"
            },
            "test_location_city": {
                "time": 1678374190.375762,
                "value": "Frankfurt"
            },
            "test_location_region": {
                "time": 1678374190.375764,
                "value": "Europe"
            },
            "latency_ms": {
                "time": 1678374192.015031,
                "value": 17.94
            },
            "Jitter_ms": {
                "time": 1678374192.0150359,
                "value": 2.43
            },
            "100kB_download_Mbps": {
                "time": 1678374193.044225,
                "value": 85.75
            },
            "1MB_download_Mbps": {
                "time": 1678374194.1993668,
                "value": 123.15
            },
            "10MB_download_Mbps": {
                "time": 1678374198.578162,
                "value": 123.9
            },
            "25MB_download_Mbps": {
                "time": 1678374205.641185,
                "value": 118.9
            },
            "90th_percentile_download_speed": {
                "time": 1678374205.641788,
                "value": 132.81
            },
            "100kB_upload_Mbps": {
                "time": 1678374206.030344,
                "value": 28.04
            },
            "1MB_upload_Mbps": {
                "time": 1678374206.688677,
                "value": 93.52
            },
            "10MB_upload_Mbps": {
                "time": 1678374209.82975,
                "value": 112.68
            },
            "90th_percentile_upload_speed": {
                "time": 1678374209.830365,
                "value": 112.4
            }
        }
    )


def test_cloudflare_good(mocker, cloudflare_result):
    mocker.patch(
        "cloudflarepycli.cloudflareclass.cloudflare.runalltests", return_value=cloudflare_result)
    c = ConnectivityChecks()
    result = c.check_speed_cloudflare()
    assert result == "Speedtest to speed.cloudflare.com in Frankfurt (Europe) D:132.81 U:112.4 Mb/s at 17.94 ms"


def test_cloudflare_general_error(requests_mock):
    requests_mock.get("//speed.cloudflare.com/cdn-cgi/trace",
                      exc=socket.gaierror("[Errno 8] nodename nor servname provided, or not known"))
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="Errno 8"):
        c.check_speed_cloudflare()


def test_cloudflare_latency_error(mocker, cloudflare_result):
    cloudflare_result.latency_ms.value = 1000.1
    mocker.patch(
        "cloudflarepycli.cloudflareclass.cloudflare.runalltests", return_value=cloudflare_result)
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="Speedtest insufficient.*1000.1.*ms"):
        c.check_speed_cloudflare()


def test_cloudflare_download_error(mocker, cloudflare_result):
    cloudflare_result["90th_percentile_download_speed"].value = 1.1
    mocker.patch(
        "cloudflarepycli.cloudflareclass.cloudflare.runalltests", return_value=cloudflare_result)
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="Speedtest insufficient.*D:1.1.*Mb/s"):
        c.check_speed_cloudflare()


def test_cloudflare_upload_error(mocker, cloudflare_result):
    cloudflare_result["90th_percentile_upload_speed"].value = 1.1
    mocker.patch(
        "cloudflarepycli.cloudflareclass.cloudflare.runalltests", return_value=cloudflare_result)
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="Speedtest insufficient.*U:1.1.*Mb/s"):
        c.check_speed_cloudflare()
