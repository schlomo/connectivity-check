# Connectivity Check

Python CLI program to check the various aspects of Internet connectivity.
The purpose is to validate a Cloudflare WARP VPN connection and to help validate the Cloudflare network policies.

Currently implements the following type of checks:

1. is google.com routed different compared to baidu.com, to check for VPN routing
2. does google.com use the Cloudflare CA, indicating that TLS inspection is active?
3. is https://google.com/maps actually blocked with a Cloudflare error message?
4. what is the TCP connect latency?
5. what is the Internet speed?

Checks can be specified either via command line or via a YAML file for batch mode.

Optionally, report metrics to DataDog via statsd.

## CLI Interface

```text
NAME
    connectivity-check - Run various network and HTTP connectivity checks

SYNOPSIS
    connectivity-check - COMMAND

DESCRIPTION
    Run given command for single check.
    Use checks command with YAML file for batch mode.

    --datadog PREFIX        Enable DogstatsD mode (UDP localhost:8125) and set prefix for metrics reporting

COMMANDS
    COMMAND is one of the following:

     check_cert
       Check the certificate issuer

     check_content
       Check the content of remote location

     check_latency
       Check latency based on TCP connections

     check_routing
       Compare IPv4 routing between two destinations

     check_speed_cloudflare
       Check the network speed via Cloudflare speed.cloudflare.com

     check_speed_ookla
       Check the network speed via Oookla speedtest.net

     checks
       Run all checks in config file
```

## Development

We use [Python Poetry](https://python-poetry.org/) to manage this project, most important calls are:

* `poetry install` to create a virtual environment (venv) and install the dependencies
* `poetry shell` to enter the venv
* `peotry run pytest` or `pytest` within the venv to run the unit tests
* `poetry build` to create distributable archives in `dist/`

When making changes, please ensure that the test coverage doesn't go down.
