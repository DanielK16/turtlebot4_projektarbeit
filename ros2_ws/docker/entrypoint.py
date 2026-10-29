# Autor: Daniel Körper
# Startet den OPC UA Client um SoftKeys aus Codesys zu verwenden
# Wird mit Start des Containers gestartet

import subprocess
import os 
import signal

import asyncio
from asyncua import Client

import yaml
with open("/home/ros/ros2_ws/src/turtlebot4_pkg/config/opc_topic_config.yml", "r") as f:
    config = yaml.safe_load(f)
config['OPC_Client']['ipaddress'] = os.environ.get('OPC_IP', config['OPC_Client']['ipaddress'])

# Globale Variablen
SLAM_SYNC_IS_RUNNING = False
SLAM_ASYNC_IS_RUNNING = False
OPC_CLIENTS_IS_RUNNING = False
RVIZ2_ROBOT_IS_RUNNING = False
NAV2_IS_RUNNING = False
LOCALISATION_IS_RUNNING= False

# Prozesse
SLAM_SYNC_PROZESS = None
SLAM_ASYNC_PROZESS = None
OPC_CLIENTS_PROZESS = None
RVIZ2_ROBOT_PROZESS = None
NAV2_PROZESS = None
LOCALIZATION_PROZESS = None

def Start_SLAM_sync():
    global SLAM_SYNC_IS_RUNNING
    global SLAM_SYNC_PROZESS
    # Verhindern, dass der Launch doppelt gestartet wird
    if SLAM_SYNC_IS_RUNNING is True and SLAM_SYNC_PROZESS.poll() is None:
        print("SLAM Synchron läuft bereits!")
        return

    command = "ros2 launch turtlebot4_navigation slam.launch.py sync:=true"
    SLAM_SYNC_PROZESS = subprocess.Popen(["/bin/bash", "-c", command],start_new_session=True)
    print("Synchroner SLAM Launch gestartet")
    SLAM_SYNC_IS_RUNNING=True

def Stop_SLAM_sync():
    global SLAM_SYNC_IS_RUNNING
    global SLAM_SYNC_PROZESS
    if SLAM_SYNC_IS_RUNNING is True:
        print("Sende Stop Signal...")
        try:
            os.killpg(os.getpgid(SLAM_SYNC_PROZESS.pid), signal.SIGINT)
            SLAM_SYNC_PROZESS.wait(timeout=5)
            print(f"Synchroner SLAM Launch erfolgreich beendet")
        except Exception as e:
            print(f"Fehler beim Beenden: {e}")
        finally:
            SLAM_SYNC_IS_RUNNING = False
    else:
        print("Kein Prozess da zum stoppen!")

def Start_SLAM_async():
    global SLAM_ASYNC_IS_RUNNING
    global SLAM_ASYNC_PROZESS
    # Verhindern, dass der Launch doppelt gestartet wird
    if SLAM_ASYNC_IS_RUNNING is True and SLAM_AYNC_PROZESS.poll() is None:
        print("SLAM Asynchron läuft bereits!")
        return

    command = "ros2 launch turtlebot4_navigation slam.launch.py sync:=false"
    SLAM_ASYNC_PROZESS = subprocess.Popen(["/bin/bash", "-c", command],start_new_session=True)
    print("Synchroner SLAM Launch gestartet")
    SLAM_ASYNC_IS_RUNNING=True

def Stop_SLAM_async():
    global SLAM_ASYNC_IS_RUNNING
    global SLAM_ASYNC_PROZESS
    if SLAM_ASYNC_IS_RUNNING is True:
        print("Sende Stop Signal...")
        try:
            os.killpg(os.getpgid(SLAM_ASYNC_PROZESS.pid), signal.SIGINT)
            SLAM_ASYNC_PROZESS.wait(timeout=5)
            print(f"Asynchroner SLAM Launch erfolgreich beendet")
        except Exception as e:
            print(f"Fehler beim Beenden: {e}")
        finally:
            SLAM_ASYNC_IS_RUNNING = False
    else:
        print("Kein Prozess da zum stoppen!")

def Start_RViz2_Robot():
    global RVIZ2_ROBOT_IS_RUNNING
    global RVIZ2_ROBOT_PROZESS
    # Verhindern, dass der Launch doppelt gestartet wird
    if RVIZ2_ROBOT_IS_RUNNING is True and RVIZ2_ROBOT_PROZESS.poll() is None:
        print("RVi2 Roboter läuft bereits!")
        return

    command = "ros2 launch turtlebot4_viz view_robot.launch.py"
    RVIZ2_ROBOT_PROZESS = subprocess.Popen(["/bin/bash", "-c", command],start_new_session=True)
    print("RViz2 Roboter Launch gestartet")
    RVIZ2_ROBOT_IS_RUNNING=True

def Stop_RViz2_Robot():
    global RVIZ2_ROBOT_IS_RUNNING
    global RVIZ2_ROBOT_PROZESS
    if RVIZ2_ROBOT_IS_RUNNING is True:
        print("Sende Stop Signal...")
        try:
            os.killpg(os.getpgid(RVIZ2_ROBOT_PROZESS.pid), signal.SIGINT)
            RVIZ2_ROBOT_PROZESS.wait(timeout=5)
            print(f"RViz2 Roboter Launch erfolgreich beendet")
        except Exception as e:
            print(f"Fehler beim Beenden: {e}")
        finally:
            RVIZ2_ROBOT_IS_RUNNING = False
    else:
        print("Kein Prozess da zum stoppen!")

