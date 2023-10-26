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

from pathlib import Path
from datetime import timedelta
from cryptography import x509

import pytest
from re_assert import Matches
from freezegun import freeze_time

from connectivity_check import ConnectivityChecks
from connectivity_check.check_cert import CertDetails
from connectivity_check.exceptions import ConnectivityCheckException

# Notes:
# We use a test certificate that is generated via the cert_test_der script and then
# we use @freeze_time to set a fake date to match this certificate. The freeze date is
# automatically set to the start date of the test certificate so that it is safe to regenerate it

# read test certificate and start date
with open(Path(__file__).parent / "cert.der", "rb") as f:
    test_certificate_der = f.read()
test_certificate = x509.load_der_x509_certificate(test_certificate_der)
cert_details = CertDetails(test_certificate)
test_certificate_start_date = cert_details.not_valid_before


@pytest.fixture(autouse=True)
def check_cert_mock(mocker):
    """
    Mock away socket and inject our test SSL certificate
    """
    mock_socket = mocker.Mock()
    mock_socket.getpeercert.return_value = test_certificate_der
    mocker.patch("socket.create_connection")
    mocker.patch("ssl.SSLContext.wrap_socket", return_value=mock_socket)
    mocker.patch("socket.socket")
    mocker.patch("socket.socket.connect")
    mocker.patch("socket.socket.close")


@freeze_time(test_certificate_start_date)
def test_check_cert_info():
    pattern = Matches("(?s)Fetched.*808.*issued.*example.*expires in 10 days")
    result = ConnectivityChecks().check_cert(target="https://www.example.com:808")
    pattern.assert_matches(result)


@freeze_time(test_certificate_start_date)
def test_check_cert_all_good():
    expected = "Certificate from www.example.com matches issuer »example« (CN=www.example.com,O=MyCompany,C=US) and expiration in more than 5 (10) days"
    result = ConnectivityChecks().check_cert(
        target="www.example.com", issuer="example", validity=5
    )
    assert result == expected


@freeze_time(test_certificate_start_date)
def test_check_cert_expires_soon():
    with pytest.raises(ConnectivityCheckException, match="(?s)fails.*expires.*10 days"):
        ConnectivityChecks().check_cert(
            target="www.example.com", issuer="example", validity=50
        )


@freeze_time(test_certificate_start_date)
def test_check_cert_wrong_issuer():
    with pytest.raises(
        ConnectivityCheckException,
        match="(?s)fails.*match.*no-example.*www.example.com",
    ):
        ConnectivityChecks().check_cert(
            target="www.example.com", issuer="no-example", validity=50
        )


@freeze_time(test_certificate_start_date + timedelta(days=50))
def test_check_cert_already_expired():
    # travel 50 days in the future of certificate which was created with 10 days validity -> -40 days ago expired
    with pytest.raises(
        ConnectivityCheckException, match="(?s)fails.*expires.*-40 days"
    ):
        ConnectivityChecks().check_cert(
            target="www.example.com", issuer="example", validity=50
        )
