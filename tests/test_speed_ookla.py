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
from box import Box

from speedtest import NoMatchedServers

from connectivity_check import ConnectivityChecks
from connectivity_check.exceptions import ConnectivityCheckException

server = {
    'url': 'http://example-speedtest-server.com:8080',
    'lat': '12.34',
    'lon': '56.78',
    'name': 'Test Server',
    'country': 'Testland',
    'cc': 'TL',
    'sponsor': 'Test Sponsor',
    'id': '12345',
    'host': 'example-speedtest-server.com:8080',
    'd': 123.123,
    'latency': 10
}

results = Box({
    'download': 100 * 1024 * 1024,
    'upload': 10 * 1024 * 1024,
    'ping': 10,
    'server': server
})

@pytest.fixture
def mock_speedtest(mocker):
    global server, results
    mock = mocker.patch("speedtest.Speedtest")
    mock().servers = {123.123: [server]}
    mock().get_best_server.return_value = server
    mock().get_closest_servers.return_value = [server]
    # key is distance and value is a list of servers, usually contains only one server
    mock().get_servers.return_value = mock().servers
    mock().results = results
    return mock


def test_speed_ookla(mock_speedtest):
    result = ConnectivityChecks().check_speed_ookla()
    assert result == "Speedtest to 12345 (example-speedtest-server.com:8080 by Test Sponsor in Test Server, Testland) D:100 U:10 MB/s at 10 ms"


def test_speed_ookla_target(mock_speedtest):
    result = ConnectivityChecks().check_speed_ookla(target=12345)
    assert result == "Speedtest to 12345 (example-speedtest-server.com:8080 by Test Sponsor in Test Server, Testland) D:100 U:10 MB/s at 10 ms"


def test_speed_ookla_target_invalid(mock_speedtest):
    mock_speedtest().get_servers.side_effect = NoMatchedServers
    with pytest.raises(ConnectivityCheckException, match="Speedtest server 54321 is invalid"):
        ConnectivityChecks().check_speed_ookla(target=54321)


def test_speed_ookla_target_zero(capsys, mock_speedtest):
    result = ConnectivityChecks().check_speed_ookla(target=0)
    captured = capsys.readouterr()
    assert captured.out == "Set the TARGET to a speedtest.net server ID. Here are the closest servers:\n"
    assert result == [server]

def test_speed_ookla_too_slow(mock_speedtest):
    with pytest.raises(ConnectivityCheckException, match="Speedtest insufficient to 12345"):
        ConnectivityChecks().check_speed_ookla(target=12345, latency=5, download=50, upload=20)
