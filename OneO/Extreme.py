# -*- coding: utf-8 -*-

import sys
import ExtremeGUI
from ExtremeDriver import ExtremeDriver
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QLabel

class GUI(ExtremeGUI.mainGUI):
    
    """GUI"""
    
    ## Signals definitions for Qt threading ##
    
    #Signal for turning emission on (1) and off (0)
    
    sig_turnOnOff = pyqtSignal(int)
   
    #Signal emitted to ask for disconnection.  
    
    sig_disconnectEquipment = pyqtSignal()
    
    #Signal emitted to check the status of the emission
    
    sig_requeststatus = pyqtSignal()
    
    sig_power = pyqtSignal(float)
    
    sig_wvl = pyqtSignal(float)
    
    sig_repRate = pyqtSignal(int)

    def __init__(self,MainWindow):
        
        """Take GUI and initialize threads use."""
        
        super().__init__(MainWindow)
        
        self.__threads = None 
        
        self.params = {}  # for storing parameters
        
        self.Log = ExtremeGUI.findChild(QTextEdit,"Log")
        
        self.isConnected = False
        
        #laserIsOn is the status of the emission, it is initially set to True as it is the most dangerous case scenario
        
        self.laserIsOn = True
           
        self.setupConnections()
        
        
    def setupConnections(self):
             
        self.cnectButton.clicked.connect(self.attemptConnection)
        self.powerButton.clicked.connect(self.turnOnOff)
        self.applyButton.clicked.connect(self.setWvlFromPrompt)
        self.applyButton.clicked.connect(self.setPowerFromPrompt)
        self.applyButton.clicked.connect(self.setRepRateFromPrompt)
        
    def attemptConnection(self):
        
        #this method finds all relevant equipment (laser/monochromators)
        #on the different ports.
         
            if self.isConnected == False:
                
                self.__threads = []

                laser_thread = QThread()
                laser_thread.setObjectName('laser_thread') 
                laser_worker = LaserWorker()
                laser_worker.moveToThread(laser_thread)
                laser_thread.started.connect(laser_worker.equipmentScanAndConnect) 

                laser_worker.sigcnection.connect(self.connectedToEquipment)
                
                self.sig_requeststatus.connect(laser_worker.emissionStatus)
                laser_worker.sig_status.connect(self.isLaserOnOff)
                
                self.sig_turnOnOff.connect(laser_worker.turnOnOff)
                
                laser_worker.sigpower.connect(self.updatePower)
                laser_worker.sigreprate.connect(self.updateRepRate)
                laser_worker.sigwvl.connect(self.updateWvl)
                
                self.sig_power.connect(laser_worker.setPower)
                self.sig_wvl.connect(laser_worker.setWvl)
                self.sig_repRate.connect(laser_worker.setRepRate)
                
                laser_worker.sigmsg.connect(self.react)
                                   
                laser_thread.start()
                            
                self.__threads.append((laser_thread, laser_worker))
                
    @pyqtSlot(str)   
    def react(self,string: str):
        
        self.Log.append(string)
        
    @pyqtSlot(bool)   
    def connectedToEquipment(self, status:bool):
        
        self.checkEmissionStatus()
        
        if status == True:
        
            self.isConnected = True   
            self.isConnectedupdatePosition = True
        
            self.cnectButton.setText("Disconnect")
        
            self.cnectStatusButton.setPixmap(QtGui.QPixmap(":/OrangeButton.png"))
            self.cnectButton.clicked.disconnect()
            self.cnectButton.clicked.connect(self.disconnectFromEquipment)
            
            self.react('Connection to laser Successful')
            
    def checkEmissionStatus(self):
        
        self.sig_requeststatus.emit()
        
    @pyqtSlot(bool) 
            
    def isLaserOnOff(self, emissionStatus:bool):  
    
        if emissionStatus:
            
            self.laserIsOn = True
            
            self.powerButton.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(0, 255, 0);")
            
            self.cnectStatusButton.setPixmap(QtGui.QPixmap(":/GreenButton.png"))               
            
        else:
            
            self.laserIsOn = False
            
            self.powerButton.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 0, 0);") 
            
            self.cnectStatusButton.setPixmap(QtGui.QPixmap(":/OrangeButton.png"))     
    
    @pyqtSlot()      
    def turnOnOff(self):        
        
        if self.laserIsOn:
            
            #turn laser off
            
            self.sig_turnOnOff.emit(0)
            
        else:
            
            #turn laser on
    
            self.sig_turnOnOff.emit(1)
            
    @pyqtSlot(float) 
    def updatePower(self,power:float):
        
        self.react('Updating power.')
        self.lcdPower.display(power) 
        
    @pyqtSlot(float) 
    def updateRepRate(self,reprate:float):
        
        self.react('Updating repetition rate.')
        self.lcdFrequency.display(reprate)


    @pyqtSlot(float)
    def updateWvl(self, wvl:float):
        
        self.react('Updating wavelength.')
        self.lcdWavelength.display(wvl)
        
    @pyqtSlot() 
    def setWvlFromPrompt(self):
        
        self.sig_wvl.emit(float(self.wavelengthPrompt.toPlainText()))

    @pyqtSlot() 
    def setRepRateFromPrompt(self):
        
        self.sig_repRate.emit(float(self.frequencyPrompt.toPlainText()))        
    
        
    @pyqtSlot() 
    def setPowerFromPrompt(self):
        
        self.sig_power.emit(float(self.powerPrompt.toPlainText()))    
    
    @pyqtSlot() 
    def disconnectFromEquipment(self):
        
        self.sig_disconnectEquipment.emit()

