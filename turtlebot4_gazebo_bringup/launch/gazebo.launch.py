# Copyright 2023 Clearpath Robotics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @author Roni Kreinin (rkreinin@clearpathrobotics.com)

import os

from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.actions import SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import EnvironmentVariable, LaunchConfiguration


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='use_sim_time'),
    DeclareLaunchArgument('world', default_value='',
                          description='Gazebo World'),
    DeclareLaunchArgument('model', default_value='standard',
                          choices=['standard', 'lite'],
                          description='Turtlebot4 Model'),
]


def generate_launch_description():

    # Directories
    # pkg_turtlebot4_ignition_bringup = get_package_share_directory(
    #     'turtlebot4_ignition_bringup')
    # pkg_turtlebot4_ignition_gui_plugins = get_package_share_directory(
    #     'turtlebot4_ignition_gui_plugins')
    pkg_turtlebot4_gazebo_bringup = get_package_share_directory(
        'turtlebot4_gazebo_bringup')
    pkg_turtlebot4_description = get_package_share_directory(
        'turtlebot4_description')
    pkg_irobot_create_description = get_package_share_directory(
        'irobot_create_description')
    # pkg_irobot_create_ignition_bringup = get_package_share_directory(
    #     'irobot_create_ignition_bringup')
    pkg_irobot_create_gazebo_bringup = get_package_share_directory(
        'irobot_create_gazebo_bringup')
    pkg_irobot_create_ignition_plugins = get_package_share_directory(
        'irobot_create_ignition_plugins')
    pkg_ros_ign_gazebo = get_package_share_directory(
        'ros_ign_gazebo')

    # # Set ignition resource path
    # ign_resource_path = SetEnvironmentVariable(
    #     name='IGN_GAZEBO_RESOURCE_PATH',
    #     value=[
    #         os.path.join(pkg_turtlebot4_ignition_bringup, 'worlds'), ':' +
    #         os.path.join(pkg_irobot_create_ignition_bringup, 'worlds'), ':' +
    #         str(Path(pkg_turtlebot4_description).parent.resolve()), ':' +
    #         str(Path(pkg_irobot_create_description).parent.resolve())])

    # ign_gui_plugin_path = SetEnvironmentVariable(
    #     name='IGN_GUI_PLUGIN_PATH',
    #     value=[
    #         os.path.join(pkg_turtlebot4_ignition_gui_plugins, 'lib'), ':' +
    #         os.path.join(pkg_irobot_create_ignition_plugins, 'lib')])

    # Paths
    # ign_gazebo_launch = PathJoinSubstitution(
    #     [pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py'])

    # # Ignition gazebo
    # ignition_gazebo = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([ign_gazebo_launch]),
    #     launch_arguments=[
    #         ('ign_args', [LaunchConfiguration('world'),
    #                       '.sdf',
    #                       ' -v 4',
    #                       ' --gui-config ',
    #                       PathJoinSubstitution(
    #                         [pkg_turtlebot4_ignition_bringup,
    #                          'gui',
    #                          LaunchConfiguration('model'),
    #                          'gui.config'])])
    #     ]
    # )

    # PathJoinSubstitution([pkg_irobot_create_gazebo_bringup, 'worlds', 'small_house.world'])
    world_path = LaunchConfiguration('world')

    # Set ignition resource path
    gz_resource_path = SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=[
                                                EnvironmentVariable('GAZEBO_MODEL_PATH',
                                                                    default_value=''),
                                                '/usr/share/gazebo-11/models/',
                                                ':' + os.path.join(pkg_turtlebot4_gazebo_bringup, 'worlds'),
                                                ':' + os.path.join(pkg_irobot_create_gazebo_bringup, 'worlds')
                                                # ':' + str(Path(pkg_irobot_create_description).parent.resolve()),
                                                # ':' + str(Path(pkg_turtlebot4_description).parent.resolve())

                                                ])

    # Set GAZEBO_MODEL_URI to empty string to prevent Gazebo from downloading models
    gz_model_uri = SetEnvironmentVariable(name='GAZEBO_MODEL_URI', value=[''])

    gazebo_params_yaml_file = os.path.join(
        pkg_irobot_create_gazebo_bringup, 'config', 'gazebo_params.yaml')

    # Gazebo server
    gzserver = ExecuteProcess(
        cmd=['gzserver',
             '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             world_path,
             'extra-gazebo-args', '--ros-args', 
            #  '--log-level', 'debug'
             '--params-file', gazebo_params_yaml_file
             ],
        output='screen',
    )

    # Gazebo client
    gzclient = ExecuteProcess(
        cmd=['gzclient', '--verbose'],
        output='screen',
        # condition=IfCondition(use_gazebo_gui),
    )

    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    # IGN processes
    # ld = LaunchDescription(ARGUMENTS)
    # ld.add_action(ign_resource_path)
    # ld.add_action(ign_gui_plugin_path)
    # ld.add_action(ignition_gazebo)
    # Gazebo processes
    # ld.add_action(LogInfo(msg=EnvironmentVariable('GAZEBO_MODEL_PATH')))
    ld.add_action(gz_resource_path)
    ld.add_action(LogInfo(msg=EnvironmentVariable('GAZEBO_MODEL_PATH')))

    # ld.add_action(LogInfo(msg=EnvironmentVariable('GAZEBO_MODEL_PATH')))
    ld.add_action(gz_model_uri)
    ld.add_action(LogInfo(msg=EnvironmentVariable('GAZEBO_MODEL_URI')))
    
    ld.add_action(gzserver)
    ld.add_action(gzclient)

    return ld
