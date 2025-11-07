#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker


class MeshMarkerPublisher(Node):
    def __init__(self):
        super().__init__("mesh_marker_publisher")

        self.publisher_ = self.create_publisher(Marker, "visualization_marker", 10)

        # Publish marker every 50ms
        self.timer_ = self.create_timer(0.05, self.publish_marker)

        self.get_logger().info("Mesh marker publisher node started")

    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = "aruco_board"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "my_mesh"
        marker.id = 0
        marker.type = Marker.MESH_RESOURCE
        marker.action = Marker.ADD

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0

        marker.scale.x = 1.0
        marker.scale.y = 1.0
        marker.scale.z = 1.0

        marker.color.a = 1.0
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0

        # Specify the path to your mesh file
        marker.mesh_resource = (
            "package://bb_worlds/models/robotx24/arucotag_v3/model.dae"
        )
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
