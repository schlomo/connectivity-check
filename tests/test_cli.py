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

from connectivity_check.__main__ import cli

from connectivity_check import ConnectivityChecks

import pytest
import pytest_mock


def test_cli_no_args(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.argv", ["connectivity-check"])
    cli()
    captured = capsys.readouterr()
    assert "COMMAND" in captured.out


def test_cli_with_valid_args(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockFixture):
    mocker.patch("connectivity_check.ConnectivityChecks.check_cert",
                 return_value=mocker.Mock(return_value="OK"))
    monkeypatch.setattr(
        "sys.argv", ["connectivity-check", "check-cert", "https://example.com"])
    cli()
    captured = capsys.readouterr()
    assert "OK" in captured.out


@pytest.mark.parametrize("args", [[""], ["invalid-check"], ["check-cert", "https://example.com", "--foobar"]])
def test_cli_with_invalid_args(args: list[str], capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.argv", ["connectivity-check"] + args)
    with pytest.raises(SystemExit) as e:
        cli()
    captured = capsys.readouterr()
    assert "Usage" in captured.err
    assert e.value.code == 2


def test_cli_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockFixture):
    monkeypatch.setattr(
        "sys.argv", ["connectivity-check", "check-cert", "https://example.com"])
    mocker.patch("connectivity_check.ConnectivityChecks.check_cert",
                 side_effect=KeyboardInterrupt)
    with pytest.raises(SystemExit) as e:
        cli()
    assert "ABORTED" in e.value.code


def test_cli_file_not_found_error(monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockFixture):
    monkeypatch.setattr(
        "sys.argv", ["connectivity-check", "check-cert", "https://example.com"])
    mocker.patch("connectivity_check.ConnectivityChecks.check_cert",
                 side_effect=FileNotFoundError)
    with pytest.raises(SystemExit) as e:
        cli()
    assert "ERROR: " in e.value.code


def test_cli_bug_error(monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockFixture):
    monkeypatch.setattr(
        "sys.argv", ["connectivity-check", "check-cert", "https://example.com"])
    mocker.patch("connectivity_check.ConnectivityChecks.check_cert",
                 side_effect=Exception)
    with pytest.raises(SystemExit) as e:
        cli()
    assert "BUG ERROR" in e.value.code
    assert "Traceback" in e.value.code
