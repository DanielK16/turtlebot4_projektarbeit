# Autor: Daniel Körper
# Manuell Steuerung des Roboters 

# Imports für ROS2
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

# Import Interfaces für ROS2 Messages
from geometry_msgs.msg import Twist
from irobot_create_msgs.action import Undock, Dock
from irobot_create_msgs.srv import ResetPose
from slam_toolbox.srv import SaveMap
from std_msgs.msg import String


# Imports für Asyncua
import asyncio
from asyncua import Client, ua
import logging
import os
import time

logging.basicConfig(level=logging.WARNING)

# Laden der Konfigurationsdatei
import yaml
with open("/home/ros/ros2_ws/src/turtlebot4_pkg/config/opc_topic_config.yml","r") as f:
    config = yaml.safe_load(f)
# Environment Variable von docker run übernehmen
config["OPC_Client"]["ipaddress"] = os.environ.get("OPC_IP",config["OPC_Client"]["ipaddress"])

class OPC_UA_Client_Node(Node):

    def __init__(self):
        super().__init__("opc_ua_client_node")

        # Publisher erstellen /cmd_vel
        self.cmd_vel_publisher = self.create_publisher(Twist,"/cmd_vel",10)

        # Aktuelle Sollwerte für /cmd_vel
        self.cmd_vel_freigabe = None
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.man_velocity = 0.0

        # Timer für /cmd_vel (alle 0.01s wird gepublished)
        self.cmd_vel_timer = self.create_timer(0.01,self.cmd_vel_control)

        # Action Client für /undock
        self.undock_action_client = ActionClient(self, Undock, '/undock')	
        self.get_logger().info("Warte auf Action Server /undock")
        self.undock_action_client.wait_for_server()
        self.get_logger().info("Action Server /undock gefunden")

        # Action Client für /dock
        self.dock_action_client = ActionClient(self, Dock, '/dock')	
        self.get_logger().info("Warte auf Action Server /dock")
        self.dock_action_client.wait_for_server()
        self.get_logger().info("Action Server /dock gefunden")

        # Service Client für /reset_pose
        self.reset_pose_client = self.create_client(ResetPose, '/reset_pose')
        self.get_logger().info("Warte auf Service /reset_pose")
        self.reset_pose_client.wait_for_service()
        self.get_logger().info("Service /reset_pose gefunden")

        # Variable für Namen der Map aus Codesys
        self.map_name = "test_map"
        
        # Service Client für /slam_toolbox/save_map Befehl
        self.save_map_client = self.create_client(SaveMap, '/slam_toolbox/save_map')

    def save_map(self):
        """ Speichern der mit SLAM erstellen map """
        if not self.save_map_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Service /slam_toolbox/save_map nicht verfügbar")
            return
            
        req = SaveMap.Request()
        save_path = f"/home/ros/ros2_ws/src/turtlebot4_pkg/maps/{self.map_name}" 
        req.name.data = save_path
        self.save_map_client.call_async(req)
        self.get_logger().info(f"Speichern der Maps: {save_path}")

    def reset_odom_pose(self):
        """Setzt das topic /odom auf den Ursprung zurück """
        req = ResetPose.Request()
        req.pose.position.x = 0.0
        req.pose.position.y = 0.0
        req.pose.position.z = 0.0
        req.pose.orientation.x = 0.0
        req.pose.orientation.y = 0.0
        req.pose.orientation.z = 0.0
        req.pose.orientation.w = 1.0 
        self.reset_pose_client.call_async(req)
        # self.get_logger().info("Service /reset_pose aufgerufen: Odom auf 0 gesetzt.")

    def start_undock(self):
        goal_msg = Undock.Goal()
        self.undock_action_client.send_goal_async(goal_msg)
        # self.get_logger().info("Action /undock aufgerufen: Roboter wird undocked...")

    def start_dock(self):
        goal_msg = Dock.Goal()
        self.dock_action_client.send_goal_async(goal_msg)
        # self.get_logger().info("Action /dock aufgerufen: Roboter wird gedocked...")

    def cmd_vel_control(self):
        """Publiziert die aktuellen Sollwerte kontinuierlich """
        if self.cmd_vel_freigabe:
            msg = Twist()
            msg.linear.x = self.linear_x * self.man_velocity
            msg.angular.z = self.angular_z * self.man_velocity
            self.cmd_vel_publisher.publish(msg)

    def stop_cmd_vel_control(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_vel_publisher.publish(msg)

class SubscriptionHandler:

    def __init__(self, ros_node):
        self.ros_node = ros_node

    def datachange_notification(self, node, val, data):
        """Aktualisiert Sollwerte bei OPC-UA-Wertänderungen"""
        print(f"datachange_notification {node} = {val}")
        
        # Vegleicht Wertänderung und übergit aktuellen Wert an die ROS Node
        if str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.cmd_vel.linear.x":
            if val is not None:
                self.ros_node.linear_x = val
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.cmd_vel.angular.z":
            if val is not None:
                self.ros_node.angular_z = val
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.man_velocity":
            if val is not None:
                self.ros_node.man_velocity = val
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.cmd_vel_freigabe":
            if val is not None:
                self.ros_node.cmd_vel_freigabe = bool(val)
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_dock":
            if val:
                self.ros_node.start_dock()
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_undock":
            if val:
                self.ros_node.start_undock()
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_reset_odom":
            if val:
                self.ros_node.reset_odom_pose()
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.name_map":
            if val is not None:
                self.ros_node.map_name = str(val)
        elif str(node) == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_save_map":
            if val:
                self.ros_node.save_map()
        else:
            return

async def async_main(args=None):
    # Instanziieren der ROS2 Node Klasse
    ros_node = OPC_UA_Client_Node()

    # OPC-UA-Verbindung herstellen
    ipaddress = config["OPC_Client"]["ipaddress"]
    port = config["OPC_Client"]["port"]
    opc_url = f"opc.tcp://{ipaddress}:{port}"

    try:
        async with Client(
                        url=opc_url,
                        timeout=2.0,
                        watchdog_intervall=0.5,
                        auto_reconnect=True,
                        reconnect_max_delay=5.0,
                        reconnect_request_timeout=5.0
                    ) as client:
            ros_node.get_logger().info(f"OPC Client verbunden: {opc_url}")

            # Verbindung zu den OPC-UA-Knoten herstellen
            cmd_vel_node = {
                "linear_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.cmd_vel.linear.x"),
                "angular_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.cmd_vel.angular.z"),
                "man_velocity": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.man_velocity"),
                "cmd_vel_freigabe": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.cmd_vel_freigabe"),
            }

            action_node = {
                "request_dock": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_dock"),
                "request_undock": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_undock"),
            }

            service_node = {
                "request_reset_odom": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_reset_odom"),
                "map_name": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.name_map"), 
                "request_save_map": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.request_save_map") 
            }

            watchdog_node = client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.command.watchdog_counter")
            watchdog_counter = 0

            # Subscription Handler
            handler = SubscriptionHandler(ros_node)
            subscription = await client.create_subscription(100,handler)
            await subscription.subscribe_data_change([
                cmd_vel_node["linear_x"],
                cmd_vel_node["angular_z"],
                cmd_vel_node["man_velocity"],
                cmd_vel_node["cmd_vel_freigabe"],
                action_node["request_dock"],
                action_node["request_undock"],
                service_node["request_reset_odom"],
                service_node["map_name"],
                service_node["request_save_map"]
                ])

            # Hauptschleife:
            while rclpy.ok():
                rclpy.spin_once(ros_node,timeout_sec=0.0)

                # Watchdog Variable erhöhen und schreiben
                try:
                    watchdog_counter = (watchdog_counter +1) % 32767
                    await watchdog_node.set_value(int(watchdog_counter), ua.VariantType.Int16)
                except Exception as e:
                    ros_node.get_logger().warn(f"Watchdog konnte nicht gesendet werden: {e}")

                await asyncio.sleep(0.01)

    except Exception as e:
        ros_node.get_logger().error(f"OPC-UA-Fehler: {e}")
    finally:
        if rclpy.ok():
            # Beim Beenden des Programms sichergehen dass Roboter gestoppt ist!
            ros_node.get_logger().info("Sende Stopp-Signal an Roboter...")
            ros_node.stop_cmd_vel_control()
            time.sleep(0.1)
            ros_node.destroy_node()


def main(args=None):

    rclpy.init(args=args)
    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print("Strg + C gedrückt: Programm wird beendet.")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()
