# Author: Florian Le Roux
# -*- coding: utf-8 -*-
# This version is a plugin to use with the OneO interface,
# It does not stand alone.

from ctypes import *
import tempfile
import re
import math
import time
import sys
import NpStageDriver
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

## Make sure the Port is correct, COM11 is used here##

class NPstagePluginWorker(QObject): 
    
    def __init__(self):
    
        super().__init__()    
    
    StageDriver = []
    
    sig_success = pyqtSignal()  # switch status of the status button from red to green
    sig_msg = pyqtSignal(str)  # message to be shown to user
    sig_positions = pyqtSignal(float,float,float) #send positions X, Y, Z in this order
    sig_positionsPreciseMove = pyqtSignal(float,float,float) #send positions X, Y, Z in this order for mapper precise move
    sig_preciseSuccess = pyqtSignal() #send success signal if the preciseMove is a success
    sig_disconnection = pyqtSignal()
    
    def __init__(self):
        
        super().__init__()

    @pyqtSlot()
    def connection(self):  
                       
        thread_name = QThread.currentThread().objectName()
        thread_id = str(QThread.currentThreadId())  # cast to str is necessary
        self.sig_msg.emit('Running Nano Stage worker {} from thread {}'.format(thread_name, thread_id))
               
        self.StageDriver = NpStageDriver.NpStageDriver(port = "COM11") 
        
        self.sig_msg.emit('Successful connection to the Stage')
        self.sig_success.emit()        
        
        while 1:
            
            QCoreApplication.processEvents()
            self.readPositions()     
            
    @pyqtSlot()    
    def disconnectFromEquipment(self):

        self.sig_msg.emit('Attempting disconnection from equipment.')
        
        if self.StageDriver != []:
            
            self.StageDriver.close()
            
            self.sig_disconnection.emit()

        else:
            
            self.sig_msg.emit('Not connected to equipment.')
                   
    @pyqtSlot()
    def initialTest(self):
        
        self.moveToSafePosition()
        
        self.moveTo(self.__id, 45)
        
        self.moveToSafePosition()
        
            
    @pyqtSlot(float,float,float)
    def moveTo(self,X:float,Y:float,Z:float):
        
        if self.StageDriver != []:
        
            self.StageDriver.moveto_X(math.ceil(X*1000)/1000)
            self.StageDriver.moveto_Y(math.ceil(Y*1000)/1000)
            self.StageDriver.moveto_Z(math.ceil(Z*1000)/1000)
            
            self.sig_msg.emit('Moving to X: {} um, Y: {} um, Z: {} um' .format(str(round(X,6)),str(round(Y,6)),str(round(Z,6))))
   
    @pyqtSlot(float,float,float)
    def preciseMove(self,X:float,Y:float,Z:float):
        
        #preciseMove is slow and intended to be move with Scanning applications. It will first perform a MOVEX/MOVEY/MOVEZ action
        #which should get the user approximately 100nm away from the desired location. It will then perform MOVRX/MOVRY/MOVZ actions
        #until the precisions is below 10 nm.
        
        self.sig_msg.emit('Precise Move to X: {} um, Y: {} um, Z: {} um' .format(str(round(X,6)),str(round(Y,6)),str(round(Z,6)))) 
                
        if self.StageDriver != []:
            
            self.moveTo(X,Y,Z)
            
            #give the adequate time to the stage to perform the first move
            
            time.sleep(2)
            
            self.StageDriver.moveto_X(math.ceil(X*1000)/1000)
            self.StageDriver.moveto_Y(math.ceil(Y*1000)/1000)
            self.StageDriver.moveto_Z(math.ceil(Z*1000)/1000)  
            
            #corrects the deviation obtained following the MOVEX/Y/Z operation using MOVRX/Y/Z operations
            
            self.correctDeviation(X,Y,Z)
            
            self.readPositionsPreciseMove()
            
    def correctDeviation(self,X,Y,Z):
        
        MX, MY, MZ = self.readPositionsWithNoEmission()
        
        print(MX,MY,MZ)
        
        if (abs(X-MX) > 0.010) or (abs(Y-MY) > 0.010) or (abs(Z-MZ) > 0.010):
            
            print('Correcting X')
            print(X)
            print(MX)
            print(X-MX)
            
            print('Correcting Y')
            print(Y)
            print(MY)            
            print(Y-MY)
            
            print('Correcting Z')
            print(Z)
            print(MZ)             
            print(Z-MZ)
            
            self.StageDriver.moverel_X(math.ceil((X-MX)*1000)/1000)
            self.StageDriver.moverel_Y(math.ceil((Y-MY)*1000)/1000)
            self.StageDriver.moverel_Z(math.ceil((Z-MZ)*1000)/1000)
            
            time.sleep(1)
            
            self.correctDeviation(X, Y, Z)
                
        else:
            
            return
            
    def readPositionsWithNoEmission(self):
        
        return self.StageDriver.get_X(), self.StageDriver.get_Y(), self.StageDriver.get_Z()
                
    @pyqtSlot()   
    def readPositions(self):
        
        X, Y, Z = self.StageDriver.get_X(), self.StageDriver.get_Y(), self.StageDriver.get_Z()
        
        self.sig_positions.emit(X,Y,Z)      
        
    @pyqtSlot()   
    def readPositionsPreciseMove(self):
        
        X, Y, Z = self.StageDriver.get_X(), self.StageDriver.get_Y(), self.StageDriver.get_Z()
        
        self.sig_positionsPreciseMove.emit(X,Y,Z)  

        
class NPstagePluginQThread(QThread):
    
    sigAskForPositions = pyqtSignal()  

    def __init__(self):
    
        super().__init__()
   
   
   