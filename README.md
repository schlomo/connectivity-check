# Connectivity Check

Python CLI program to check the various aspects of Internet connectivity.

This tool has been written to validate the network routing configuration,
especially in the context of a split tunnel VPN connection and to help validate
network policies.

## Installation

Install from [PyPI](https://pypi.org/project/connectivity-check):

```text
pip install connectivity-check
```

## Features

Currently implements the following features:

### Split Tunnel Routing

Check if the routing for a given destination is different compared to a
reference destination. For example, check if the routing for `google.com` is
different compared to `baidu.com` for a given VPN connection that should only
route `google.com` through the VPN.

### TLS Certificate Authority Inspection

Check if the TLS certificate for a given destination is issued by a given
certificate authority. For example, check if the TLS certificate for
`google.com` is issued by Cloudflare, indicating that TLS interception is
active.

This can also be used to validate if

1. the TLS certificate is issued by a given desired CA
2. the TLS certificate is valid for a minimum amount of time and not expired

### HTTP(S) Response Content Inspection

Check if the HTTP(S) response content for a given destination contains a given
string. For example, check if the HTTP(S) response content for `bad-site.com`
contains the string `Access Forbidden` to validate a policy that forbids access
to `bad-site.com`.

### TCP Connect Latency

Check the TCP connect latency for a given destination. For example, check the
TCP connect latency for `google.com` to validate the latency for a network or
VPN connection.

### Internet Speed

Check the Internet speed via [Cloudflare Speed Test](https://speed.cloudflare.com/)
or [Ookla Speedtest](https://www.speedtest.net/). For example, check the Internet
speed for a network or VPN connection.

### Batch Mode

Checks can be specified either individually via command line or - to specify
multiple checks - via a YAML file for batch mode.

See [successfulchecks.yaml](./successfulchecks.yaml) and the other YAML files
for an example.

### DataDog reporting

Optionally, report metrics to DataDog via a locally running statsd under a given
prefix.

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

Example output of all checks passing:

```text
$ connectivity-check checks successfulchecks.yaml
DD: schlomo.cert = 1 / ['target:google.com']
Certificate from google.com matches issuer »Google« (CN=GTS CA 1C3,O=Google Trust Services LLC,C=US) and expiration in more than 5 (62) days
Check check_cert({'target': 'google.com', 'issuer': 'Google'}) OK
DD: schlomo.content = 1 / ['target:https://google.com/drive']
Content from https://google.com/drive matches »download«
Check check_content({'target': 'https://google.com/drive', 'content': 'download'}) OK
DD: schlomo.routing = 1 / ['target:google.com', 'device:en7']
Routing to google.com via 192.168.11.1/en7 is same as route to mail.google.com
Check check_routing({'target': 'google.com', 'reference': 'mail.google.com', 'same': True}) OK
DD: schlomo.latency.average = 21 / ['target:google.com']
DD: schlomo.latency.minimum = 19 / ['target:google.com']
DD: schlomo.latency.maximum = 26 / ['target:google.com']
TCP connection latency to google.com:443 is 21 (limit 150)
Check check_latency({'target': 'https://google.com/', 'latency': 150}) OK
DD: schlomo.speed_cloudflare.download = 213.05 / ['target:speed.cloudflare.com', 'host:speed.cloudflare.com in Berlin (Land Berlin)']
DD: schlomo.speed_cloudflare.upload = 40.45 / ['target:speed.cloudflare.com', 'host:speed.cloudflare.com in Berlin (Land Berlin)']
DD: schlomo.speed_cloudflare.latency = 20.83 / ['target:speed.cloudflare.com', 'host:speed.cloudflare.com in Berlin (Land Berlin)']
Speedtest to speed.cloudflare.com in Berlin (Land Berlin) D:213.05 U:40.45 Mb/s at 20.83 ms
Check check_speed_cloudflare({'latency': 150}) OK
0 failed and 5 successful checks
```

Example output of failing checks:

```text
$ connectivity-check checks failingchecks.yaml
Certificate from google.com matches issuer »google« (CN=GTS CA 1C3,O=Google Trust Services LLC,C=US) and expiration in more than 5 (62) days
Check check_cert({'target': 'google.com', 'issuer': 'google'}) OK
Check check_content({'target': 'https://ifconfig.me/all', 'content': 'yahoo'}) FAILED
ERROR: Content from https://ifconfig.me/all fails content match »yahoo«

ip_addr: 2003:ea:XXXX:XXXX:XXXX:XXXX
remote_host: unavailable
user_agent: python-requests/2.31.0
port: 53210
language:
referer:
connection:
keep_alive:
method: GET
encoding: gzip, deflate
mime: */*
charset:
via: 1.1 google
```

## Development

We use [Python Poetry](https://python-poetry.org/) to manage this project, most
important calls are:

* `poetry install` to create a virtual environment (venv) and install the
  dependencies
* `poetry shell` to enter the venv
* `peotry run pytest` or `pytest` within the venv to run the unit tests
* `poetry build` to create distributable archives in `dist/`

When making changes, please ensure that the test coverage doesn't go down.

This project uses [Fire](https://github.com/google/python-fire) to expose the
`ConnectivityChecks`  class as a CLI. The individual check functions can also
be imported and used directly.

## License

This project is licensed under the Apache License, Version 2.0 - see the
[LICENSE](./LICENSE) file for details.

## Acknowledgments

This tool was developy by Schlomo Schapiro at [Forto](https://forto.com/) and
then [released](https://github.com/freight-hub/connectivity-check) as Open
Source. From there it was forked by [Schlomo Schapiro](https://github.com/schlomo)
and published to [PyPI](https://pypi.org/project/connectivity-check) to ensure
ongoing maintenance and support.
