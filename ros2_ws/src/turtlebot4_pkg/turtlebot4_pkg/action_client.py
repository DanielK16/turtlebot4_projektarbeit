# Autor: Daniel Körper
# Steuerung des Roboters über eine Schrittkette in CODESYS

# Imports für ROS2
import rclpy
from rclpy.node import Node

# Import Interfaces für ROS2 Messages
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped

from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Navigator, TaskResult

# Imports für Asyncua
import asyncio
from asyncua import Client, ua
import logging
import os
logging.basicConfig(level=logging.WARNING)

# Laden der Konfigurationsdatei
import yaml
with open("/home/ros/ros2_ws/src/turtlebot4_pkg/config/opc_topic_config.yml", "r") as f:
    config = yaml.safe_load(f)

# Environment Variable von docker run übernehmen
config["OPC_Client"]["ipaddress"] = os.environ.get("OPC_IP", config["OPC_Client"]["ipaddress"])


class OPC_UA_Client_Node(Node):
    def __init__(self):
        super().__init__("opc_ua_client_node")

        self.navigator = TurtleBot4Navigator()

        # Publisher zu /initialpose erstellen
        self.initialpose_pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        
        # Initialposition Variablen 
        self.initialpose_trans_x = 0.0
        self.initialpose_trans_y = 0.0
        self.initialpose_trans_z = 0.0
        self.initialpose_orient_x = 0.0
        self.initialpose_orient_y = 0.0
        self.initialpose_orient_z = 0.0
        self.initialpose_orient_w = 1.0

        # Zielposition Variablen 
        self.goalpose_trans_x = 0.0
        self.goalpose_trans_y = 0.0
        self.goalpose_trans_z = 0.0
        self.goalpose_orient_x = 0.0
        self.goalpose_orient_y = 0.0
        self.goalpose_orient_z = 0.0
        self.goalpose_orient_w = 1.0

        # Status-Code & Timer für Navigation:
        # 0 = Läuft, 1 = Erfolg, 2 = Canceled, 3 = Failed, 99 = Unbekannt
        self.nav_status_code = None
        self.nav_check_timer = None

    def set_initialpose(self):
        """ Ersetzt 2D Estimate in RViz2 """ 
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        
        msg.pose.pose.position.x = float(self.initialpose_trans_x)
        msg.pose.pose.position.y = float(self.initialpose_trans_y)
        msg.pose.pose.position.z = float(self.initialpose_trans_z)
        msg.pose.pose.orientation.x = float(self.initialpose_orient_x)
        msg.pose.pose.orientation.y = float(self.initialpose_orient_y)
        msg.pose.pose.orientation.z = float(self.initialpose_orient_z)
        msg.pose.pose.orientation.w = float(self.initialpose_orient_w)
        
        self.initialpose_pub.publish(msg)
        self.get_logger().info(f"Initialpose gesetzt - Pos: [{msg.pose.pose.position.x:.2f}, {msg.pose.pose.position.y:.2f}, {msg.pose.pose.position.z:.2f}] | Ori(xyzw): [{msg.pose.pose.orientation.x:.2f}, {msg.pose.pose.orientation.y:.2f}, {msg.pose.pose.orientation.z:.2f}, {msg.pose.pose.orientation.w:.2f}]")

    def move_to_goal(self):
        """ Navigiert TB4 an die vorgegebene Zielposition """
        # Warten bis Nav2 bereit ist
        self.navigator.waitUntilNav2Active()
    
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_pose.pose.position.x = float(self.goalpose_trans_x)
        goal_pose.pose.position.y = float(self.goalpose_trans_y)
        goal_pose.pose.position.z = float(self.goalpose_trans_z)
        goal_pose.pose.orientation.x = float(self.goalpose_orient_x)
        goal_pose.pose.orientation.y = float(self.goalpose_orient_y)
        goal_pose.pose.orientation.z = float(self.goalpose_orient_z)
        goal_pose.pose.orientation.w = float(self.goalpose_orient_w)

        # Status auf 0 (Fahrt läuft) setzen
        self.nav_status_code = 0

        # Fahrbefehl absenden
        self.navigator.startToPose(goal_pose)
        self.get_logger().info(f"Fahrbefehl an Nav2 gesendet: Ziel [{goal_pose.pose.position.x:.2f}, {goal_pose.pose.position.y:.2f}]")
        
        # Überwachungstimer (alle 0.2 Sekunden) starten
        if self.nav_check_timer is not None:
            self.nav_check_timer.cancel()
        self.nav_check_timer = self.create_timer(0.2, self.check_nav_status)

    def check_nav_status(self):
        """ Prüft periodisch den Task-Status von Nav2 und ordnet Fehlercodes zu """
        if self.navigator.isTaskComplete():
            result = self.navigator.getResult()
            
            if result == TaskResult.SUCCEEDED:
                self.get_logger().info("Nav2 [Code 1]: Zielposition erfolgreich erreicht!")
                self.nav_status_code = 1
                
            elif result == TaskResult.CANCELED:
                self.get_logger().warn("Nav2 Fehler [Code 2]: Navigation wurde abgebrochen.")
                self.nav_status_code = 2
                
            elif result == TaskResult.FAILED:
                self.get_logger().error("Nav2 Fehler [Code 3]: Navigation fehlgeschlagen (Pfad blockiert oder Ziel unerreichbar).")
                self.nav_status_code = 3
                
            else:
                self.get_logger().error(f"Nav2 Fehler [Code 99]: Unbekannter Status-Code ({result}).")
                self.nav_status_code = 99
                
            # Timer stoppen nach Beendigung der Fahrt
            if self.nav_check_timer is not None:
                self.nav_check_timer.cancel()
                self.nav_check_timer = None


