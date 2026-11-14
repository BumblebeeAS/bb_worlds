import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

NODE_NAMESPACES = ["aruco", "helipad"]


def launch_markers(context):
    base_url = LaunchConfiguration("asset_base_url").perform(context).rstrip("/")
    mesh_paths = {
        "aruco": "bb_worlds/models/robotx24/arucotag_v3/model.dae",
        "helipad": "bb_worlds/models/robotx24/helipad/helipad.glb",
    }
    config = os.path.join(
        get_package_share_directory("bb_worlds"),
        "config",
        "uav.launch.yaml",
    )

    launch_objects = [PushRosNamespace("/uav")]

    nodes = [
        Node(
            name="vis_marker_publisher_node",
            package="bb_worlds",
            executable="vis_marker_publisher_node.py",
            parameters=[config] + (
                [{"mesh_resource": f"{base_url}/{mesh_paths[node_namespace]}"}]
                if base_url else []
            ),
            namespace=node_namespace,
        )
        for node_namespace in NODE_NAMESPACES
    ]

    return launch_objects + nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "asset_base_url", default_value="",
            description="HTTPS mesh/texture host; empty uses local package resources",
        ),
        OpaqueFunction(function=launch_markers),
    ])
