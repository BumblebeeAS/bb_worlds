#!/usr/bin/env python3
import rclpy
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rclpy.node import Node
from tf_transformations import quaternion_from_euler
from visualization_msgs.msg import Marker


class MeshMarkerPublisher(Node):
    def __init__(self):
        super().__init__("mesh_marker_publisher")

        self.mesh_resource = (
            self.declare_parameter(
                "mesh_resource",
                descriptor=ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
            )
            .get_parameter_value()
            .string_value
        )
        self.frame_id = (
            self.declare_parameter(
                "frame_id",
                descriptor=ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
            )
            .get_parameter_value()
            .string_value
        )
        output_marker_topic = (
            self.declare_parameter("output_marker_topic", "marker")
            .get_parameter_value()
            .string_value
        )
        self.mesh_roll_pitch_yaw = (
            self.declare_parameter(
                "mesh_roll_pitch_yaw",
                [0.0, 0.0, 0.0],
                descriptor=ParameterDescriptor(
                    type=ParameterType.PARAMETER_DOUBLE_ARRAY
                ),
            )
            .get_parameter_value()
            .double_array_value
        )

        self.publisher_ = self.create_publisher(Marker, output_marker_topic, 10)

        # Publish marker every 50ms
        self.timer_ = self.create_timer(0.05, self.publish_marker)

        self.get_logger().info("Mesh marker publisher node started")

    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = self.frame_id
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "my_mesh"
        marker.id = 0
        marker.type = Marker.MESH_RESOURCE
        marker.action = Marker.ADD

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0

        orientation = self.mesh_roll_pitch_yaw
        qx, qy, qz, qw = quaternion_from_euler(
            orientation[0], orientation[1], orientation[2]
        )
        marker.pose.orientation.x = qx
        marker.pose.orientation.y = qy
        marker.pose.orientation.z = qz
        marker.pose.orientation.w = qw

        marker.scale.x = 1.0
        marker.scale.y = 1.0
        marker.scale.z = 1.0

        marker.color.a = 1.0
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0

        # Specify the path to your mesh file
        marker.mesh_resource = self.mesh_resource
        marker.mesh_use_embedded_materials = True

        self.publisher_.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = MeshMarkerPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
