# Autor: Daniel Körper

# Imports
import rclpy
from rclpy.node import Node
import os

# Import Interfaces für ROS2 Messages
from irobot_create_msgs.msg import DockStatus, WheelVels
from sensor_msgs.msg import Imu, BatteryState
from std_msgs.msg import String
# Import QoS Default Settings
from rclpy.qos import qos_profile_system_default, qos_profile_sensor_data


# Imports für Asyncua
import asyncio
from asyncua import Client, ua
import logging
logging.basicConfig(level=logging.WARNING) # reduziert Fehlermeldungen von asyncua  

# Laden der Konfigurations Datei
import yaml
with open("/home/ros/ros2_ws/src/turtlebot4_pkg/config/opc_topic_config.yml", "r") as f:
    config = yaml.safe_load(f)
    # Environment Variable von docker run übergebn
config['OPC_Client']['ipaddress'] = os.environ.get('OPC_IP', config['OPC_Client']['ipaddress'])

class OPC_UA_Client_Node(Node):
    def __init__(self):
        super().__init__('opc_ua_client_node')
        
        # Variablen festlegen
        # /dock_status
        self.dock_visible = None
        self.is_docked = None
        # /wheel_vels
        self.velocity_left = None
        self.velocity_right = None
        # /imu
        self.orientation = None
        self.angular_velocity = None
        self.linear_acceleration = None
        # ip
        self.ip = None
        #batterystate
        self.voltage = None
        self.temperature = None
        self.percentage = None

        # Subscriber für /dock_status
        self.dock_status_sub = self.create_subscription(
            DockStatus,
            '/dock_status',
            self.dock_status_callback,
            qos_profile_sensor_data)

        # Subscriber für /wheel_vels
        self.wheel_vels_sub = self.create_subscription(
            WheelVels,
            '/wheel_vels',
            self.wheel_vels_callback,
            qos_profile_sensor_data)

        # Subscriber für /imu
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu',
            self.imu_callback,
            qos_profile_sensor_data)

        # Subscriber für /ip
        self.ip_sub = self.create_subscription(
            String, 
            '/ip',
            self.ip_callback,
            qos_profile_system_default
        )

        # Subscriber für /battery_state
        self.battery_state_sub = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_state_callback,
            qos_profile_sensor_data
        )

        

    # Verarbeiten von Subscribern erhaltenen Daten    
    def dock_status_callback(self, msg):
        self.dock_visible = msg.dock_visible
        self.is_docked = msg.is_docked

    def wheel_vels_callback(self,msg):
        self.velocity_left = msg.velocity_left
        self.velocity_right = msg.velocity_right

    def imu_callback(self,msg):
        self.orientation = msg.orientation
        self.angular_velocity = msg.angular_velocity
        self.linear_acceleration = msg.linear_acceleration

    def ip_callback(self,msg):
        self.ip = msg.data

    def battery_state_callback(self,msg):
        self.voltage = msg.voltage
        self.temperature = msg.temperature
        self.percentage = msg.percentage

