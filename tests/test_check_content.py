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
from re_assert import Matches

from connectivity_check import ConnectivityChecks
from connectivity_check.exceptions import ConnectivityCheckException


@pytest.fixture(autouse=True)
def mock(requests_mock):
    requests_mock.get("https://example.com", text="Lorem ipsum dolor sit amet")
    return requests_mock


def test_check_content_matches():
    result = ConnectivityChecks().check_content("https://example.com", "Lorem ipsum")
    assert result == "Content from https://example.com matches »Lorem ipsum«"


def test_check_content_with_regex():
    result = ConnectivityChecks().check_content("https://example.com", "Lorem.*amet")
    assert result == "Content from https://example.com matches »Lorem.*amet«"


def test_check_content_not_matching():
    with pytest.raises(ConnectivityCheckException):
        ConnectivityChecks().check_content("https://example.com", "foo")


def test_check_content_dump_content():
    result = ConnectivityChecks().check_content("https://example.com")
    # dump shows < request ... and > response
    pattern = Matches("(?s)< GET.*> HTTP/.*200.*Lorem ipsum dolor sit amet")
    pattern.assert_matches(result)
