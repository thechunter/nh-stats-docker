#!/bin/sh

_nhstats_tag=$1


# tags that start with v are treated as releases
if echo "$_nhstats_tag" | grep -q "^v"; then
	_nhstats_version=$(echo "${_nhstats_tag}" | cut -d "v" -f 2)	
	_docker_repo=${2:-thechunter/nh-stats}
else
	_nhstats_version=$_nhstats_tag
	_docker_repo=${2:-thechunter/nh-stats-dev}
fi

echo "pushing ${_docker_repo}:${_nhstats_version}"
docker push "${_docker_repo}:${_nhstats_version}"


echo "pushing ${_docker_repo}:latest"
docker push "${_docker_repo}:latest"
