# Copyright 2021 Open Source Robotics Foundation, Inc.
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


from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python import get_package_share_directory

import robotx_gz.launch
from robotx_gz.model import Model


def launch(context, *args, **kwargs):
    config_file = LaunchConfiguration('config_file').perform(context)
    world_name = LaunchConfiguration('world').perform(context)
    sim_mode = LaunchConfiguration('sim_mode').perform(context)
    bridge_competition_topics = LaunchConfiguration(
        'bridge_competition_topics').perform(context).lower() == 'true'
    # quadcopter = LaunchConfiguration('quadcopter').perform(context)
    headless = LaunchConfiguration('headless')\
        .perform(context).lower() == 'true'
    wamv_name = LaunchConfiguration('wamv_name').perform(context)
    wamv_xacro = LaunchConfiguration('wamv_xacro').perform(context)
    gz_paused = LaunchConfiguration('paused')\
        .perform(context).lower() == 'true'
    competition_mode = LaunchConfiguration('competition_mode')\
        .perform(context).lower() == 'true'
    extra_gz_args = LaunchConfiguration('extra_gz_args').perform(context)

    launch_processes = []

    models = []
    xacro_file = wamv_xacro
    if xacro_file == '':
        xacro_file = os.path.join(
                get_package_share_directory('bbauv_gazebo_plugins'),
                "robots/auv4.xacro")
    
    if config_file and config_file != '':
        with open(config_file, 'r', encoding='utf-8') as stream:
            models = Model.FromConfig(stream)
            if models is not list:
                models = [models]
    else:
        if world_name == 'rsyc':
            m = Model(wamv_name, 'wam-v', [167.67, -41.84, 0, 0, 0, 2.61799388])
        elif world_name == "sauvc":
            m = Model(wamv_name, 'auv4', [0, 0, 0, 0, 0, 2.61799388])
        elif world_name == "robosub_2023_pool":
            m = Model(wamv_name, 'auv4', [0, 0, 0, 0, 0, 2.61799388])
        else:
            m = Model(wamv_name, 'wam-v', [-168, 829, 0, 0, 0, 1])
        if xacro_file and xacro_file != '':
            m.set_urdf(xacro_file)
            m.generate()
            print("Generated model", m)
            models.append(m)

    world_name, _ = os.path.splitext(world_name)
    launch_processes.extend(robotx_gz.launch.simulation(
        world_name, headless, gz_paused, extra_gz_args))
    world_name_base = os.path.basename(world_name)
    print(world_name_base, xacro_file, sim_mode)

    print(f"Spawing {wamv_name} in {world_name_base} {models}, {xacro_file} {sim_mode}")
    if xacro_file != "" and sim_mode != 'world':
        launch_processes.extend(robotx_gz.launch.spawn(
            sim_mode, world_name_base, models, wamv_name))
        if (sim_mode == 'bridge' or sim_mode == 'full')\
                and bridge_competition_topics:
            launch_processes.extend(robotx_gz.launch.competition_bridges(
                world_name_base, competition_mode))

    return launch_processes


def generate_launch_description():
    return LaunchDescription([
        # Launch Arguments
        DeclareLaunchArgument(
            'world',
            default_value='sauvc',
            description='Name of world (sydney_regatta / nbpark)'),
        DeclareLaunchArgument(
            'sim_mode',
            default_value='world',
            description='Simulation mode: "full", "sim", "bridge", "world".'
                        'full: spawns robot and launch ros_gz bridges, '
                        'sim: spawns robot only, '
                        'bridge: launch ros_gz bridges only,'
                        'world: spawn world only'),
        DeclareLaunchArgument(
            'bridge_competition_topics',
            default_value='True',
            description='True to bridge competition topics, False to disable bridge.'),
        DeclareLaunchArgument(
            'config_file',
            default_value='',
            description='YAML configuration file to spawn'),
        DeclareLaunchArgument(
            'wamv_name',
            default_value='auv4',
            description='Name of wamv to spawn if specified. '
                        'This must match one of the robots in the config_file'),
        DeclareLaunchArgument(
            'headless',
            default_value='False',
            description='True to run simulation headless (no GUI). '),
        DeclareLaunchArgument(
            'wamv_xacro',
            default_value='',
            description='URDF file of the wam-v model. '),
        DeclareLaunchArgument(
            'paused',
            default_value='True',
            description='True to start the simulation paused. '),
        DeclareLaunchArgument(
            'competition_mode',
            default_value='False',
            description='True to disable debug topics. '),
        DeclareLaunchArgument(
            'extra_gz_args',
            default_value='',
            description='Additional arguments to be passed to gz sim. '),
        OpaqueFunction(function=launch),
    ])
