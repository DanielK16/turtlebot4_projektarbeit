#Nele Heinz 2025
#Python Code um die Kommunikation mit den Actions vom Create3 zu erleichtern sodass der Code durchschnittlich kürzer wird 

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data, qos_profile_system_default
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

import time

from irobot_create_msgs.action import Dock   #Dock Funktion importieren --> hat beim ersten Versuch nicht funktioniert irobot_create_msgs konnte nicht gefunden werden
from irobot_create_msgs.action import Undock   #Dock Funktion importieren --> hat beim ersten Versuch nicht funktioniert irobot_create_msgs konnte nicht gefunden werden
from irobot_create_msgs.msg import DockStatus
from sensor_msgs.msg import BatteryState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistWithCovariance
from geometry_msgs.msg import TransformStamped

class action_helper(Node):		
	#Variablendeklaration
	is_docked=None

	def __init__(self):
		super().__init__('action_helper_node')
		#Erstellen der Action Clients
		self.dock_action_client = ActionClient(self,Dock,'/dock')
		self.undock_action_client = ActionClient(self, Undock, '/undock')	

		#Erstellen der nötigen Subs
		self.create_subscription(DockStatus,'dock_status',self.dockCallback,qos_profile_sensor_data)
	
	#Funktion für das Erhalten der Information ob der Roboter im Dock ist oder nicht
	def dockCallback(self,msg: DockStatus):
		#Abruf kann TRUE oder FALSE zurückgeben
		self.is_docked = msg.is_docked

	#Funktion um den Dockstatus zu erhalten 
	def getDockedStatus(self):

		#Spin der eigenen Funktion um über die Subscription Informationen zu erhalten 
		rclpy.spin_once(self, timeout_sec=0.1)
        
		#Wenn noch keine Information erhalten wurde wird die Funktion erneut abgerufen bis die Info da ist
		while self.is_docked is None:
			rclpy.spin_once(self, timeout_sec=0.1)
		
		#Rückgabe der Information
		return self.is_docked

	
	#Funktion die den Roboter über eine Action dockt und dauerhaftes feedback gibt
	def dock(self):
		
		#Dock Status abrufen
		dstatus=self.getDockedStatus()
		
		#Wenn der Roboter schon gedockt ist wird die Funktion beendet
		if dstatus==True:
			print("Roboter schon gedockt") #Ausgabe im Terminal
			return
		
		else:
			#Information zum Docken festlegen
			msg=Dock.Goal()
			print('Docking started') #Ausgabe im Terminal
			#Warten auf Server
			self.dock_action_client.wait_for_server()
			print('Server bereit') #Ausgabe im Terminal
			#Befehl an Server schicken
			self.dock_action_client.send_goal_async(msg)
			i=0
			#Dauerhafte ausgabe während der Dockingvorgangs
			while dstatus == False:
				i=i+1
				if i%10==0 :
					print("docking...") #Ausgabe im Terminal
				dstatus=self.getDockedStatus()
			
			return 
			
	#Funktion die den Roboter über eine Action entdockt und dauerhaftes feedback gibt
	def undock(self):

		#Dock Status abrufen
		dstatus=self.getDockedStatus()

		#Wenn der Roboter schon entdockt ist wird die Funktion beendet
		if dstatus==False:
			print("der Roboter ist schon entdockt") #Ausgabe im Terminal
			return
		else:
			#Information zum Entdocken festlegen
			msg=Undock.Goal()
			print('Undocking started') #Ausgabe im Terminal
			#Warten auf Server
			self.undock_action_client.wait_for_server()
			print('Server bereit') #Ausgabe im Terminal
			#Befehl an Server schicken
			self.undock_action_client.send_goal_async(msg)
			
			i=0
			#Dauerhafte ausgabe während der Dockingvorgangs
			while dstatus == True:
				i=i+1
				if i%10==0 :
					print("undocking...") #Ausgabe im Terminal
				dstatus=self.getDockedStatus()
			
			return

