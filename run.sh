#!/bin/bash -e

INFLUXDB_PATH="/var/lib/influxdb/data/nhstats"
GRAFANA_PATH="/var/lib/grafana"

influxd &
sleep 2

PERFORM_INIT=false


if [ "$NHS_FORCE_DB_INIT" = false ] ;
then

    if find "$INFLUXDB_PATH" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
      printf "Existing database found! Inheriting.\n"
    else
      # If the database doesn't exist already, we'll set it up
      printf "Existing database not found. Setting up as new.\n"
      PERFORM_INIT=true    
    fi    
else
    printf "Forcing initialization, this may overwrite existing InfluxDB contents\n"
    PERFORM_INIT=true
fi

if [ "$PERFORM_INIT" = true ] ;
then

  #Configure InfluxDB
  printf "Configuring InfluxDB...\n"
  curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE nhstats"
  curl -POST http://localhost:8086/query --data-urlencode "q=CREATE USER pythonwriter WITH PASSWORD '$NHS_INFLUXDB_PYTHON_WRITE_PASSWORD'"
  curl -POST http://localhost:8086/query --data-urlencode "q=CREATE USER grafanareader WITH PASSWORD '$NHS_INFLUXDB_GRAFANA_READ_PASSWORD'"
  curl -POST http://localhost:8086/query --data-urlencode "q=GRANT ALL ON nhstats TO pythonwriter"
  curl -POST http://localhost:8086/query --data-urlencode "q=GRANT READ ON nhstats TO grafanareader"
fi


if [ "$NHS_FORCE_GF_INIT" = false ] ;
then

    if find "$GRAFANA_PATH" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
      printf "Existing grafana found! Inheriting.\n"
    else
      printf "Copying over golden Grafana directory as a sane default.\n"
      PERFORM_INIT=true    
    fi    
else
    printf "Forcing initialization, this will overwrite existing Grafana contents\n"
    PERFORM_INIT=true
fi


if [ "$PERFORM_INIT" = true ] ;
then  
  printf "Copying over golden Grafana directory as a sane default.\n"
  cp -r /grafana_default/* $GRAFANA_PATH
fi

chown -R grafana:grafana /var/lib/grafana

#Start grafana
service grafana-server start

if [ "$PERFORM_INIT" = true ] ;
then

    #Install plugins
    grafana-cli plugins install petrslavotinek-carpetplot-panel 

    #Restart grafana
    service grafana-server restart

fi

# Set up Python dependencies
pip install pywemo

# Copy over our environment variables so cron can get them
printenv | sed 's/^\(.*\)$/export \1/g' > /nh-stats/project_env.sh
chmod +x /nh-stats/project_env.sh

crontab /nh-stats/nh-stats-cron
service cron start

printf "Finished!\n"

cleanup ()                                                                 
{                                                                          
  kill -s SIGTERM $!                                                         
  exit 0                                                                     
}                                                                          
                                                                           
trap cleanup SIGINT SIGTERM                                                
                                                                           
while [ 1 ]                                                                
do                                                                         
  sleep 60 &                                                             
  wait $!                                                                
done