def Start_OPC_Clients():
    global OPC_CLIENTS_IS_RUNNING
    global OPC_CLIENTS_PROZESS
    # Verhindern, dass der Launch doppelt gestartet wird
    if OPC_CLIENTS_IS_RUNNING is True and OPC_CLIENTS_PROZESS.poll() is None:
        print("OPC Clients läuft bereits!")
        return

    arbeitsverzeichnis = os.path.expanduser("~/ros2_ws")
    command = "source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch turtlebot4_pkg opc_clients_launch.py"
    OPC_CLIENTS_PROZESS = subprocess.Popen(["/bin/bash", "-c", command],cwd=arbeitsverzeichnis, start_new_session=True)
    print("OPC Clients gestartet")
    OPC_CLIENTS_IS_RUNNING=True

def Stop_OPC_Clients():
    global OPC_CLIENTS_IS_RUNNING
    global OPC_CLIENTS_PROZESS

    if OPC_CLIENTS_IS_RUNNING is True:
        print("Sende Stopp-Signal an Communication Client...")
        try:
            os.killpg(os.getpgid(OPC_CLIENTS_PROZESS.pid), signal.SIGINT)
            OPC_CLIENTS_PROZESS.wait(timeout=5)
            print("OPC Clients Launch erfolgreich beendet.")
        except Exception as e:
            print(f"Fehler beim Beenden: {e}")
        finally:
            OPC_CLIENTS_IS_RUNNING = False
    else:
        print("Kein Prozess da zum stoppen!")

def Start_Lokalisierung():
    print("start lokal")
def Stop_Lokalisierung():
    print("stop lokal")

def Start_Navigation2():
    global NAV2_IS_RUNNING
    global NAV2_PROZESS
    # Verhindern, dass der Launch doppelt gestartet wird
    if NAV2_IS_RUNNING is True and NAV2_PROZESS.poll() is None:
        print("NAV2 läuft bereits!")
        return

    command = "ros2 launch turtlebot4_navigation nav2.launch.py"
    RVIZ2_ROBOT_PROZESS = subprocess.Popen(["/bin/bash", "-c", command],start_new_session=True)
    print("RViz2 Roboter Launch gestartet")
    RVIZ2_ROBOT_IS_RUNNING=True
def Stop_Navigation2():
    print("nav2 s")


class SubscriptionHandler:
    def datachange_notification(self, node, val, data):
        try:
            # Nur Ausführen wenn Wert auf True gesetzt wird
            if val == True:
                # Prüfen ob Name in NodeId vorkommt
                if "Start_SLAM_sync" in str(node.nodeid):
                    Start_SLAM_sync()
                elif "Stop_SLAM_sync" in str(node.nodeid):
                    Stop_SLAM_sync()
                elif "Start_SLAM_async" in str(node.nodeid):
                    Start_SLAM_async()
                elif "Stop_SLAM_async" in str(node.nodeid):
                    Stop_SLAM_async()
                elif "Start_RViz2_Robot" in str(node.nodeid):
                    Start_RViz2_Robot()
                elif "Stop_RViz2_Robot" in str(node.nodeid):
                    Stop_RViz2_Robot()      
                elif "Start_OPC_Clients" in str(node.nodeid):
                    Start_OPC_Clients()
                elif "Stop_OPC_Clients" in str(node.nodeid):
                    Stop_OPC_Clients()
                elif "Start_Lokalisierung" in str(node.nodeid):
                    Start_Lokalisierung()   
                elif "Stop_Lokalisierung" in str(node.nodeid):
                    Stop_Lokalisierung()
                elif "Start_Navigation2" in str(node.nodeid):
                    Start_Navigation2()
                elif "Stop_Navigation2" in str(node.nodeid):
                    Stop_Navigation2()
        except Exception as e:
            print(f"Fehler im Subscription Handler: {e}")

async def async_main():
    while True:
        try:
            # OPC UA Verbindung
            ipaddress = config['OPC_Client']['ipaddress']
            port = "4840"
            opc_url = f"opc.tcp://{ipaddress}:{port}"

            async with Client(url = opc_url,
                            timeout = 2.0,
                            watchdog_intervall = 0.5, 
                            auto_reconnect = True,  
                            reconnect_max_delay = 5.0,    
                            reconnect_request_timeout = 5.0, ) as client:
                print(f"OPC Client verbunden: {opc_url}")

                nodes = [
                    # Sync Slam
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Start_SLAM_sync"),
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Stop_SLAM_sync"),
                    # Async SLAM
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Start_SLAM_async"),
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Stop_SLAM_async"),
                    # RViz2 Roboter
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Start_RViz2_Robot"),
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Stop_RViz2_Robot"),
                    # OPC Kommunikation
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Start_OPC_Clients"),
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Stop_OPC_Clients"),
                    # Lokalisierung
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Start_Lokalisierung"),
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Stop_Lokalisierung"),
                    # Navigation 2
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Start_Navigation2"),
                    client.get_node("ns=4;s=|var|CODESYS Virtual Control for Linux SL.Application.GVL_OPCUA.Stop_Navigation2"),
                ]

                # Subscription erstellen
                handler = SubscriptionHandler()
                subscription = await client.create_subscription(500, handler)
                await subscription.subscribe_data_change(nodes)

                while True:
                    await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Verbindungsabbruch {ipaddress}: {e}")
            # Wartet 5 Sekunden vor erneutem Versuch
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Str + C gedrückt: Beende alle ROS2 Prozesse")
    finally:
        print("Alle Prozesse beendet!")
