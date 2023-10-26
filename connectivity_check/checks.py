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

import yaml
from schema import Schema, Optional, Or, SchemaError
from .exceptions import ConnectivityCheckException

config_schema = Schema(
    {
        Optional("config"): {Optional("datadog", default=None): Or(str, None)},
        "checks": [
            {
                Or(
                    "cert",
                    "content",
                    "routing",
                    "latency",
                    "speed_ookla",
                    "speed_cloudflare",
                    error="Invalid check type",
                ): dict
            }
        ],
    }
)


def checks(self, config: str, all: bool = False):
    """
    Run all checks in config file

    Run all checks defined in CONFIG file. Fail on first failed check unless ALL is set.

    Config file format is YAML like this:

    config:
        datadog: prefix

    checks:
        - cert:
            target: host:port
            issuer: foobar
        - content:
            target: url
            content: something
        - routing:
            target: host
            reference: otherhost
        - latency:
            target: host:port
            max: 200
        - speed_ookla:
            target: Ookla-ID
            latency: 200
        - speed_cloudflare:
            latency: 200

    Entries can be repeated to different checks
    """

    try:
        with open(config) as yaml_config_file:
            yaml_data = yaml.safe_load(yaml_config_file)
        yaml_data = config_schema.validate(yaml_data)
    except SchemaError as se:
        raise ConnectivityCheckException(
            f"Configuration file {config} has an error:\n"
            + str(se)
            + "\n"
            + self.checks.__doc__
        )
    except Exception as e:
        raise ConnectivityCheckException(str(e))

    if "config" in yaml_data:
        self._update_config(**yaml_data["config"])
    checks_to_run = yaml_data["checks"]

    errors = []
    success = []
    for check_dict in checks_to_run:
        for check, kwargs in check_dict.items():
            function_name = "check_" + check
            status = "FAILED"
            description = f"Check {function_name}({str(kwargs)})"
            try:
                try:
                    result = getattr(self, function_name)(**kwargs)
                except TypeError as e:
                    raise ConnectivityCheckException(
                        f"Error in check parameters: {e}\nProblematic parameter block: {kwargs}\nUse {function_name} --help for details"
                    )
                print(result)
                success.append((description, result))
                status = "OK"
            except ConnectivityCheckException as e:
                if all:
                    print(e)
                    errors.append((description, e))
                else:
                    raise e
            except Exception as e:
                raise ConnectivityCheckException(str(e))
            finally:
                print(description + " " + status)

    print(f"{len(errors)} failed and {len(success)} successful checks")
    if all and len(errors) > 0:
        raise ConnectivityCheckException("Not all checks succesfull")
