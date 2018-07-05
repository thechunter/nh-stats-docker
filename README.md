# Grafana Docker image

This repository contains everything needed to build the [nh-stats Docker Hub image](https://hub.docker.com/r/thechunter/nh-stats/).

## Building a Custom Image

The included `Dockerfile` sets everything up automatically. Modify the contents of the repository to your liking and then build a new Docker image. I use the included `build.sh` script to create the image and `start_container.sh` to start a container from that image.

## Donations

If you find this work helpful, donations are greatly appreciated!

BTC: 3GQjpuKzGRk4Hzx1CWt5Q4F7FHdvmzFSMy

## Changelog

### v1.0 - July 4, 2018
* Initial release. Built on Grafana 5.2.0 and InfluxDB 1.5.4