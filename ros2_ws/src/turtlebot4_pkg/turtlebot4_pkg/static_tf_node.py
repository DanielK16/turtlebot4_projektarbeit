# Autor: Daniel Koerper
# Veröffentlicht die statischen Transformationen von LiDAR, Kamera, IMU und Bumper
# lokal im Container auf /tf_static.

# Problem: Vor Start von Nav2, Lokalisierung, SLAM oder RViz2 statische Transf. vorhanden.
# Nach Start fehlen diese Transformationen!
# Neuveröffentlichung bei Start über entrypoint.py!
# manuell starten mit ros2 run turtlebot4_pkg static_tf_node

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

class StaticTfNode(Node):
    def __init__(self):
        super().__init__("static_tf_node")
        self.broadcaster = StaticTransformBroadcaster(self)
        now = self.get_clock().now().to_msg()

        # LiDAR Sensor
        tf_rplidar = TransformStamped()
        tf_rplidar.header.stamp = now
        tf_rplidar.header.frame_id = "base_link"
        tf_rplidar.child_frame_id = "rplidar_link"
        tf_rplidar.transform.translation.x = 0.00393584
        tf_rplidar.transform.translation.y = 0.0
        tf_rplidar.transform.translation.z = 0.13949272
        tf_rplidar.transform.rotation.x = 0.0
        tf_rplidar.transform.rotation.y = 0.0
        tf_rplidar.transform.rotation.z = 0.7071067811865475
        tf_rplidar.transform.rotation.w = 0.7071067811865476

        # Kamera
        tf_oakd_bracket = TransformStamped()
        tf_oakd_bracket.header.stamp = now
        tf_oakd_bracket.header.frame_id = "base_link"
        tf_oakd_bracket.child_frame_id = "oakd_camera_bracket"
        tf_oakd_bracket.transform.translation.x = -0.09
        tf_oakd_bracket.transform.translation.y = 0.0
        tf_oakd_bracket.transform.translation.z = 0.09334772
        tf_oakd_bracket.transform.rotation.x = 0.0
        tf_oakd_bracket.transform.rotation.y = 0.0
        tf_oakd_bracket.transform.rotation.z = 0.0
        tf_oakd_bracket.transform.rotation.w = 1.0

        tf_oakd_link = TransformStamped()
        tf_oakd_link.header.stamp = now
        tf_oakd_link.header.frame_id = "oakd_camera_bracket"
        tf_oakd_link.child_frame_id = "oakd_link"
        tf_oakd_link.transform.translation.x = 0.05294026
        tf_oakd_link.transform.translation.y = 0.0
        tf_oakd_link.transform.translation.z = 0.0925385
        tf_oakd_link.transform.rotation.x = 0.0
        tf_oakd_link.transform.rotation.y = 0.0
        tf_oakd_link.transform.rotation.z = 0.0
        tf_oakd_link.transform.rotation.w = 1.0

        tf_oakd_imu = TransformStamped()
        tf_oakd_imu.header.stamp = now
        tf_oakd_imu.header.frame_id = "oakd_link"
        tf_oakd_imu.child_frame_id = "oakd_imu_frame"
        tf_oakd_imu.transform.translation.x = 0.0
        tf_oakd_imu.transform.translation.y = 0.0
        tf_oakd_imu.transform.translation.z = 0.0
        tf_oakd_imu.transform.rotation.x = 0.5
        tf_oakd_imu.transform.rotation.y = -0.5
        tf_oakd_imu.transform.rotation.z = 0.5
        tf_oakd_imu.transform.rotation.w = -0.5

        tf_oakd_rgb = TransformStamped()
        tf_oakd_rgb.header.stamp = now
        tf_oakd_rgb.header.frame_id = "oakd_link"
        tf_oakd_rgb.child_frame_id = "oakd_rgb_camera_frame"
        tf_oakd_rgb.transform.translation.x = 0.0
        tf_oakd_rgb.transform.translation.y = 0.0
        tf_oakd_rgb.transform.translation.z = 0.0
        tf_oakd_rgb.transform.rotation.x = 0.0
        tf_oakd_rgb.transform.rotation.y = 0.0
        tf_oakd_rgb.transform.rotation.z = 0.0
        tf_oakd_rgb.transform.rotation.w = 1.0

        tf_oakd_rgb_optical = TransformStamped()
        tf_oakd_rgb_optical.header.stamp = now
        tf_oakd_rgb_optical.header.frame_id = "oakd_rgb_camera_frame"
        tf_oakd_rgb_optical.child_frame_id = "oakd_rgb_camera_optical_frame"
        tf_oakd_rgb_optical.transform.translation.x = 0.0
        tf_oakd_rgb_optical.transform.translation.y = 0.0
        tf_oakd_rgb_optical.transform.translation.z = 0.0
        tf_oakd_rgb_optical.transform.rotation.x = 0.5
        tf_oakd_rgb_optical.transform.rotation.y = -0.5
        tf_oakd_rgb_optical.transform.rotation.z = 0.5
        tf_oakd_rgb_optical.transform.rotation.w = -0.5

        tf_oakd_left = TransformStamped()
        tf_oakd_left.header.stamp = now
        tf_oakd_left.header.frame_id = "oakd_link"
        tf_oakd_left.child_frame_id = "oakd_left_camera_frame"
        tf_oakd_left.transform.translation.x = 0.0
        tf_oakd_left.transform.translation.y = 0.0375
        tf_oakd_left.transform.translation.z = 0.0
        tf_oakd_left.transform.rotation.x = 0.0
        tf_oakd_left.transform.rotation.y = 0.0
        tf_oakd_left.transform.rotation.z = 0.0
        tf_oakd_left.transform.rotation.w = 1.0

        tf_oakd_left_optical = TransformStamped()
        tf_oakd_left_optical.header.stamp = now
        tf_oakd_left_optical.header.frame_id = "oakd_left_camera_frame"
        tf_oakd_left_optical.child_frame_id = "oakd_left_camera_optical_frame"
        tf_oakd_left_optical.transform.translation.x = 0.0
        tf_oakd_left_optical.transform.translation.y = 0.0
        tf_oakd_left_optical.transform.translation.z = 0.0
        tf_oakd_left_optical.transform.rotation.x = 0.5
        tf_oakd_left_optical.transform.rotation.y = -0.5
        tf_oakd_left_optical.transform.rotation.z = 0.5
        tf_oakd_left_optical.transform.rotation.w = -0.5

        tf_oakd_right = TransformStamped()
        tf_oakd_right.header.stamp = now
        tf_oakd_right.header.frame_id = "oakd_link"
        tf_oakd_right.child_frame_id = "oakd_right_camera_frame"
        tf_oakd_right.transform.translation.x = 0.0
        tf_oakd_right.transform.translation.y = -0.0375
        tf_oakd_right.transform.translation.z = 0.0
        tf_oakd_right.transform.rotation.x = 0.0
        tf_oakd_right.transform.rotation.y = 0.0
        tf_oakd_right.transform.rotation.z = 0.0
        tf_oakd_right.transform.rotation.w = 1.0

        tf_oakd_right_optical = TransformStamped()
        tf_oakd_right_optical.header.stamp = now
        tf_oakd_right_optical.header.frame_id = "oakd_right_camera_frame"
        tf_oakd_right_optical.child_frame_id = "oakd_right_camera_optical_frame"
        tf_oakd_right_optical.transform.translation.x = 0.0
        tf_oakd_right_optical.transform.translation.y = 0.0
        tf_oakd_right_optical.transform.translation.z = 0.0
        tf_oakd_right_optical.transform.rotation.x = 0.5
        tf_oakd_right_optical.transform.rotation.y = -0.5
        tf_oakd_right_optical.transform.rotation.z = 0.5
        tf_oakd_right_optical.transform.rotation.w = -0.5

        # IMU 
        tf_imu_link = TransformStamped()
        tf_imu_link.header.stamp = now
        tf_imu_link.header.frame_id = "base_link"
        tf_imu_link.child_frame_id = "imu_link"
        tf_imu_link.transform.translation.x = 0.050613
        tf_imu_link.transform.translation.y = 0.043673
        tf_imu_link.transform.translation.z = 0.0844
        tf_imu_link.transform.rotation.x = 0.0
        tf_imu_link.transform.rotation.y = 0.0
        tf_imu_link.transform.rotation.z = 0.0
        tf_imu_link.transform.rotation.w = 1.0

        tf_imu = TransformStamped()
        tf_imu.header.stamp = now
        tf_imu.header.frame_id = "base_link"
        tf_imu.child_frame_id = "imu"
        tf_imu.transform.translation.x = 0.051
        tf_imu.transform.translation.y = 0.035
        tf_imu.transform.translation.z = 0.0685
        tf_imu.transform.rotation.x = 0.0
        tf_imu.transform.rotation.y = 0.0
        tf_imu.transform.rotation.z = 0.0
        tf_imu.transform.rotation.w = 1.0

        # Bumper 
        tf_bumper = TransformStamped()
        tf_bumper.header.stamp = now
        tf_bumper.header.frame_id = "base_link"
        tf_bumper.child_frame_id = "bumper"
        tf_bumper.transform.translation.x = 0.0
        tf_bumper.transform.translation.y = 0.0
        tf_bumper.transform.translation.z = 0.0392
        tf_bumper.transform.rotation.x = 0.0
        tf_bumper.transform.rotation.y = 0.0
        tf_bumper.transform.rotation.z = 0.0
        tf_bumper.transform.rotation.w = 1.0

        transforms = [
            tf_rplidar,
            tf_oakd_bracket,
            tf_oakd_link,
            tf_oakd_imu,
            tf_oakd_rgb,
            tf_oakd_rgb_optical,
            tf_oakd_left,
            tf_oakd_left_optical,
            tf_oakd_right,
            tf_oakd_right_optical,
            tf_imu_link,
            tf_imu,
            tf_bumper,
        ]
        self.broadcaster.sendTransform(transforms)
        self.get_logger().info(f"{len(transforms)} statische Transformationen veroeffentlicht.")

def main(args=None):
    rclpy.init(args=args)
    node = StaticTfNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
