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

import yaml
from box import Box

from connectivity_check import ConnectivityChecks
from connectivity_check.exceptions import ConnectivityCheckException


@pytest.fixture
def config_file(tmp_path):
    return tmp_path / "config.yaml"


def test_checks_no_checks_sections(config_file):
    config_file.write_text("foo")
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException):
        c.checks(config_file)


def test_checks_no_checks_defined(config_file):
    config_file.write_text("check:\n")
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException):
        c.checks(config_file)


def test_checks_with_config(config_file):
    config_content = {
        "config": {"datadog": "foobar"},
        "checks": [{"cert": {"key": "value"}}],
    }
    config_file.write_text(yaml.safe_dump(config_content))
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException):
        c.checks(config_file)
    assert dict(c._config) == {"datadog": "foobar"}


def test_checks_invalid_check(config_file):
    config_content = {"checks": [{"blubberlutsch": {}}]}
    config_file.write_text(yaml.safe_dump(config_content))
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException) as exc:
        c.checks(config_file)
    assert "Missing key" in exc.value.args[0]


def test_checks_normal(config_file, mocker):
    config_content = {
        "checks": [
            {"cert": {"key": "value"}},
            {"routing": {"key": "value"}},
            {
                "latency": {"key": "value"},
                "content": {"key": "value", "foo": "bar"},
                "cert": {"key": "value"},
            },
        ]
    }
    mocks = Box(
        mocker.patch.multiple(
            ConnectivityChecks,
            check_cert=mocker.DEFAULT,
            check_routing=mocker.DEFAULT,
            check_latency=mocker.DEFAULT,
            check_content=mocker.DEFAULT,
        )
    )
    config_file.write_text(yaml.safe_dump(config_content))
    c = ConnectivityChecks()
    c.checks(config_file, all=True)
    assert mocks.check_cert.call_count == 2
    assert mocks.check_routing.call_count == 1
    assert mocks.check_content.call_count == 1
    assert mocks.check_latency.call_count == 1
    mocks.check_content.assert_called_once_with(key="value", foo="bar")


def test_checks_all_with_error(config_file, mocker):
    config_content = {
        "checks": [
            {"cert": {"key": "value"}},
            {"routing": {"key": "value"}},
            {
                "latency": {"key": "value"},
                "content": {"key": "value", "foo": "bar"},
                "cert": {"key": "value"},
            },
        ]
    }
    mocks = Box(
        mocker.patch.multiple(
            ConnectivityChecks,
            check_cert=mocker.DEFAULT,
            check_routing=mocker.DEFAULT,
            check_latency=mocker.DEFAULT,
            check_content=mocker.DEFAULT,
        )
    )
    mocks.check_latency.side_effect = ConnectivityCheckException
    config_file.write_text(yaml.safe_dump(config_content))
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="Not all checks succesfull"):
        c.checks(config_file, all=True)
    assert mocks.check_cert.call_count == 2
    assert mocks.check_routing.call_count == 1
    assert mocks.check_content.call_count == 1
    assert mocks.check_latency.call_count == 1
    mocks.check_content.assert_called_once_with(key="value", foo="bar")


def test_checks_file_error(config_file):
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="blubberlutsch"):
        c.checks(f"{config_file}.blubberlutsch")


def test_checks_other_error(config_file, mocker):
    config_content = {"checks": [{"cert": {"key": "value"}}]}
    config_file.write_text(yaml.safe_dump(config_content))
    cert_mock = mocker.patch.object(ConnectivityChecks, "check_cert")
    cert_mock.side_effect = Exception("foo error")
    c = ConnectivityChecks()
    with pytest.raises(ConnectivityCheckException, match="foo error"):
        c.checks(config_file)