async def async_main(args=None):
    # Instanzziieren der ROS2 Node Klasse
    ros_node = OPC_UA_Client_Node()
    
    # OPC UA Verbindung
    ipaddress = config['OPC_Client']['ipaddress']
    port = config['OPC_Client']['port']
    opc_url = f"opc.tcp://{ipaddress}:{port}"

    async with Client(url = opc_url,
                      timeout = 2.0,
                      watchdog_intervall = 0.5, 
                      auto_reconnect = True,  
                      reconnect_max_delay = 5.0,    
                      reconnect_request_timeout = 5.0, ) as client:
        ros_node.get_logger().info(f"OPC Client verbunden: {opc_url}")

        # Verbindung zu Knoten im OPC-UA Server herstelle
        dock_status_node = {
            "is_docked": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.dock_status.is_docked"),
            "dock_visible": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.dock_status.dock_visible")
        }

        wheel_vels_node = {
            "velocity_left": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.wheel_vels.velocity_left"),
            "velocity_right": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.wheel_vels.velocity_right")
        }

        imu_node = {
            "orientation_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.orientation.x"),
            "orientation_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.orientation.y"),
            "orientation_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.orientation.z"),
            "orientation_w": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.orientation.w"),

            "angular_velocity_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.angular_velocity.x"),
            "angular_velocity_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.angular_velocity.y"),
            "angular_velocity_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.angular_velocity.z"),

            "linear_acceleration_x": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.linear_acceleration.x"),
            "linear_acceleration_y": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.linear_acceleration.y"),
            "linear_acceleration_z": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.imu.linear_acceleration.z"),
        }

        ip_node = client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.ip.ip")

        battery_state_node = {
            "voltage": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.battery_state.voltage"),
            "temperature": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.battery_state.temperature"),
            "percentage": client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.status.battery_state.percentage"),
        }

        try:
            # Hauptschleife
            while rclpy.ok():
                
                # ROS2 Callbacks verarbeiten -> ließt neue msg für Subscriber ein
                rclpy.spin_once(ros_node, timeout_sec=0.0)
                
                if ros_node.is_docked is not None:
                    await dock_status_node["is_docked"].set_value(bool(ros_node.is_docked), ua.VariantType.Boolean)
                if ros_node.dock_visible is not None:
                    await dock_status_node["dock_visible"].set_value(bool(ros_node.dock_visible), ua.VariantType.Boolean)
                
                if ros_node.velocity_left is not None:
                    await wheel_vels_node["velocity_left"].set_value(float(ros_node.velocity_left), ua.VariantType.Float)
                if ros_node.velocity_right is not None:
                    await wheel_vels_node["velocity_right"].set_value(float(ros_node.velocity_right), ua.VariantType.Float)    

                if ros_node.orientation is not None:
                    await imu_node["orientation_x"].set_value(float(ros_node.orientation.x), ua.VariantType.Double)
                    await imu_node["orientation_y"].set_value(float(ros_node.orientation.y), ua.VariantType.Double)
                    await imu_node["orientation_z"].set_value(float(ros_node.orientation.z), ua.VariantType.Double)
                    await imu_node["orientation_w"].set_value(float(ros_node.orientation.w), ua.VariantType.Double)

                if ros_node.angular_velocity is not None:
                    await imu_node["angular_velocity_x"].set_value(float(ros_node.angular_velocity.x), ua.VariantType.Double)
                    await imu_node["angular_velocity_y"].set_value(float(ros_node.angular_velocity.y), ua.VariantType.Double)
                    await imu_node["angular_velocity_z"].set_value(float(ros_node.angular_velocity.z), ua.VariantType.Double)

                if ros_node.linear_acceleration is not None:
                    await imu_node["linear_acceleration_x"].set_value(float(ros_node.linear_acceleration.x), ua.VariantType.Double)
                    await imu_node["linear_acceleration_y"].set_value(float(ros_node.linear_acceleration.y), ua.VariantType.Double)
                    await imu_node["linear_acceleration_z"].set_value(float(ros_node.linear_acceleration.z), ua.VariantType.Double)

                if ros_node.ip is not None:
                    await ip_node.set_value(str(ros_node.ip), ua.VariantType.String)

                if ros_node.voltage is not None:
                    await battery_state_node["voltage"].set_value(float(ros_node.voltage), ua.VariantType.Float)
                if ros_node.temperature is not None:
                    await battery_state_node["temperature"].set_value(float(ros_node.temperature), ua.VariantType.Float)
                if ros_node.percentage is not None:
                    await battery_state_node["percentage"].set_value(float(ros_node.percentage), ua.VariantType.Float)

                # Kurze Pause 
                await asyncio.sleep(0.05)
                
        except KeyboardInterrupt:
            ros_node.get_logger().info("Strg + C gedrückt: Programm wird beendet...")
        finally:
            await client.disconnect()   
            ros_node.destroy_node()


def main(args=None):
    rclpy.init(args=args)
    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        pass
    finally:
        # ROS2 sauber herunterfahren
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()