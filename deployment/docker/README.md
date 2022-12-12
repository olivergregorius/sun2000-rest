# sun2000-rest

RESTful interface for reading Huawei Sun2000 inverter metrics.

## Latest tag

- <latest_tag_placeholder>, latest

## Supported platforms

- amd64
- arm64

## How to use this image

### Basic configuration

```shell
docker run -d --name sun2000-rest \
-p 5000:5000 \
-e ACCEPTED_API_KEYS=secretApiKey \
olivergregorius/sun2000-rest:latest
```

### Configuration options

The application can be configured setting the following environment variables:

| Environment Variable | Description                                                       | Example                          | Default Value |
|----------------------|-------------------------------------------------------------------|----------------------------------|---------------|
| INVERTER_HOST        | Inverter IP address, usually 192.168.200.1                        | 192.168.200.1                    | 192.168.200.1 |
| INVERTER_PORT        | Inverter Modbus TCP port, usually 502, or 6607 on newer firmwares | 6607                             | 6607          |
| ACCEPTED_API_KEYS    | Comma separated list of one or more API keys for authorization    | secretApiKey,anotherSecretApiKey |               |
| LOG_LEVEL            | Log level                                                         | DEBUG                            | INFO          |
| UWSGI_WORKERS        | Set amount of workers/processes                                   | 5                                | 5             |

## Find Me

* [GitHub](https://github.com/olivergregorius/sun2000-rest)

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/olivergregorius/sun2000-rest/tags).

## Authors

* **Oliver Gregorius** - [olivergregorius](https://github.com/olivergregorius)

See also the list of [contributors](https://github.com/olivergregorius/sun2000-rest/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/olivergregorius/sun2000-rest/blob/HEAD/LICENSE) file for details.
