#!/bin/bash

docker volume create nh-stats-influxdb-storage
docker volume create nh-stats-grafana-storage

docker run -d \
  --restart=always \
  --name=nh-stats \
  -p 3001:3000 \
  -v nh-stats-grafana-storage:/var/lib/grafana \
  -v nh-stats-influxdb-storage:/var/lib/influxdb \
  -e NHS_INTERNAL_WALLET=1P5PNW6Wd53QiZLdCs9EXNHmuPTX3rD6 \
  -e NHS_WEMO_DEVICE_IP=false \
  -e NHS_FIAT_CURRENCY="USD" \
  -e NHS_ENERGY_COST_FIAT_PER_KWHR=.1 \
  thechunter/nh-stats:latest
