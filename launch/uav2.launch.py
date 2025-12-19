import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node, PushRosNamespace

NODE_NAMESPACES = ["aruco", "helipad"]


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory("bb_worlds"),
        "config",
        "uav2.launch.yaml",
    )

    launch_objects = [PushRosNamespace("/uav2")]

    nodes = [
        Node(
            name="vis_marker_publisher_node",
            package="bb_worlds",
            executable="vis_marker_publisher_node.py",
            parameters=[config],
            namespace=node_namespace,
        )
        for node_namespace in NODE_NAMESPACES
    ]

    return LaunchDescription(launch_objects + nodes)
