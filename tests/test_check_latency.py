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

from connectivity_check.__main__ import ConnectivityCheckException, ConnectivityChecks


@pytest.fixture
def tcp_latency_mock(mocker):
    return mocker.patch("tcp_latency.measure_latency", return_value=[20.1, 30.1, 40.1])


def test_check_latency(tcp_latency_mock):
    checks = ConnectivityChecks()
    result = checks.check_latency(
        target="https://example.com:123", latency=50, verbose=True)
    tcp_latency_mock.assert_called_once_with("example.com", 123, 5, 3, 1, True)
    assert result == "TCP connection latency to example.com:123 is 30 (limit 50)"

def test_check_latency_too_high(tcp_latency_mock):
    checks = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="exceeding the limit of 1"):
        checks.check_latency(target="example.com:123", latency=1, verbose=True)

def test_check_latency_error(tcp_latency_mock):
    tcp_latency_mock.return_value = [] # tcp_latency.measure_latency returns an empty list on any kind of error
    checks = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="TCP connection to example.com:443 failed"):
        checks.check_latency(target="example.com", latency=1)