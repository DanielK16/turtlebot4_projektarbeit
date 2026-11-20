# Steuerung eines TurtleBot4 aus Codesys via OPC UA  
Dieses Repository enthält eine Kommunikationsschnittstelle zwischen einer virtuellen CODESYS-SPS (vSPS) und einem realen TurtleBot 4 Lite auf Basis von OPC UA und ROS 2 Humble. Der Roboter wird vollständig über eine CODESYS-Visualisierung bedient: Sensor- und Zustandsdaten werden an die SPS übertragen, der Roboter wird im Handbetrieb gesteuert oder navigiert autonom mit Nav2 zu vorgegebenen Zielpositionen in einer zuvor mit SLAM erstellten Karte.  

## Aufbau und Installation der Entwicklungsumgebung  
Die ROS 2 Programme laufen in einem Docker-Container unter WSL2. Da WSL2 im NAT-Modus betrieben wird, ist eine direkte DDS-Verbindung zum Roboter im WLAN nicht möglich. Die Verbindung zwischen Container und TurtleBot 4 erfolgt deshalb über die zenoh-bridge-ros2dds.
![Aufbau_Entwicklungsumgebung](doc/img/Entwicklungsumgebung_TB4.svg)  
## Installation und Aufbau der Container
Innerhalb des Dockerfiles werden die Zenoh-Schnittstelle und die TurtleBot-4-Pakete installiert und der `ros2_ws` mit `colcon build` gebaut. Anschließend wird aus dem Dockerfile das Image gebaut und aus dem Image der Container erstellt. Beim Start des Containers wird `entrypoint.py` automatisch ausgeführt.
![Ablauf Dockerfile → Image → Container](doc/img/Dockerfile_Image_Container.svg)
#### Dockerfile -> Image
```bash
docker build \
  --build-arg ROS_DISTRO=humble \
  --build-arg ZENOH_VERSION=1.9.0 \
  --build-arg SYSTEM_VERSION=x86_64 \
  -t turtlebot4_projektarbeit:latest \
  .
```
| Parameter | Erklärung |
|---|---|
| `ROS_DISTRO` | ROS 2 Distribution des Basis-Images. Das Projekt wurde mit **Humble** entwickelt. |
| `ZENOH_VERSION` | Version der zenoh-bridge-ros2dds. Verwendet wird **1.9.0**, da mit Version 1.10.0 nicht alle Topics korrekt übertragen wurden. Die Version muss mit der Bridge auf dem TurtleBot 4 übereinstimmen. |
| `SYSTEM_VERSION` | Prozessorarchitektur des Zielsystems: `x86_64` für einen PC, `aarch64` für ARM-Rechner (z. B. Raspberry Pi). |
| `-t` | Name und Tag des Images (`turtlebot4_projektarbeit:latest`). |
| `.` | Build-Kontext: das aktuelle Verzeichnis, in dem das Dockerfile liegt. |

#### Image -> Container
```bash
docker run -it \
  --name tb4_container \
  --hostname ros_container \
  --network=host \
  -e OPC_IP=172.21.225.150 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  turtlebot4_projektarbeit
```
| Parameter | Erklärung |
|---|---|
| `-it` | Startet den Container interaktiv mit Terminal. Die Ausgaben von `entrypoint.py` werden direkt angezeigt. |
| `--name` | Name des Containers (`tb4_container`). Über diesen Namen wird der Container später gestartet und geöffnet. |
| `--hostname` | Hostname innerhalb des Containers (`ros_container`). |
| `--network=host` | Der Container nutzt das Netzwerk des Hosts (WSL2). Dadurch ist die Verbindung zum Zenoh Router auf dem TurtleBot 4 und zum OPC UA Server möglich. |
| `-e OPC_IP` | IP-Adresse des OPC UA Servers (vSPS). Die Umgebungsvariable hat Vorrang vor der Konfigurationsdatei `opc_topic_config.yml`. Die IP-Adresse wird in WSL mit `ip a` ermittelt. |
| `-e DISPLAY` | Teilt dem Container mit, mit welchem Display er sich für grafische Anwendungen (z. B. RViz2) verbindet. |
| `-v /tmp/.X11-unix:/tmp/.X11-unix` | Bindet die Schnittstelle ein, über die der X Server von WSL kommuniziert. |
| `turtlebot4_projektarbeit` | Name des Images, aus dem der Container erstellt wird. |

## Aufbau der Clients
![Aufbau_Clients](doc/img/Aufbau_Clients_TB4.svg)  
## Kartenerstellung mit SLAM aus Codesys:
![Schrittkette_TB4](doc/gif/TB4_Kartenerstellung_x4.gif)
## Autonome Navigation
Ansteuerung des Roboters aus dem Raum 103 und wieder zurück aus einer Schrittkette aus Codesys.
![Schrittkette_TB4](doc/gif/TB4_Schrittkette_x5.gif)
