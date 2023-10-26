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

import speedtest

from .exceptions import ConnectivityCheckException


def check_speed_ookla(
    self, target: int = -1, latency: int = 50, download: int = 20, upload: int = 5
):
    """
    Check the network speed via Oookla speedtest.net

    Check the network speed via the TARGET server id from speedtest.net.
    Use 0 to show a list of closest servers to use.
    Use -1 to use the closest server

    LATENCY (ms), DOWNLOAD (Mb/s) and UPLOAD (Mb/s) specify the minimum quality to check against.
    """

    s = speedtest.Speedtest()
    if target == 0:
        print(
            "Set the TARGET to a speedtest.net server ID. Here are the closest servers:"
        )
        return s.get_closest_servers()
    elif target > 0:
        try:
            server_list = list(s.get_servers([target]).values())[0]  # one in - one out
        except speedtest.NoMatchedServers:
            raise ConnectivityCheckException(f"Speedtest server {target} is invalid")
    else:  # target < 0
        server_list = None  # use default

    s.get_best_server(servers=server_list)
    s.download()
    s.upload()
    result_download = int(s.results.download / 1024 / 1024)
    result_upload = int(s.results.upload / 1024 / 1024)
    result_latency = int(s.results.ping)
    result_server_description = (
        "{id} ({host} by {sponsor} in {name}, {country})".format(**s.results.server)
    )
    check_result = (
        result_download >= download
        and result_upload >= upload
        and result_latency <= latency
    )
    self._datadog(
        target=target,
        check="speed_ookla",
        values={
            "download": result_download,
            "upload": result_upload,
            "latency": result_latency,
        },
        host=result_server_description,
    )
    if check_result:
        return f"Speedtest to {result_server_description} D:{result_download} U:{result_upload} MB/s at {result_latency} ms"
    else:
        raise ConnectivityCheckException(
            f"Speedtest insufficient to {result_server_description} D:{result_download} ({download}) U:{result_upload} ({upload}) MB/s at {result_latency} ({latency}) ms"
        )
