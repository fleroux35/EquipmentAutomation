# Author: Florian Le Roux

from ctypes import *
import tempfile
import re
import math
import time
import sys
import UI_RsGUI
import RsDriver
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit


class GUI(UI_RsGUI.mainGUI):
    
    """GUI"""
    
    sigInitTest = pyqtSignal() 
    
    identifierTop = 'TopArm'
    
    identifierBt = 'BottomArm'    

    def __init__(self,MainWindow):
        
        """Take GUI and initialize threads use."""
        
        super().__init__(MainWindow)
        
        self.__threads = None 
        
        self.params = {}  # for storing parameters
        
        self.Log = RsGUI.findChild(QTextEdit,"Log")
        
        self.isTopConnected = False
        
        self.isBottomConnected = False
        
        self.setupConnections()


    def setupConnections(self):
             
        self.cnectButton.clicked.connect(self.attemptConnections)
        self.InitCheckBtn.clicked.connect(self.carryInitialTest)
            
    def attemptConnections(self):
         
            if self.isTopConnected == False and self.isBottomConnected ==  False:
          
                if not self.__threads: 
                
                    self.__threads = []
        
                    #initialize connection on the top thread, perform initial step/angle reading

                    top_thread = RotatingStageQThread()
                    top_thread.setObjectName('thread_' + self.identifierTop) 
                    top_connect_worker = ConnectionWorker(self.identifierTop)
                    top_connect_worker.moveToThread(top_thread)
                    top_thread.started.connect(top_connect_worker.connection) 
                    top_thread.sigInitTest.connect(top_connect_worker.initialTest) 
                    
                    top_thread.start()
                    
                    top_connect_worker.sig_msg.connect(self.react)
                    top_connect_worker.sig_stepsangles.connect(self.updateAnglesAndSteps)
                    top_connect_worker.sig_success.connect(self.connectedToEquipment)
        
                    self.__threads.append((top_thread, top_connect_worker))
        
                    #initialize connection on the bottom thread, perform initial step/angle reading 
        
                    bt_thread = RotatingStageQThread()
                    bt_thread.setObjectName('thread_' + self.identifierBt)          

                    bt_connect_worker = ConnectionWorker(self.identifierBt)
                    bt_connect_worker.moveToThread(bt_thread) 
                    bt_thread.started.connect(bt_connect_worker.connection) 
                    bt_thread.sigInitTest.connect(bt_connect_worker.initialTest) 
                    
                    bt_thread.start()
                    
                    bt_connect_worker.sig_msg.connect(self.react)
                    bt_connect_worker.sig_stepsangles.connect(self.updateAnglesAndSteps)
                    bt_connect_worker.sig_success.connect(self.connectedToEquipment)
        
                    self.__threads.append((bt_thread, bt_connect_worker))
                    

    def carryInitialTest(self):
        
        topThread, topWorker = self.__threads[0]
        btThread, btWorker = self.__threads[1]
        
        topThread.sigInitTest.emit()
        btThread.sigInitTest.emit()        
                    
                    
    def disconnectFromEquipment(self):
        self.Log.append('I disconnect')


    @pyqtSlot(str)   
    def react(self,string: str):
        self.Log.append(string)
        
    @pyqtSlot(str)   
    def connectedToEquipment(self, arm_id: str):
        
        if arm_id == self.identifierTop:
            
            self.topArmButton.setPixmap(QPixmap(":/GreenButton.png"))
            self.isTopConnected = True
            
        if arm_id == self.identifierBt:
            
            self.btArmButton.setPixmap(QPixmap(":/GreenButton.png")) 
            self.isBottomConnected = True
            
        if self.isBottomConnected and self.isTopConnected:
        
            self.cnectButton.setText("Disconnect")
            self.cnectButton.clicked.connect(self.disconnectFromEquipment)
            
    @pyqtSlot(str, float, float)
    def updateAnglesAndSteps(self, arm_id:str, steps:float, angle:float):  
        
        if arm_id == self.identifierTop:
            
            self.stepLCDTop.display(steps)
            self.angleLCDTop.display(angle)
        
        if arm_id == self.identifierBt:
                
            self.stepLCDBt.display(steps)
            self.angleLCDBt.display(angle)
                 
            
    @pyqtSlot()
    def disconnect(self):
        
            self.sig_abort_workers.emit()
            self.log.append('Asking each worker to abort')
            for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
                thread.quit()  # this will quit **as soon as thread event loop unblocks**
                thread.wait()  # <- so you need to wait for it to *actually* quit
            self.log.append('Disconnected from Equipment')    
        
class ConnectionWorker(QObject):
    
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """
    identifierTop = 'TopArm'
    
    identifierBt = 'BottomArm' 
    
    StageDriver = []
    
    sig_success = pyqtSignal(str)  # switch status of the status button from red to green
    sig_msg = pyqtSignal(str)  # message to be shown to user
    sig_stepsangles = pyqtSignal(str,float,float)

    def __init__(self, id: str):
        
        super().__init__()
        self.__id = id

    @pyqtSlot()
    def connection(self):
        
        if self.__id == self.identifierTop:  
                       
            thread_name = QThread.currentThread().objectName()
            thread_id = str(QThread.currentThreadId())  # cast to str is necessary
            self.sig_msg.emit('Running connection worker {} from thread "{}" ({})'.format(self.__id, thread_name, thread_id))
               
            self.StageDriver = RsDriver.RsDriver(0)  
                
            self.readAngles()     
            self.sig_msg.emit('Successful connection to Top Arm')
            self.sig_success.emit(self.__id)
            
        if self.__id == self.identifierBt:  

            #simple wait to ensure the connection to the bottom arm happens after top arm
            time.sleep(0.1)            
        
            thread_name = QThread.currentThread().objectName()
            thread_id = str(QThread.currentThreadId())  # cast to str is necessary
            self.sig_msg.emit('Running connection worker {} from thread "{}" ({})'.format(self.__id, thread_name, thread_id))
        
            self.StageDriver = RsDriver.RsDriver(1) 
            
            self.readAngles()       
            self.sig_msg.emit('Successful connection to Bottom Arm')
            self.sig_success.emit(self.__id)
            
    def initialTest(self):
        
        self.moveToSafePosition()
        
        self.moveTo(45)
        
        self.moveToSafePosition()
        
    def moveToSafePosition(self):
        
        if self.StageDriver != []:
        
            self.StageDriver.moveToSafePosition()
            
        self.readAngles()
            
    def moveTo(self, angle):
        
        if self.StageDriver != []:
            
            self.StageDriver.moveTo(angle)
        
        self.readAngles()
        
    def readAngles(self):
        
        step, ustep = self.StageDriver.getPositions()
        
        self.StageDriver.getCurrentAngleRelativeToNormal()
        
        currentAngle = round(self.StageDriver.currentAngle,3)
        
        self.sig_stepsangles.emit(self.__id,step,currentAngle)         
             
        
    def abort(self):
    
        self.__abort = True
        
class RotatingStageQThread(QThread):
    
    sigInitTest = pyqtSignal()

    def __init__(self):
    
        super().__init__()
        
    
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    RsGUI = QMainWindow()
    ui = GUI(RsGUI)
    RsGUI.show()
    
    sys.exit(app.exec_())
    
   
   