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

import re
import ssl
import socket
from datetime import datetime

from cryptography import x509
from urllib.parse import urlparse

from .exceptions import ConnectivityCheckException


class CertDetails:
    def __init__(self, cert: x509.Certificate) -> None:
        self.issuer = cert.issuer.rfc4514_string()
        self.subject = cert.subject.rfc4514_string()
        self.altNames = cert.extensions.get_extension_for_class(
            x509.SubjectAlternativeName
        ).value.get_values_for_type(x509.DNSName)
        self.not_valid_before = cert.not_valid_before
        self.not_valid_after = cert.not_valid_after
        self.validity = (self.not_valid_after - datetime.now()).days

    def __str__(self) -> str:
        return f"Certificate {self.subject}\n  issued by {self.issuer}\n  alt names {', '.join(self.altNames)}\n  expires in {self.validity} days at {self.not_valid_after}"

    __repr__ = __str__


def check_cert(self, target: str, issuer: str = None, validity: int = 5, timeout=10):
    """
    Check the certificate issuer

    Check the certificate issuer given by TARGET (HOST[:443] or URL) against
    ISSUER regex or plain string.

    Check the certificate expiration given by VALIDITY

    Shows certificate details without validation pattern.

    Accepts also HTTPS URLs.
    Will ignore most TLS certificate errors to retrieve more certificates.
    """

    url = urlparse(target)  # try to decode arg as URL
    if url.scheme == "https" and url.netloc:
        target = url.netloc

    try:
        host, port = target.split(":")
        port = int(port)
    except:
        host = target
        port = 443

    # ignore SSL errors, we always want to fetch the details
    context = ssl._create_unverified_context()
    conn = socket.create_connection((host, port))
    sock = context.wrap_socket(conn, server_hostname=host)
    sock.settimeout(timeout)
    try:
        der_cert = sock.getpeercert(True)
    finally:
        sock.close()

    cert = x509.load_der_x509_certificate(der_cert)
    cert_details = CertDetails(cert)
    if issuer:
        issuer = str(issuer)
        check_result_issuer = (
            re.search(issuer, cert_details.issuer, re.IGNORECASE) is not None
        )
        check_result_validity = cert_details.validity >= validity
        check_result = check_result_issuer and check_result_validity
        self._datadog(target=host, check="cert", values=check_result)
        if check_result:
            return f"Certificate from {host} matches issuer »{issuer}« ({cert_details.issuer}) and expiration in more than {validity} ({cert_details.validity}) days"
        else:
            raise ConnectivityCheckException(
                f"Certificate from {host} fails issuer match »{issuer}« or expires before {validity} days\n"
                + str(cert_details)
            )
    else:
        return f"Fetched X.509 certificate from {host}:{port}\n" + str(cert_details)
