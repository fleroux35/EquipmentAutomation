# -*- coding: utf-8 -*-

import sys
from ExtremeDriver import ExtremeDriver
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QLabel

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
    def turnLaserOnOff(self, OnOrOff:int): 
        
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
    #ui = GUI(ExtremeGUI)
    #ExtremeGUI.show()
    
    laserWorker = LaserWorker()
    print('initialized')
    
    sys.exit(app.exec_())