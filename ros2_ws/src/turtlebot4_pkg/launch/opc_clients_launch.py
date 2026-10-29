import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():


    return LaunchDescription([

        Node(
            package = 'turtlebot4_pkg',
            executable = 'status_client',
            name = 'status_client_node'
        ),

        Node(
            package = 'turtlebot4_pkg',
            executable = 'command_client',
            name = 'command_client_node'
        ),
    ])