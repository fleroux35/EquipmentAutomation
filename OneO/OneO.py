# Author: Florian Le Roux
# -*- coding: utf-8 -*-

from ctypes import *
import tempfile
import re
import math
import time
import sys
import inputs
import os

import datetime

print('Loading Dependencies, Comment Out The Thorlabs Stage Features for better software performances.')
import OneOGUI

#Thorlabs Stage Plugin
#import ThorlabStagePlugin as tsp / will only be needed when threading works

import thorlabs_apt as apt # Comment Out This Line To Speed Up 

#Nanopositioning Stage Plugin
import NpPlugin as nps

#Extreme Laser/Extend UV Plugin
import ExtremePlugin as el

#Spectrometer/CCD Plugin
import LightFieldPlugin as sccd
import Spectrometry

#Map Pop Ups
import promptSavePopUp
import ConfirmMapStartPopUp
import MapPopUp

#Data Handler
from DataHandlers import mapDataHandler
from DataMapper import dataMapper

#Map Class
import Mapper
import ImageDisplayer as imd
from PIL import ImageQt, Image
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QDockWidget, QWidget, QPushButton
from PyQt5.QtGui import QPixmap


class GUI(OneOGUI.mainGUI):
    
    ## Signals definitions for Qt threading ## 
    
    #Thorlabs Stage signals
    sig_askForThorMove = pyqtSignal(float)
    ThorStageSerial = 27504894
    
    #Nanopositioning Stage signals
    
    sig_disconnectNPStage = pyqtSignal()     
    sig_askForMove = pyqtSignal(float,float,float)  
    
    #Extreme Laser/ Extend UV signals   
    
    sig_turnLaserOnOff = pyqtSignal(int)  
    sig_requestLaserEmissionstatus = pyqtSignal()    
    sig_LaserPower = pyqtSignal(float)
    sig_Laserwvl = pyqtSignal(float)    
    sig_LaserRepRate = pyqtSignal(int)    
          
    #Spectrometer/CCD signals
    
    sig_disconnectSpectrometer = pyqtSignal()
    sig_setSaveExportFolder = pyqtSignal(str)
    
    #Map signals
    
    sig_previewProgress = pyqtSignal(float)
    
    def __init__(self,MainWindow):
        
        #Take GUI and initialize threads use.
        
        super().__init__(MainWindow)
        
        self.MainWindow = MainWindow
        self.__threads = []
        self.Log = MainWindow.findChild(QTextEdit,"Log")            
        self.setupGamepad()    
        self.setupConnections()
        
        #Thorlab Stage Booleans
        self.ThorThreadIsStarted = False
        self.isConnectedToThorStage = False
        self.isConnectedToThorStageUpdatePosition = False
        
        #Nanopositioning Stage Booleans 
        self.ThreadIsStarted = False    
        self.isConnectedToStage = False   
        self.HasAskedForDisconnection = False 
        self.StagehasAlreadyRanOnce = False
        self.isConnectedupdatePosition = False  

        #Extreme Laser/Extend UV Booleans
        self.isLaserConnected = False       
        self.IsLaserOn = True   
        
        #Spectrometer/CCD Booleans
        self.isSpectrometerConnected = False
        
    def setupGamepad(self):
        
        #gamepad Controls
        
        gamepad_Thread = GamepadSthread()
        gamepad_Thread.setObjectName('thread_gamepad') 
        self.gamepadThreadName = gamepad_Thread.objectName
        Gamepad_worker = Gamepad()
        Gamepad_worker.moveToThread(gamepad_Thread)
        gamepad_Thread.started.connect(Gamepad_worker.listeningToCommands) 
        gamepad_Thread.finished.connect(self.emptyThreads)
        
        gamepad_Thread.start()
        
        Gamepad_worker.sig_msg.connect(self.react)
        Gamepad_worker.sig_move.connect(self.moveFromGamepad)
        Gamepad_worker.sigConnect.connect(self.attemptPiezoStageConnection)
        
        self.__threads.append((gamepad_Thread, Gamepad_worker))        


    def setupConnections(self):
        
        # NanoPositioning Stage Connections
             
        self.cnectNpStageButton.clicked.connect(self.attemptPiezoStageConnection)
        self.goToZeroPushButton.clicked.connect(self.goToZero)       
        self.goToCentrePushButton.clicked.connect(self.goToCentre)        
        self.goToPushButton.clicked.connect(self.goTo)
        
        # Thorlabs Stage Connection (when threading will be available)
        
        self.cnectThorButton.clicked.connect(self.attemptThorConnection)
        self.updtThorButton.clicked.connect(self.updatePosThor)
        self.goThorButton.clicked.connect(self.goToThor)
        
        # Laser Connections
        
        self.cnectLaserButton.clicked.connect(self.attemptLaserConnection)
        self.LaserPowerButton.clicked.connect(self.turnLaserOnOff)
        self.LaserApplyButton.clicked.connect(self.setLaserWvlFromPrompt)
        self.LaserApplyButton.clicked.connect(self.setLaserPowerFromPrompt)
        self.LaserApplyButton.clicked.connect(self.setLaserRepRateFromPrompt) 
        
        # Spectrometer CCD Connections
        
        self.cnectSpectroButton.clicked.connect(self.attemptSpectrometerConnection)
        
        # Map acquisition
        # Map acquisition is left on the main thread as the measurement should not be
        # interrupted by other moves made on the same GUI
        
        self.mapButton.clicked.connect(self.enterMapAcquisitionMode)
        
    def attemptThorConnection(self):
        
        #As is the library does not support threading, it will run on main
        #if self.isConnectedToThorStage == False:
                  
            ##initialize connection

            #thorThread = tsp.ThorlabStagePluginQThread()
            #thorThread.setObjectName('thorThread') 
            #self.thorThreadName = thorThread.objectName
            
            #thorWorker = tsp.ThorlabStagePluginWorker()
            #thorWorker.moveToThread(thorThread)
            
            #thorThread.started.connect(thorWorker.connection) 
            #thorThread.start()
                
            #thorWorker.sig_msg.connect(self.react)
            #thorWorker.sig_position.connect(self.updatePositionThorReceivingMessage)
            #thorWorker.sig_success.connect(self.connectedToThorStage)
                                                
            #self.__threads.append((thorThread, thorWorker))
                                            
            #self.sig_askForThorMove.connect(thorWorker.moveTo) 
            
        #else:
            
            #self.Log.append('Already Connected to Thorlabs Stage.')
        
        self.ThorStage = apt.Motor(self.ThorStageSerial)
        self.ThorPosLCD.display(self.ThorStage.position)
        self.connectedToThorStage()
        
    def attemptPiezoStageConnection(self):
        
        if self.isConnectedToStage == False:
                  
            #initialize connection

            nps_position_Thread = nps.NPstagePluginQThread()
            nps_position_Thread.setObjectName('NPstageThread') 
            self.npsThreadName = nps_position_Thread.objectName
            
            nps_position_worker = nps.NPstagePluginWorker()
            nps_position_worker.moveToThread(nps_position_Thread)
            
            nps_position_Thread.started.connect(nps_position_worker.connection) 
            nps_position_Thread.start()
                
            nps_position_worker.sig_msg.connect(self.react)
            nps_position_worker.sig_positions.connect(self.updatePositionReceivingMessage)
            nps_position_worker.sig_success.connect(self.connectedToNPStage)
            nps_position_worker.sig_disconnection.connect(self.mainDisconnection)
                                                
            self.__threads.append((nps_position_Thread, nps_position_worker))
                                                
            self.sig_disconnectNPStage.connect(nps_position_worker.disconnectFromEquipment)
            self.sig_askForMove.connect(nps_position_worker.moveTo) 
            
             
    def attemptLaserConnection(self):
        
        #this method finds all relevant equipment (laser/monochromators)
        #on the different ports.

        if self.isLaserConnected == False:

            laser_thread = QThread()
            laser_thread.setObjectName('laser_thread') 
            self.laserThreadName = laser_thread.objectName
            laser_worker = el.LaserWorker()
            laser_worker.moveToThread(laser_thread)
            laser_thread.started.connect(laser_worker.equipmentScanAndConnect) 

            laser_worker.sigcnection.connect(self.connectedToLaser)
                         
            self.sig_requestLaserEmissionstatus.connect(laser_worker.emissionStatus)
            laser_worker.sig_status.connect(self.isLaserOnOff)
            
            self.sig_turnLaserOnOff.connect(laser_worker.turnLaserOnOff)
            
            laser_worker.sigpower.connect(self.updatePower)
            laser_worker.sigreprate.connect(self.updateRepRate)
            laser_worker.sigwvl.connect(self.updateWvl)
            
            self.sig_LaserPower.connect(laser_worker.setPower)
            self.sig_Laserwvl.connect(laser_worker.setWvl)
            self.sig_LaserRepRate.connect(laser_worker.setRepRate)
            
            laser_worker.sigmsg.connect(self.react)
                               
            laser_thread.start()                           
            self.__threads.append((laser_thread, laser_worker))
            
    def attemptSpectrometerConnection(self):
        
        self.react('Attempting connection to Spectrometer/CCD.')   
         
        if self.isSpectrometerConnected == False:

            spectro_thread = QThread()
            spectro_thread.setObjectName('spectro_thread') 
            self.spectroThreadName = spectro_thread.objectName
            
            spccdPlugin = sccd.LFPlugin()
            spccdPlugin.moveToThread(spectro_thread)
            
            spectro_thread.started.connect(spccdPlugin.equipmentScanAndConnect) 

            spccdPlugin.sigcnection.connect(self.connectedToSpectrometer)
            
            self.sig_disconnectSpectrometer.connect(spccdPlugin.close)
            #self.sig_setSaveExportFolder.connect(spccdPlugin.setSaveExportFolder)
            
            spccdPlugin.sig_msg.connect(self.react)
                               
            spectro_thread.start()                           
            self.__threads.append((spectro_thread, spccdPlugin)) 
            
            self.sig_setSaveExportFolder.emit('C://Users//leroux//Desktop')
            
    def enterMapAcquisitionMode(self):
        
        #this is where the mapper receives his first information about work to come
        #for now the mapper is not yet in a new thread as its execution is not confirmed
        #it can therefore directly share its information with the main thread
        
        self.mapper = Mapper.mapper(self.XCentrePromptmap.toPlainText(), self.YCentrePromptmap.toPlainText(), self.XLengthPromptmap.toPlainText(), self.YLengthPromptmap.toPlainText(), self.XStepPromptmap.toPlainText(), self.YStepPromptmap.toPlainText(),self.zPosLCD.value())
        
        #the mapper then transmits the estimation to the pop up awaiting confirmation
        
        self.confirmMapStartPopUp = ConfirmMapStartPopUp.confirmMapStartPopUp()
        
        self.fillConfirmMapStartPopUp()
        
        self.confirmMapStartPopUp.show()
        
        self.confirmMapStartPopUp.ConfirmAcquisition.clicked.connect(self.whereToSave)
                
    def whereToSave(self):
        
        self.whereToSavePopUp = promptSavePopUp.promptPopUp()
        
        self.whereToSavePopUp.savePathButton.clicked.connect(self.rawfolderCreation)
        
    def rawfolderCreation(self):
        
        if not os.path.exists(self.whereToSavePopUp.pathToFolderPrompt.toPlainText()):
            
            os.mkdir(self.whereToSavePopUp.pathToFolderPrompt.toPlainText())
            
            os.mkdir(self.whereToSavePopUp.pathToFolderPrompt.toPlainText()+'\Raw')

            self.acquisitionFolder = self.whereToSavePopUp.pathToFolderPrompt.toPlainText()+'\Raw'
            
            self.whereToSavePopUp.pathToFolderPrompt.setText("Directory created.")
            
            self.whereToSavePopUp.close()
                    
            self.confirmedAcquisitionExecution()
            
            return
            
        else: 
            
            self.whereToSavePopUp.pathToFolderPrompt.setText("Directory already exists.")
            
            os.mkdir(self.whereToSavePopUp.pathToFolderPrompt.toPlainText()+'\Raw')
            
            self.acquisitionFolder = self.whereToSavePopUp.pathToFolderPrompt.toPlainText()+'\Raw'
            
            self.whereToSavePopUp.close()
            
            self.confirmedAcquisitionExecution()
            
            return     
        
    def fillConfirmMapStartPopUp(self):
        
        self.confirmMapStartPopUp.NumberOfStepsValueLabel.setText('{} steps'.format(self.mapper.numberOfSteps))
        
        self.totalNumberOfMapSteps = self.mapper.numberOfSteps
             
        estimatedTime = str(datetime.timedelta(seconds=self.mapper.estimatedTime))
        
        self.estimatedMapTime = self.mapper.estimatedTime
        
        finishTime = str(datetime.datetime.now() + datetime.timedelta(seconds=self.estimatedMapTime))
        
        self.estimatedMapFinishTime = finishTime
        
        self.confirmMapStartPopUp.EstimatedAcTimeValueLabel.setText(estimatedTime) 
        
        self.confirmMapStartPopUp.finishTimeValueLabel.setText(finishTime)      
        
    def confirmedAcquisitionExecution(self):
        
        self.react('Acquisition has been confirmed, opening acquisition pop up.')
        
        #self.MainWindow.hide()
        
        self.confirmMapStartPopUp.close()
        
        #at this point the main GUI is hidden to prevent the user from disturbing the acquisition
        
        self.mapacquisitionPopUp = MapPopUp.mapPopUp()
        
        self.mapacquisitionPopUp.show()
        
        #the mapper is added to a new QThread, destroyed at the end of the execution of the map
        #this triggers the map acquisition
        
        self.triggerMapThreads()
        
        self.initializeMapPopUp()
        
    def triggerMapThreads(self):
  
        mapper_thread = QThread()
        mapper_thread.setObjectName('mapper_thread') 
        
        #this is where the mapper is disconnected from the main thread
        mapper = self.mapper  
        self.mapper = []
        
        #and connected to the mapper thread
        mapper.moveToThread(mapper_thread)       
        mapper_thread.started.connect(mapper.acquiremap) 
    
        mapper.sig_msg.connect(self.reactMapAc)
        mapper.sig_stepPerformed.connect(self.mapStepHasBeenPerformed)
        mapper.sig_time.connect(self.mapupdateEstimate)
        
        #this thread is the data handler thread
        
        datahandler_thread = QThread()
        datahandler_thread.setObjectName('data_handler_thread')
        self.datahandlerThreadName = datahandler_thread.objectName
        
        #the data handler is connected to its own thread and work on the computer
        #side to handle all the data collection
        
        datahandler = mapDataHandler(self.acquisitionFolder)
        datahandler.moveToThread(datahandler_thread)
        
        datahandler.sig_msg.connect(self.reactMapAc)
        mapper.sig_Spectrum.connect(datahandler.saveLastSpectrum)
        
        #this thread is dedicated to making the progress map
        
        progressmapper_thread = QThread()
        progressmapper_thread.setObjectName('progressmapper_thread') 
        
        progressmapper = imd.QImageMaker()
        
        #and connected to the progressmapper thread
        
        progressmapper.moveToThread(progressmapper_thread) 
    
        progressmapper.sig_image.connect(self.updateProgressImage)
    
        mapper.sig_requestImgProgress.connect(progressmapper.makeProgressImage)
        mapper.sig_requestFinProgress.connect(progressmapper.greenDefault)
        
        #this thread is dedicated to making the preview map
        
        previewmapper_thread = QThread()
        previewmapper_thread.setObjectName('previewmapper_thread') 
        
        previewmapper = dataMapper(mapper, self.acquisitionFolder)
        
        #and connected to the previewmapper thread
        
        previewmapper.moveToThread(previewmapper_thread) 
        
        previewmapper_thread.started.connect(previewmapper.firstConnection)
        
        datahandler.sig_askForNorm.connect(previewmapper.normalizeFile)
    
        previewmapper.sig_image.connect(self.updateMapImage)
        
        self.sig_previewProgress.connect(previewmapper.makePreviewImage)
        
        self.mapacquisitionPopUp.updatePreviewBtn.clicked.connect(self.askForMapImage)
        
        #this thread connects the last recorded spectrum to the spectrum plot
        #and to the data handler
        
        for thread, worker in self.__threads:
            
            if thread.objectName == self.spectroThreadName:

                worker.sig_spectrum.connect(self.updateSpectrumPlot)
                worker.sig_spectrum.connect(mapper.spectrumReceived)       
                worker.sig_msg.connect(self.reactMapAc)   
                
                mapper.sig_requestSpectrum.connect(worker.recordSpectrum)  
                               
            if thread.objectName == self.npsThreadName:
                
                worker.sig_positionsPreciseMove.connect(mapper.positionsReceived)
                
                #the mapper uses Precise Move for its movement to get more accuracy, it is slower
                mapper.sig_askForMove.connect(worker.preciseMove)
                
        #All the threads are then started
        
        datahandler_thread.start()
        self.__threads.append((datahandler_thread, datahandler))
        
        progressmapper_thread.start()
        self.__threads.append((progressmapper_thread, progressmapper))
        
        previewmapper_thread.start()
        self.__threads.append((previewmapper_thread, previewmapper))
                           
        mapper_thread.start()                           
        self.__threads.append((mapper_thread, mapper))    
        
    def initializeMapPopUp(self):
        
        self.progressPercentage = 0
        
        self.progressSteps = 0
        
        self.currentX = 0
        
        self.currentY = 0
        
        self.currentDirection = 1
        
        self.mapacquisitionPopUp.Log.append('Starting Map Acquisition, please do not touch the controller while the acquisition is running.')
        
        #this should initialize the values on the pop up given that it is faster than the first step
        
        self.finishTime = (datetime.datetime.now() + datetime.timedelta(seconds=self.estimatedMapTime))
            
        self.mapacquisitionPopUp.finishTimeValueLabel.setText(str(self.finishTime))
            
        self.mapacquisitionPopUp.remainingTimeValueLabel.setText(str(self.finishTime - datetime.datetime.now()))
            
        self.mapacquisitionPopUp.progressValueLabel.setText('{}%, {} steps out of {}\n \n steps have been performed'.format(round(self.progressPercentage,1), self.progressSteps, self.totalNumberOfMapSteps))    
    
    @pyqtSlot(float)
        
    def mapupdateEstimate(self, estimatedTime:float):
        
        self.estimatedMapTime = estimatedTime
        
        self.finishTime = (datetime.datetime.now() + datetime.timedelta(seconds=self.estimatedMapTime))
        
        self.mapacquisitionPopUp.finishTimeValueLabel.setText(str(self.finishTime))
        
        self.mapacquisitionPopUp.remainingTimeValueLabel.setText(str(self.finishTime - datetime.datetime.now()))
        
    @pyqtSlot(int)
        
    def mapStepHasBeenPerformed(self, currentStep:int):
        
        self.progressPercentage = (currentStep/self.totalNumberOfMapSteps)*100 
            
        self.mapacquisitionPopUp.progressValueLabel.setText('{}%, {} steps out of {}\n \nsteps have been performed'.format(round(self.progressPercentage,1), currentStep, self.totalNumberOfMapSteps))   

    @pyqtSlot(ImageQt.ImageQt)
    
    def updateProgressImage(self, progressimg: ImageQt.ImageQt):
           
        self.mapacquisitionPopUp.progressSlot.updateImage(progressimg)
        self.mapacquisitionPopUp.show()
    
    @pyqtSlot(Spectrometry.Spectrum)
    
    def updateSpectrumPlot(self, lastSpectrum: Spectrometry.Spectrum):
        
        self.mapacquisitionPopUp.static_canvas.figure.clf() 
        self.mapacquisitionPopUp.static_canvas.figure.subplots().plot(lastSpectrum.wvl, lastSpectrum.inte, ".")  
        self.mapacquisitionPopUp.static_canvas.draw()
        
    @pyqtSlot(ImageQt.ImageQt)
    
    def updateMapImage(self, mapimg: ImageQt.ImageQt):
           
        self.mapacquisitionPopUp.mapSlot.updateImage(mapimg)
        self.mapacquisitionPopUp.show() 
        
    def askForMapImage(self):
        
        self.sig_previewProgress.emit(float(self.mapacquisitionPopUp.wvlPrompt.toPlainText()))
        
    @pyqtSlot(str)   
    
    def react(self,string: str):
        
        self.Log.append(string)
        
    @pyqtSlot(str)   
    def reactMapAc(self,string: str):
        
        self.mapacquisitionPopUp.Log.append(string) 
        
 #Thorlabs stage methods
    
    @pyqtSlot()
    def connectedToThorStage(self):
        
        self.isConnectedToThorStage = True
        self.isConnectedToThorStageUpdatePosition = True
        
        self.cnectThorButton.setText("Connected")  
        self.cnectThorButtonLabel.setPixmap(QPixmap(":/GreenButton.png"))
        
 #Nanopositioning stage methods   
 
    @pyqtSlot()   
    def connectedToNPStage(self):
        
        self.isConnectedToStage = True   
        self.isConnectedupdatePosition = True
        
        #upon Connection the stage is asked to move to the center position
        
        self.moveTo(100, 100, 25)
        
        self.cnectNpStageButton.setText("Disconnect")
        self.cnectNpStageButton.clicked.disconnect()
        self.cnectNpStageButton.clicked.connect(self.disconnectFromEquipment)
        
        padThread, padWorker = self.__threads[0]
        padWorker.sigConnect.disconnect()
        padWorker.sigConnect.connect(self.disconnectFromEquipment)

    @pyqtSlot()        
    def disconnectFromEquipment(self):
        
        self.sig_disconnectNPStage.emit()  
        
        
    @pyqtSlot()                 
    def mainDisconnection(self):
        
        connectionThread, connectionWorker = self.__threads[1]
             
        connectionThread.quit()
        
        gamepadThread, gamepad = self.__threads[0]
        
        gamepadThread.quit()
        
    @pyqtSlot() 
    
    def emptyThreads(self):
        
        if self.howManyThreadHaveStopped == 0:
            
            self.howManyThreadHaveStopped = 1
                
        else:
        
            self.__threads = []  
            
            self.howManyThreadHaveStopped = 0
        
            self.succesfullDisconnection()
    
        
    @pyqtSlot()     
    
    def succesfullDisconnection(self):    
         
        self.statusButton.setPixmap(QPixmap(":/RedButton.png"))
        self.isLaserConnected = False
        
        self.xPosLCD.display(0)
        self.yPosLCD.display(0)
        self.zPosLCD.display(0)

        self.Log.append("Succesful Disconnection")
        
        self.hasAlreadyRanOnce = True
        
        self.cnectButton.setText("Connect")  
        
        self.cnectButton.clicked.disconnect()
        self.cnectButton.clicked.connect(self.attemptConnection)          
            
    @pyqtSlot(float, float, float)
    
    #in order X, Y, Z
    
    def updatePositionReceivingMessage(self, X:float, Y:float, Z:float):  
        
        self.xPosLCD.display(X)
            
        self.yPosLCD.display(Y)
            
        self.zPosLCD.display(Z)
        
        self.statusButton.setPixmap(QPixmap(":/GreenButton.png"))
        
    def updatePositionThorReceivingMessage(Pos: float):
        
        self.ThorPosLCD.display(Pos)  

            
    @pyqtSlot(str)
    def moveFromGamepad(self, direction:str):
        
        currentX = self.xPosLCD.value()
        currentY = self.yPosLCD.value()
        currentZ = self.zPosLCD.value()
        
        if direction == 'U':
            
            self.moveTo(currentX ,currentY + float(self.YStepPrompt.toPlainText()), currentZ)
            
        if direction == 'D':
                
            self.moveTo(currentX ,currentY - float(self.YStepPrompt.toPlainText()), currentZ)
            
        if direction == 'R':
                        
            self.moveTo(currentX + float(self.XStepPrompt.toPlainText()) ,currentY, currentZ)  
            
        if direction == 'L':
                            
            self.moveTo(currentX - float(self.XStepPrompt.toPlainText()) ,currentY, currentZ) 
            
        if direction == 'Low':
            
            self.moveTo(currentX, currentY, currentZ - float(self.ZStepPrompt.toPlainText()))
            
        if direction == 'High':
                
            self.moveTo(currentX, currentY, currentZ + float(self.ZStepPrompt.toPlainText()))        
                   
            
    def moveTo(self, X, Y, Z):
        
        if self.isConnectedToStage:
            
            self.sig_askForMove.emit(X,Y,Z)
                
    def goToZero(self):
        
        self.moveTo(0,0,25)
        
    def goToCentre(self):
    
        self.moveTo(100,100,25)
        
    def goTo(self):
        
        self.moveTo(float(self.goToXPrompt.toPlainText()),float(self.goToYPrompt.toPlainText()),float(self.goToZPrompt.toPlainText()))
 
  #Thorlabs Stage method
  
    def goToThor(self):

        self.ThorStage.move_to(float(self.goToThorPrompt.toPlainText()))
        self.ThorPosLCD.display(float(self.goToThorPrompt.toPlainText()))
        
    def updatePosThor(self):
        
        self.ThorPosLCD.display(self.ThorStage.position)
  
  #Laser methods   
  
    @pyqtSlot(bool)   
    def connectedToLaser(self, status:bool):
        
        self.checkEmissionStatus()
        
        if status == True:
        
            self.isLaserConnected = True   
            self.isConnectedupdatePosition = True
        
            self.cnectLaserButton.setText("Disconnect")
        
            self.cnectLaserStatusButton.setPixmap(QPixmap(":/OrangeButton.png"))
            #self.cnectLaserStatusButton.clicked.disconnect()
            #self.cnectLaserStatusButton.clicked.connect(self.disconnectFromEquipment)
            
            self.react('Connection to laser Successful')
            
    def checkEmissionStatus(self):
        
        self.sig_requestLaserEmissionstatus.emit()
        
    @pyqtSlot(bool) 
            
    def isLaserOnOff(self, emissionStatus:bool):  
    
        if emissionStatus:
            
            self.IsLaserOn = True
            
            self.LaserPowerButton.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(0, 255, 0);")
            
            self.cnectLaserStatusButton.setPixmap(QPixmap(":/GreenButton.png"))               
            
        else:
            
            self.IsLaserOn = False
            
            self.LaserPowerButton.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 0, 0);") 
            
            self.cnectLaserStatusButton.setPixmap(QPixmap(":/OrangeButton.png"))     
    
    @pyqtSlot()      
    def turnLaserOnOff(self):        
        
        if self.IsLaserOn:
            
            #turn laser off
            
            self.sig_turnLaserOnOff.emit(0)
            
        else:
            
            #turn laser on
    
            self.sig_turnLaserOnOff.emit(1)
            
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
    def setLaserWvlFromPrompt(self):
        
        self.sig_Laserwvl.emit(float(self.wavelengthPrompt.toPlainText()))

    @pyqtSlot() 
    def setLaserRepRateFromPrompt(self):
        
        self.sig_LaserRepRate.emit(float(self.frequencyPrompt.toPlainText()))        
    
        
    @pyqtSlot() 
    def setLaserPowerFromPrompt(self):
        
        self.sig_LaserPower.emit(float(self.powerPrompt.toPlainText()))    
        
    #Spectro methods   
    
    @pyqtSlot(bool)   
    def connectedToSpectrometer(self, status:bool):
        
        if status == True:
        
            self.isConnectedToSpectrometer = True   
        
            self.cnectSpectroButton.setText("Disconnect")
        
            self.spectroButton.setPixmap(QPixmap(":/GreenButton.png"))
            
            self.cnectSpectroButton.clicked.disconnect()
            self.cnectSpectroButton.clicked.connect(self.disconnectFromSpectrometer)
            
            self.react('Connection to Spectrometer/CCD Successful')
            
    @pyqtSlot(bool)   
    def disconnectFromSpectrometer(self):       
        
        if self.isConnectedToSpectrometer == True:
            
            self.sig_disconnectSpectrometer.emit()
        
        
