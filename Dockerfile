FROM ubuntu:18.04

# Use known-compatible versions
ARG GRAFANA_DEB_FILENAME="grafana_5.2.0_amd64.deb"
ARG INFLUXDB_DEB_FILENAME="influxdb_1.5.4_amd64.deb"

ARG GRAFANA_URL="https://s3-us-west-2.amazonaws.com/grafana-releases/release/$GRAFANA_DEB_FILENAME"
ARG INFLUXDB_URL="https://dl.influxdata.com/influxdb/releases/$INFLUXDB_DEB_FILENAME"

# Add environment variables
ENV NHS_FORCE_DB_INIT=false
ENV NHS_FORCE_GF_INIT=false

# Note: if you change the read password, you'll need to manually configure the data source in grafana.
# Since its permissions are read-only I'd just let it be.
ENV NHS_INFLUXDB_GRAFANA_READ_PASSWORD=83geP4LxRutNrZtL6RpL
ENV NHS_INFLUXDB_PYTHON_WRITE_PASSWORD=CyxCD7ahzo4gCrTMQ83f
ENV NHS_INTERNAL_WALLET=1P5PNW6Wd53QiZLdCs9EXNHmuPTX3rD6hW
ENV NHS_WEMO_DEVICE_IP=false
ENV NHS_DEFAULT_ENERGY_COST_FIAT_PER_DAY=0

# FIATs USD, EUR, GBP
ENV NHS_FIAT_CURRENCY="USD"
ENV NHS_ENERGY_COST_FIAT_PER_KWHR=.10


RUN apt-get update && apt-get install -qq -y wget libfontconfig cron python-setuptools python-dev python-pip curl && \
    wget $INFLUXDB_URL &&\
    dpkg -i $INFLUXDB_DEB_FILENAME &&\ 
    rm $INFLUXDB_DEB_FILENAME &&\
    wget $GRAFANA_URL &&\
    dpkg -i $GRAFANA_DEB_FILENAME &&\
    rm $GRAFANA_DEB_FILENAME &&\
    chown -R grafana:grafana "/var/lib/grafana" && \
    chmod 777 "/var/lib/grafana"
    
EXPOSE 3000

COPY /nh-stats /nh-stats/
COPY /grafana_default /grafana_default/
COPY ./run.sh /run.sh
WORKDIR /
ENTRYPOINT [ "/run.sh" ]
