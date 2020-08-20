# Author: Florian Le Roux
# -*- coding: utf-8 -*-

from ctypes import *
import tempfile
import re
import math
import time
import sys
import UI_RsGUI
import FreeMovePopUp
import ReflectionPopUp
import RsDriver
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QLabel


class ConnectionWorker(QObject):
    
    identifierTop = 'Top Arm'
    identifierBt = 'Bottom Arm'
    
    StageDriver = []
    
    sig_success = pyqtSignal(str)  # switch status of the status button from red to green
    sig_msg = pyqtSignal(str)  # message to be shown to user
    sig_stepsangles = pyqtSignal(str,float,float)
    sig_disconnection = pyqtSignal(str)
    
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
            
            
    @pyqtSlot()    
    def disconnectFromEquipment(self):

        self.sig_msg.emit('Attempting disconnection from equipment.')
        
        if self.StageDriver != []:
            
            self.StageDriver.terminateConnection()
           
            if self.__id == self.identifierTop:
               
                self.sig_msg.emit('Top Arm is disconnected')
                self.sig_disconnection.emit(self.__id)
                
            if self.__id == self.identifierBt:
            
                self.sig_msg.emit('Bottom Arm is disconnected')
                self.sig_disconnection.emit(self.__id)
           
        else:
            
            self.sig_msg.emit('Not connected to equipment.')
                   
    @pyqtSlot()
    
    def initialTest(self):
        
        self.moveToSafePosition()
        
        self.moveTo(self.__id, 45)
        
        self.moveToSafePosition()
        
    def moveToSafePosition(self):
        
        if self.StageDriver != []:
        
            self.StageDriver.moveToSafePosition()
            
            self.sig_msg.emit('{} in safe position' .format(self.__id) )
            
        self.readAngles()
            
    @pyqtSlot(str,float)
    def moveTo(self, id:str, angle:float):
        
        if self.__id == id:
        
            if self.StageDriver != []:
            
                result = self.StageDriver.moveTo(angle)
            
                if result != 'OK':
                
                    self.sig_msg.emit(result)
            
                else:
                
                    self.sig_msg.emit('{} moved to {}°' .format(self.__id,str(round(angle,3))))
        
                    self.readAngles()
       
    def readAngles(self):
        
        step, ustep = self.StageDriver.getPositions()
        
        self.StageDriver.getCurrentAngleRelativeToNormal()
        
        currentAngle = round(self.StageDriver.currentAngle,3)
        
        self.sig_stepsangles.emit(self.__id,step,currentAngle)                 
        
class RotatingStageQThread(QThread):
    
    sigInitTest = pyqtSignal()
    sig_finished = pyqtSignal(str)

    def __init__(self, id:str):
    
        super().__init__()
        self.id = id
        
    @pyqtSlot()
    
    def finishedWithId():
    
        sig_finished.emit(self.id)
    
   
   