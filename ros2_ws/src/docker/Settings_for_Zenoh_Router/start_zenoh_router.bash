#!/bin/bash

# TurtleBot4 Umgebung laden
export ROBOT_SETUP=/etc/turtlebot4/setup.bash
source "$ROBOT_SETUP"
source /etc/turtlebot4/aliases.bash

# Start des Zenoh Routers
echo "Start des Zenoh Routers:"
exec /home/ubuntu/zenoh_bridge/zenoh-bridge-ros2dds -c /home/ubuntu/zenoh_bridge/CONFIG_ROUTER.json5
