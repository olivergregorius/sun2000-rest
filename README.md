# sun2000-rest

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/olivergregorius/sun2000-rest/Publish?label=Publish&logo=github)](https://github.com/olivergregorius/sun2000-rest/actions/workflows/publish.yml)
[![GitHub](https://img.shields.io/github/license/olivergregorius/sun2000-rest?label=License)](https://github.com/olivergregorius/sun2000-rest/blob/HEAD/LICENSE)
[![Docker](https://img.shields.io/docker/v/olivergregorius/sun2000-rest?label=Tag&logo=docker&sort=semver)](https://hub.docker.com/r/olivergregorius/sun2000-rest)

## Introduction

sun2000-rest provides a RESTful interface for accessing the Sun2000 inverter metrics. This project uses the
[sun2000_modbus](https://github.com/olivergregorius/sun2000_modbus)-library to connect to the Sun2000 inverter. Currently only read-access to the registers is
implemented.

## Requirements

The inverter must be accessible through its internal Wifi access point providing the Modbus TCP interface that the
[sun2000_modbus](https://github.com/olivergregorius/sun2000_modbus)-library connects to.

A possible scenario would be to use a Raspberry Pi connecting its Wifi to the internal Sun2000 Wifi access point, connecting the Ethernet-port to the local LAN
and starting the application. The REST-API should then be accessible on the local LAN IP.

Furthermore, a [Docker image](https://hub.docker.com/r/olivergregorius/run2000-rest) is provided for platforms `amd64` and `arm64`, including all required
libraries, to simplify the setup.

## Usage

### Native Python Application

Given the scenario using a Raspberry Pi as described above:

1. Checkout the repository to a location of your choice
2. Install requirements via pip: `pip install -r requirements.txt`
3. Set the following environment variables:
   ```shell
   export FLASK_APP=./src/main.py
   export INVERTER_HOST=<inverter IP address, usually 192.168.200.1>
   export INVERTER_PORT=<inverter Modbus TCP port, usually 502, or 6607 on newer firmwares>
   export ACCEPTED_API_KEYS=<comma separated list of one or more API keys for authorization>
   ```
   Note that the inverter's IP address is the one from the subnet provided by the inverter's Wifi access point. Usually that is 192.168.200.1.
4. Start the application: `flask run`, the API should now be accessible on `http://<LAN IP>:5000`.

### Docker Container

Given the scenario using a Raspberry Pi as described above:

Run the Docker container with:

```
docker run -d --name sun2000-rest --network host \
-e INVERTER_HOST=<inverter IP address, usually 192.168.200.1> \
-e INVERTER_PORT=<inverter Modbus TCP port, usually 502, or 6607 on newer firmwares> \
-e ACCEPTED_API_KEYS=<comma separated list of one or more API keys for authorization> \
olivergregorius/sun2000-rest:<latest image tag>
```

The API should now be accessible on `http://<LAN IP>:5000`.

### Configuration Options

The application can be configured setting the following environment variables:

| Environment Variable | Description                                                       | Example       | Default Value |
|----------------------|-------------------------------------------------------------------|---------------|---------------|
| INVERTER_HOST        | Inverter IP address, usually 192.168.200.1                        | 192.168.200.1 | 192.168.200.1 |
| INVERTER_PORT        | Inverter Modbus TCP port, usually 502, or 6607 on newer firmwares | 6607          | 6607          |
| ACCEPTED_API_KEYS    | Comma separated list of one or more API keys for authorization    | secretApiKey  |               |
| LOG_LEVEL            | Log level                                                         | DEBUG         | INFO          |

## Provided Endpoints/Resources

The OpenAPI endpoint specification can be found in [./docs/api-specification.yml](./docs/api-specification.yml)