class LaserWorker(QObject):
    
    sigcnection = pyqtSignal(bool) 
    sigmsg = pyqtSignal(str)
    sig_status = pyqtSignal(bool)
    sigpower = pyqtSignal(float)
    sigreprate = pyqtSignal(float)
    sigwvl = pyqtSignal(float)
    
    def __init__(self):
        
        super().__init__()
        self.LaserDriver = ExtremeDriver()
        
    @pyqtSlot()
    def equipmentScanAndConnect(self):
        
        self.sigmsg.emit('Attempting connection to SuperK Extreme.')
        
        status = self.LaserDriver.equipmentScanAndConnect()
        initialPowerSetting = self.LaserDriver.readPower()
        initialRepRate = self.LaserDriver.readRepRate()
        initialWvl = self.LaserDriver.readWavelengthExtendUV()

        self.sigcnection.emit(status)
        self.sigpower.emit(initialPowerSetting)
        self.sigreprate.emit(initialRepRate)
        self.sigwvl.emit(initialWvl)
            
    @pyqtSlot()
    def emissionStatus(self): 
                        
        self.sig_status.emit(self.LaserDriver.laserIsOn())
        
    @pyqtSlot(float)
    def setPower(self,power:float): 
        
        self.LaserDriver.writePower(power)
                        
        self.sigpower.emit(power) 
        
    @pyqtSlot(int)
    def setRepRate(self,reprateRatio:int): 
                        
        self.LaserDriver.writeRepRate(reprateRatio)  
        
        self.sigreprate.emit(round(self.LaserDriver.heartFrequency/reprateRatio,2))

    @pyqtSlot(float)
    def setWvl(self,wavelength:float): 
                        
        self.LaserDriver.setWavelengthExtendUV(wavelength)
        
        self.sigwvl.emit(wavelength)
        
    @pyqtSlot(int)
    def turnOnOff(self, OnOrOff:int): 
        
        if OnOrOff == 0:
            
            #turn Off
                        
            turnedOff = self.LaserDriver.switchOffLaser()
            
            if turnedOff == 0 :
                
                self.sig_status.emit(False)
            
        if OnOrOff == 1:
    
            #turn On
                
            turnedOn = self.LaserDriver.switchOnLaser()
            
            if turnedOn == 0 :
                
                self.sig_status.emit(True)
 
    @pyqtSlot()
    def disconnectEquipment(self): 
        
        self.turnOnOff(0)
        
        self.LaserDriver.disconnect()
        
        self.sigmsg.emit('Disconnected from laser')
    
            
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    ExtremeGUI = QMainWindow()
    ui = GUI(ExtremeGUI)
    ExtremeGUI.show()
    
    sys.exit(app.exec_())