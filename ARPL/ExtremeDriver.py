# -*- coding: utf-8 -*-

import sys
from NKTP_DLL import *
import time
import numpy as np
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QLabel

class ExtremeDriver():
    
    def __init__(self):
        
        #rep rate is read in Mhz
        
        self.heartFrequency = 77.87
    
        self.laserCOM = 'undefined'
        self.hasFoundLaser = False
        
        self.UVMonochromator = 'undefined'
        self.isConnectedToUVMonochromator = False
          
        self.VisMonochromator = 'undefined'
        self.isConnectedtoVisMonochromator = False
        
        
    def equipmentScanAndConnect(self):
             
        # print('Find modules on all existing and accessible ports - Might take a few seconds to complete.....')
       
        openPorts(getAllPorts(), 1, 1)

        # All ports returned by the getOpenPorts function has modules (ports with no modules will automatically be closed)
     
        portlist = getOpenPorts().split(',')
        
        for portName in portlist:
            
            result, devList = deviceGetAllTypes(portName)
            
            for devId in range(0, len(devList)):
                
                if (devList[devId] != 0):
                    
                    print('Comport:',portName,'Device type:',"0x%0.2X" % devList[devId],'at address:',devId)
                    
        #records addresses of the different components
        
        self.laserCOM = getOpenPorts()
        
        self.hasFoundLaser = True
        
        #self.UVMonochromator = 
        #self.VisMonochromator
        
        return(self.hasFoundLaser)

        
    def disconnect(self):
    
        # Close all ports
        
        closeResult = closePorts('')
        
        print('Close result: ', PortResultTypes(closeResult))
        
        self.hasFoundLaser = False
        
    def laserIsOn(self):
        
        if self.hasFoundLaser:
            
            result,resultdata = registerReadU8(self.laserCOM, 15, 0x30,-1)
            
            if resultdata == 3:
                
                return True
            
            else:
                
                return False
    
    def switchOnLaser(self):
        
        if self.hasFoundLaser:
         
            result = registerWriteU8(self.laserCOM, 15, 0x30, 0x03, -1)
        
            interpretedResult = RegisterResultTypes(result)
        
            if interpretedResult == '0:RegResultSuccess':
    
                return (0)     
        
        else:
            
            return ('Please connect to Laser first')
            
    
    def switchOffLaser(self):
        
        if self.hasFoundLaser:
        
            result = registerWriteU8(self.laserCOM, 15, 0x30, 0x00, -1)
        
            interpretedResult = RegisterResultTypes(result)
            
            if interpretedResult == '0:RegResultSuccess':
    
                return (0)    
        else:
        
            return ('Please connect to Laser first')   
        
    def readPower(self):
        
        if self.hasFoundLaser:
        
            result, resultdata = registerReadU16(self.laserCOM, 15, 0x37, -1)
            
            return (resultdata/10)  
        
        else:
        
            return ('Please connect to Laser first')
        
    def writePower(self,power):
        
        powerConverted = np.uint32(power*10)
        
        if self.hasFoundLaser:
            
            result = registerWriteU32(self.laserCOM, 15, 0x37, powerConverted, -1)
            
            interpretedResult = RegisterResultTypes(result)
        
            if interpretedResult == '0:RegResultSuccess':

                return ('Power set to {}%'.format(power))       
        else:
                    
            return ('Please connect to Laser first') 
        
    def readRepRate(self):
        
        if self.hasFoundLaser:
        
            result, resultdata = registerReadU8(self.laserCOM, 15, 0x34, -1)
            
            return (float(round(self.heartFrequency/resultdata,2)))  
        
        else:
        
            return ('Please connect to Laser first') 
        
    def writeRepRate(self,repRateRatio):
        
        if self.hasFoundLaser:
            
            result = registerWriteU8(self.laserCOM, 15, 0x34, repRateRatio, -1)
            
            interpretedResult = RegisterResultTypes(result)
        
            if interpretedResult == '0:RegResultSuccess':

                return ('Rep Rate set to {} MHz'.format(round(self.heartFrequency/repRateRatio),2))       
        else:
                    
            return ('Please connect to Laser first') 
        
        
    def readWavelengthExtendUV(self):             
                
        if self.hasFoundLaser:
        
            result, resultdata = registerReadU16(self.laserCOM, 16, 0x31, 0)
            
            return (resultdata/10)  
        
        else:
        
            return ('Please connect to Laser first')
        
    def setWavelengthExtendUV(self,wavelength):
        
        #wavelength can be entered with 1/10 nm precision
                
        if self.hasFoundLaser:
        
            result = registerWriteU16(self.laserCOM, 16, 0x31, int(wavelength*10), 0)
            
            interpretedResult = RegisterResultTypes(result)
        
            if interpretedResult == '0:RegResultSuccess':

                return ('Wavelength set to {} nm'.format(wavelength))    
        
        else:
        
            return ('Please connect to Laser first')
        
    def readMinWavelengthExtendUV(self):             
                
        if self.hasFoundLaser:
        
            result, resultdata = registerReadU16(self.laserCOM, 16, 0x33, 0)
            
            return (resultdata/10)  
        
        else:
        
            return ('Please connect to Laser first')
        
    def readMaxWavelengthExtendUV(self):             
                
        if self.hasFoundLaser:
        
            result, resultdata = registerReadU16(self.laserCOM, 16, 0x32, 0)
            
            return (resultdata/10)  
        
        else:
        
            return ('Please connect to Laser first')
          
    
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    ExtremeDriver = ExtremeDriver()
    
    #ExtremeDriver.equipmentScanAndConnect()
    
    ExtremeDriver.hasFoundLaser = True
    ExtremeDriver.laserCOM = 'COM12'
    
    #if ExtremeDriver.laserIsOn() == False:
    
        #print(ExtremeDriver.switchOnLaser())
    
        #print(ExtremeDriver.writePower(26))
    
        #print(ExtremeDriver.readPower())
        
        #print(ExtremeDriver.readRepRate())
        
        #print(ExtremeDriver.writeRepRate(1))
        
        #print(ExtremeDriver.readWavelengthExtendUV())
        
        #ExtremeDriver.setWavelengthExtendUV(360.0)
    
        #time.sleep(5)
    
        #print(ExtremeDriver.switchOffLaser())
        
    #else:
        
        #print(ExtremeDriver.switchOffLaser())
    
    print(ExtremeDriver.writePower(50))
    
    print(ExtremeDriver.readPower())
    
    ExtremeDriver.disconnect()
        
    sys.exit(app.exec_())