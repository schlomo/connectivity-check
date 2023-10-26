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

from unittest.mock import Mock, call

import pytest

from connectivity_check import ConnectivityChecks


@pytest.fixture
def mock_gauge(mocker):
    return mocker.patch("datadog.statsd.gauge")


# Note: datadog.initialize is called only once, globally, and therefore we don't have a test for it
@pytest.fixture
def mock_initialize(mocker):
    return mocker.patch("datadog.initialize")


def test_datadog_int(mock_gauge, mock_initialize):
    c = ConnectivityChecks(datadog="prefix")
    c._datadog("target", "check", 42, foo="bar", blubber="lutsch")
    mock_gauge.assert_called_once_with(
        "prefix.check", 42, ["target:target", "foo:bar", "blubber:lutsch"]
    )


def test_datadog_bool(mock_gauge, mock_initialize):
    c = ConnectivityChecks(datadog="prefix")
    c._datadog("target", "check", True, foo="bar", blubber="lutsch")
    mock_gauge.assert_called_once_with(
        "prefix.check", 1, ["target:target", "foo:bar", "blubber:lutsch"]
    )


def test_datadog_dict(mock_gauge, mock_initialize):
    c = ConnectivityChecks(datadog="prefix")
    c._datadog("target", "check", {"one": 1, "two": 2}, foo="bar", blubber="lutsch")
    mock_gauge.assert_has_calls(
        [
            call("prefix.check.one", 1, ["target:target", "foo:bar", "blubber:lutsch"]),
            call("prefix.check.two", 2, ["target:target", "foo:bar", "blubber:lutsch"]),
        ]
    )


def test_datadog_disabled(mock_gauge, mock_initialize):
    c = ConnectivityChecks()
    c._datadog("foo", "foo", "foo")
    mock_gauge.assert_not_called()