#Funtkion zum Abrufen des aktuellen Ladezustandes des Roboters
#Funktion kann in anderen Funktionen verwendet werden wenn die Zeit nicht wichitg ist sonst solte sie in dem Programm selbst dauerhaft verwendet (Spin) werden
class Batterie(Node): 
	#Deklarieren der Variablen
	battery_perc=None #Speichert den Batteriezustand in %

	def __init__(self):
		super().__init__('batterie_node') #Benennung der Node

		#Erstellen der Subs
		self.batterystate_sub = self.create_subscription(BatteryState, '/battery_state', self.battery,qos_profile_sensor_data)
		self.batterystate_sub # verhindert "unused variable"-Warnung

	#Rückruffunktion des Batteriestatusen
	def battery(self,msg:BatteryState):
		#Variable speichert die aktuelle Ladung in Prozent
		self.battery_perc=msg.percentage

	#Funktion zum erhalten des Batteriestatuses
	def getBatterieStatusperc(self):
        #Funktion abrufen
		rclpy.spin_once(self, timeout_sec=0.1)
       
	    #Funktion abrufen bis gewünschte Information vorhanden ist
		while self.battery_perc is None:
			rclpy.spin_once(self, timeout_sec=0.1)
		
		#Ausgabe der Information
		return self.battery_perc 


#Funtkion zum Abrufen des aktuellen Odometrie des Roboters
#Funktion kann in anderen Funktionen verwendet werden wenn die Zeit nicht wichitg ist sonst solte sie in dem Programm selbst dauerhaft verwendet (Spin) werden
class OdomSubscriber(Node):
	#Deklarieren der Variablen
	position=None #Speichert die Position
	orientation=None #Speichert die Orientierung
	linear=None #Speichern von twist.linear
	angular=None #Speicehern von twist.angular
	
	def __init__(self):
		super().__init__('odom_listener')
		#Estellen des benötigten QOS Profils
		qos_profile_odom = QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT,history=QoSHistoryPolicy.KEEP_LAST,depth=10)
		#Erstellung der Subs
		self.subscription = self.create_subscription(Odometry,'/odom',self.odom_callback,qos_profile_odom)
		self.subscription  # verhindert "unused variable"-Warnung

	#Rückruffunktion 
	def odom_callback(self, msg):
		#Zuweisung der Werte zu den passenden Variablen
		self.position = msg.pose.pose.position
		self.orientation = msg.pose.pose.orientation
		self.linear = msg.twist.twist.linear
		self.angular = msg.twist.twist.angular

	#Funktionen zur Ausgabe der Informationen

	def getOdomTwistlin(self): #ruft die eigene Klasse solange ab, bis Informationen vorhanden sind
		rclpy.spin_once(self, timeout_sec=0.1) 
       	
		while self.linear is None:
			rclpy.spin_once(self, timeout_sec=0.1)
		
		return self.linear #Rückgabe Variable
	
	def getOdomTwistang(self): #ruft die eigene Klasse solange ab, bis Informationen vorhanden sind
        # Spin to get latest status
		rclpy.spin_once(self, timeout_sec=0.1)
		
        # If dock status hasn't been published yet, spin until it is
		
		while self.angular is None:
			rclpy.spin_once(self, timeout_sec=0.1)
		
		return self.angular #Rückgabe Variable
	
	def getOdomPosePosition(self): #ruft die eigene Klasse solange ab, bis Informationen vorhanden sind
        # Spin to get latest status
		rclpy.spin_once(self, timeout_sec=0.1)
        # If dock status hasn't been published yet, spin until it is
		
		while self.position is None:
			rclpy.spin_once(self, timeout_sec=0.1)
		
		return self.position #Rückgabe Variable
	
	def getOdomPoseOrientation(self): #ruft die eigene Klasse solange ab, bis Informationen vorhanden sind
        # Spin to get latest status
		rclpy.spin_once(self, timeout_sec=0.1)
        # If dock status hasn't been published yet, spin until it is
		
		while self.orientation is None:
			rclpy.spin_once(self, timeout_sec=0.1)
		
		return self.orientation #Rückgabe Variable

	
