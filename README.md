# Grafana Docker image

This repository contains everything needed to build the [nh-stats Docker Hub image](https://hub.docker.com/r/thechunter/nh-stats/).

## Building a Custom Image

The included `Dockerfile` sets everything up automatically. Modify the contents of the repository to your liking and then build a new Docker image. I use the included `build.sh` script to create the image and `start_container.sh` to start a container from that image.

## Donations

If you find this work helpful, donations are greatly appreciated!

BTC: 3GQjpuKzGRk4Hzx1CWt5Q4F7FHdvmzFSMy

## Changelog

### v1.2 - July 31, 2018
* Added support for multiple NH wallets. Separate wallet addresses with `,` when configuring the Docker container
* Added support for multiple WeMo Insight plugs. Separate IP addresses with `,` when configuring the Docker container
* Various bug fixes that improve logged estimates
* See [closed issues](https://github.com/thechunter/nh-stats-docker/milestone/3?closed=1) for more details

### v1.1 - July 8, 2018
* Improved accuracy of plotted estimates by tightening up timings
* See [closed issues](https://github.com/thechunter/nh-stats-docker/milestone/1?closed=1) for more details

### v1.0 - July 4, 2018
* Initial release. Built on Grafana 5.2.0 and InfluxDB 1.5.4