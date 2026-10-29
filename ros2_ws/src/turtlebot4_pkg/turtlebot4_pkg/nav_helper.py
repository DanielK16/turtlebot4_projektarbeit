#Python Code um die Kommunikation mit dem Nav2 Navigator zu vereinfachen
#Die Kommunikation läuft über den NAV2 Simple Commander alle Befehle sind hier zu finden: https://docs.nav2.org/commander_api/index.html#

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

import rclpy
from rclpy.duration import Duration

from helper.c3_helper import action_helper
import math

class navhelp(BasicNavigator):

    def __init__(self, namespace=''):
        super().__init__(namespace=namespace)
        self.acti=action_helper()
       

    def getPoseStamped(self, x ,y ,rot):
        # Funktion um eine PoseStaped zu erzeugen die am Ende ausgegeben wird 
        #Eingabe x,y Koordinaten auf einer Karte rot: Rotation die der Roboter an dieser Stelle haben soll 0-360?

        #Pose als Typ PoseStamped festlegen
        Pose = PoseStamped()

        #Festlegen der Karte sowie der Zeit
        Pose.header.frame_id = 'map'
        Pose.header.stamp = self.get_clock().now().to_msg()

        #Festlegen der Koordinaten 
        Pose.pose.position.x = x
        Pose.pose.position.y = y
        # Convert Z rotation to quaternion
        Pose.pose.orientation.z = math.sin(math.radians(rot) / 2)
        Pose.pose.orientation.w = math.cos(math.radians(rot) / 2)

        return Pose
    
    def getDocked(self):

        if self.acti.getDockedStatus()== False:
            # Roboter fährt vor den Dock
            DockingPose=self.getPoseStamped(0.00696,0.2035,315.0)
            self.goToPose(DockingPose)
            
            #Roboter dockt mit der dock Funktion aus dem Action helper
            self.acti.dock()
        else:
            print("Roboter schon gedockt") #Ausgabe im Terminal


    def setInitialPoseDock(self): 
        # Funktion um die Initialpose mithilfe der Docking Funktion zu setzten 

        #Hier wird der Action_helper verwendet um den Code zu verkürzen und da hier die Zeit nicht wichtig ist
        

        #Wenn der Roboter noch nuicht gedockt ist wird dieser zuerst gedockt
        if self.acti.getDockedStatus()== False: 
            print("Docking bevcolor die Initialpose gesetzt werden kann") #Ausgabe im Terminal
            self.acti.dock()
        
        #Sollte der Roboter nach dem Docking Vorgang immer noch nicht gedockt sein ist es Fehlgeschlagen und der Roboter hat sein dock wahrscheinlich nicht gesehen
        #ist dies der Fall soll der Vorgang abgebrochen werden mit der Angabe an den Benutzer den Roboter woanders hin zu stellen mit der Funktionsrückgabe False die im weiteren Code verwendet werden kann
        if self.acti.getDockedStatus()== False: 
            print("Docking failed Initialisierung kann nicht ausgeführt werden") #Ausgabe im Terminal
            print("bewege den Roboter näher zum Dock und führe das Programm erneut aus") #Ausgabe im Terminal

            return False #Rückgabe "False" falls der Prozess nicht funktioniert hat

        #War das Docken erfolgreich wird der Roboter entdockt, sodass alle Sensoren aktiv sind
        #Hier wird die Vorher ausgelesene Position erstellt und als Initialposition gesetzt
        else:
            initial_pose=self.getPoseStamped(0.131726,0.235034,308) #Festlegen der Initialpose

            #wartet bis Nav2 aktiv ist
            self.waitUntilNav2Active()
            print("Nav2 aktiv") #Ausgabe im Terminal
            self.setInitialPose(initial_pose) #Setzt Initialpose
            self.acti.undock() #Entdockt den Roboter

            return True #Rückgabe "True" wenn der Vorgang erfolgreich war


    def setInitialPoseSim(self): 
        # Funktion um die Initialpose mithilfe der Docking Funktion zu setzten 

        #Wenn der Roboter noch nuicht gedockt ist wird dieser zuerst gedockt
        if self.acti.getDockedStatus()== False: 
            print("Docking bevor die Initialpose gesetzt werden kann")
            self.acti.dock()
        
        #Sollte der Roboter nach dem Docking Vorgang immer noch nicht gedockt sein ist es Fehlgeschlagen und der Roboter hat sein dock wahrscheinlich nicht gesehen
        #ist dies der Fall soll der Vorgang abgebrochen werden mit der Angabe an den Benutzer den Roboter woanders hin zu stellen mit der Funktionsrückgabe False die im weiteren Code verwendet werden kann
        if self.acti.getDockedStatus()== False: 
            print("Docking failed Initialisierung kann nicht ausgeführt werden")
            print("bewege den Roboter näher zum Dock und führe das Programm erneut aus")

            return False #Rückgabe "False" falls der Prozess nicht funktioniert hat

        #War das Docken erfolgreich wird der Roboter entdockt, sodass alle Sensoren aktiv sind
        #Hier wird die Vorher ausgelesene Position erstellt und als Initialposition gesetzt
        else:
            initial_pose=self.getPoseStamped(0.0,0.0,0) #Festlegen der Initialpose

            self.waitUntilNav2Active() #wartet bis Nav2 aktiv ist
            print("Nav2 aktiv")#Ausgabe im Terminal
            self.setInitialPose(initial_pose) #Setzt Initialpose
            self.acti.undock()#Entdockt den Roboter 

            return True #Rückgabe "True" wenn der Vorgang erfolgreich war

    

        
