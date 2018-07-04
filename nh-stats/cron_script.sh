#!/bin/bash -e
echo "Setting up environment variables..."
source /nh-stats/project_env.sh
echo "Executing Python..."
python /nh-stats/nh-stats.py
echo "Done!"