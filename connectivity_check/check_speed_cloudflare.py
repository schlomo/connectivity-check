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

from cloudflarepycli import cloudflareclass

from .exceptions import ConnectivityCheckException


def check_speed_cloudflare(
    self, latency: int = 50, download: int = 20, upload: int = 5, progress: bool = False
):
    """
    Check the network speed via Cloudflare speed.cloudflare.com

    LATENCY (ms), DOWNLOAD (MB/s) and UPLOAD (MB/s) specify the minimum quality to check against.
    """

    try:
        results = cloudflareclass.cloudflare(printit=progress).runalltests()
    except Exception as e:
        raise ConnectivityCheckException(str(e))

    # import json, pathlib ; pathlib.Path("./out.json").write_text(json.dumps(results, indent=2))

    results = {key: compound["value"] for key, compound in results.items()}
    result_download = results["90th_percentile_download_speed"]
    result_upload = results["90th_percentile_upload_speed"]
    result_latency = results["latency_ms"]
    result_server_description = (
        "speed.cloudflare.com in {test_location_city} ({test_location_region})".format(
            **results
        )
    )
    check_result = (
        result_download >= download
        and result_upload >= upload
        and result_latency <= latency
    )
    self._datadog(
        target="speed.cloudflare.com",
        check="speed_cloudflare",
        values={
            "download": result_download,
            "upload": result_upload,
            "latency": result_latency,
        },
        host=result_server_description,
    )
    if check_result:
        return f"Speedtest to {result_server_description} D:{result_download} U:{result_upload} Mb/s at {result_latency} ms"
    else:
        raise ConnectivityCheckException(
            f"Speedtest insufficient to {result_server_description} D:{result_download} ({download}) U:{result_upload} ({upload}) Mb/s at {result_latency} ({latency}) ms"
        )