class GamepadSthread(QThread):
    
    def __init__(self):
        
        super().__init__()
        
class Gamepad(QObject):
    
    sig_msg = pyqtSignal(str)
    
    sig_move = pyqtSignal(str)
    
    sigConnect = pyqtSignal()

    def __init__(self):
        
        super().__init__()
        
        self.sig_msg.emit('gamepad started')
        
    def listeningToCommands(self):
        
        while 1:
            events = inputs.get_gamepad()
            
            for event in events:
                
                if event.code == 'ABS_HAT0X' and event.state == 1:
                    
                    self.sig_move.emit('R')
                    
                if event.code == 'ABS_HAT0Y' and event.state == -1:
                    
                    self.sig_move.emit('U')
                    
                if event.code == 'ABS_HAT0X' and event.state == -1:
                        
                    self.sig_move.emit('L')
                        
                if event.code == 'ABS_HAT0Y' and event.state == 1:
                        
                    self.sig_move.emit('D')
                    
                if event.code == 'BTN_TL'and event.state == 1:
                    
                    self.sig_move.emit('Low')
                    
                if event.code == 'BTN_TR'and event.state == 1:
                    
                    self.sig_move.emit('High')
                    
                if event.code == 'BTN_SELECT' and event.state == 1:
                    
                    self.sigConnect.emit()
   
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    NpGui = QMainWindow()
    ui = GUI(NpGui)
    NpGui.show()
    
    sys.exit(app.exec_())
    
   
   