class SubscriptionHandler:
    def __init__(self, ros_node):
        self.ros_node = ros_node

    async def datachange_notification(self, node, val, data):
        """Aktualisiert Sollwerte bei OPC-UA-Wertänderungen"""
        print(f"datachange_notification {node} = {val}")
        
        node_str = str(node)

        # --- INITIAL POSE ---
        if node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.position.x":
            if val is not None: self.ros_node.initialpose_trans_x = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.position.y":
            if val is not None: self.ros_node.initialpose_trans_y = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.position.z":
            if val is not None: self.ros_node.initialpose_trans_z = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.x":
            if val is not None: self.ros_node.initialpose_orient_x = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.y":
            if val is not None: self.ros_node.initialpose_orient_y = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.z":
            if val is not None: self.ros_node.initialpose_orient_z = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.w":
            if val is not None: self.ros_node.initialpose_orient_w = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.request_set_inital_position":
            if val: 
                self.ros_node.set_initialpose()

        # --- GOAL POSE ---
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.position.x":
            if val is not None: self.ros_node.goalpose_trans_x = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.position.y":
            if val is not None: self.ros_node.goalpose_trans_y = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.position.z":
            if val is not None: self.ros_node.goalpose_trans_z = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.x":
            if val is not None: self.ros_node.goalpose_orient_x = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.y":
            if val is not None: self.ros_node.goalpose_orient_y = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.z":
            if val is not None: self.ros_node.goalpose_orient_z = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.w":
            if val is not None: self.ros_node.goalpose_orient_w = val
        elif node_str == "ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.request_move_to_goal":
            if val: 
                # Kurze Pause (50ms) zur Synchronisierung eintreffender Koordinaten
                await asyncio.sleep(0.05)
                self.ros_node.move_to_goal()


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

            # Statuscode-Variable zum Beschreiben abrufen
            status_code_node = client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_status_code")

            # Verbindung zu den OPC-UA-Knoten herstellen
            initialpose_node = {
                "trans_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.position.x"),
                "trans_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.position.y"),
                "trans_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.position.z"),
                "orient_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.x"),
                "orient_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.y"),
                "orient_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.z"),
                "orient_w": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.initial_pose.orientation.w"),
                "request_set": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.request_set_inital_position")
            }

            goalpose_node = {
                "trans_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.position.x"),
                "trans_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.position.y"),
                "trans_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.position.z"),
                "orient_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.x"),
                "orient_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.y"),
                "orient_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.z"),
                "orient_w": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.goal_pose.orientation.w"),
                "request_move": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.navigation.request_move_to_goal")
            }

            # Subscription Handler
            handler = SubscriptionHandler(ros_node)
            subscription = await client.create_subscription(100, handler)
            await subscription.subscribe_data_change([
                initialpose_node["trans_x"], initialpose_node["trans_y"], initialpose_node["trans_z"],
                initialpose_node["orient_x"], initialpose_node["orient_y"], initialpose_node["orient_z"], initialpose_node["orient_w"],
                initialpose_node["request_set"],
                goalpose_node["trans_x"], goalpose_node["trans_y"], goalpose_node["trans_z"],
                goalpose_node["orient_x"], goalpose_node["orient_y"], goalpose_node["orient_z"], goalpose_node["orient_w"],
                goalpose_node["request_move"]
            ])

            # Hauptschleife:
            while rclpy.ok():
                rclpy.spin_once(ros_node, timeout_sec=0.0)
                
                # neuen Statuscode anlegen
                if ros_node.nav_status_code is not None:
                    await status_code_node.write_value(
                        ua.DataValue(ua.Variant(int(ros_node.nav_status_code), ua.VariantType.Int16))
                    )
                    ros_node.get_logger().info(f"Statuscode '{ros_node.nav_status_code}' an CODESYS übertragen.")
                    ros_node.nav_status_code = None
                
                await asyncio.sleep(0.01)

    except Exception as e:
        ros_node.get_logger().error(f"OPC-UA-Fehler: {e}")
    finally:
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