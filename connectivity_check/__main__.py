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

import traceback
import fire

from .exceptions import *

from . import ConnectivityChecks


def cli():
    try:
        fire.Fire(ConnectivityChecks, name="connectivity-check")
    except KeyboardInterrupt:
        raise SystemExit("ABORTED")
    except (
        ConnectivityCheckException,
        SSLCertVerificationError,
        MissingSchema,
        SSLError,
        TimeoutError,
        FileNotFoundError,
    ) as e:
        raise SystemExit("ERROR: " + str(e))
    except Exception as e:
        raise SystemExit(
            f"BUG ERROR (unexpected {e.__class__} exception):\n"
            + "  \n".join(traceback.format_exception(e))
        )


if __name__ == "__main__":
    cli()  # pragma: no cover
