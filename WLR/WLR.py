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

import WLRGUI

#Thorlabs Stage for Rotating Sample
import thorlabs_apt as apt

#Rotating Stage Plugin and Pop Ups
import RsPlugin as rs
import FreeMovePopUp
import ReflectionPopUp
import AlignmentConfirmation

#Spectrometer/CCD Plugin
import LightFieldPlugin as sccd
import Spectrometry

#Measurement Pop Ups
import promptSavePopUp
import ConfirmMeasStartPopUp
import MeasPopUp
import ReferencePopUp

#Data Handler
from DataHandlers import WLRDataHandler
from DataPreviewer import dataPreviewer

#Map Class
import Acquirer
import ImageDisplayer as imd
from PIL import ImageQt, Image

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QDockWidget, QWidget, QPushButton
from PyQt5.QtGui import QPixmap


class GUI(WLRGUI.mainGUI):
    
    ## Stage serial for rotating the sample
    
    ThorStageSerial = 55113014
    
    ## Signals definitions for Qt threading ## 
    
    #Rotating Stage signals
    
    sigInitTest = pyqtSignal()        
    sig_disconnectRS = pyqtSignal()    
    sig_askForMove = pyqtSignal(str, float)   
    
    #Extreme Laser/ Extend UV signals   
    
    sig_turnLaserOnOff = pyqtSignal(int)  
    sig_requestLaserEmissionstatus = pyqtSignal()    
    sig_LaserPower = pyqtSignal(float)
    sig_Laserwvl = pyqtSignal(float)    
    sig_LaserRepRate = pyqtSignal(int)    
          
    #Spectrometer/CCD signals
    
    sig_disconnectSpectrometer = pyqtSignal()
    
    #Acquisition signals
    
    sig_previewProgress = pyqtSignal(float)
    sigReference = pyqtSignal(bool,str)
    sigReadyforMainAcquisition = pyqtSignal()
    
    def __init__(self,MainWindow):
        
        #Take GUI and initialize threads use.
        
        super().__init__(MainWindow)
        
        self.MainWindow = MainWindow
        self.__threads = []
        self.Log = MainWindow.findChild(QTextEdit,"Log")              
        self.setupConnections()
        
        #Rotating Stage Parameters
        
        self.identifierTop = 'Top Arm'       
        self.identifierBt = 'Bottom Arm'            
        self.hasAlreadyRanOnce = False                
        self.isTopConnected = False
        self.isBottomConnected = False    
        self.freeMovePopUp = None      
        self.ReflectionPopUp = None

        #Extreme Laser/Extend UV Booleans
        self.isLaserConnected = False       
        self.IsLaserOn = True   
        
        #Spectrometer/CCD Booleans
        self.isSpectrometerConnected = False      

    def setupConnections(self):
        
        # Rotating Stage Connections
             
        self.connectRStageButton.clicked.connect(self.attemptRotatingStageConnection)
        self.InitCheckBtn.clicked.connect(self.carryInitialTest)
        self.freeMoveBtn.clicked.connect(self.freeMove)
        self.reflectionBtn.clicked.connect(self.Reflection)
        
        # Laser Connections
        
        self.cnectLaserButton.clicked.connect(self.attemptLaserConnection)
        self.LaserPowerButton.clicked.connect(self.turnLaserOnOff)
        self.LaserApplyButton.clicked.connect(self.setLaserWvlFromPrompt)
        self.LaserApplyButton.clicked.connect(self.setLaserPowerFromPrompt)
        self.LaserApplyButton.clicked.connect(self.setLaserRepRateFromPrompt) 
        
        # Spectrometer CCD Connections
        
        self.cnectSpectroButton.clicked.connect(self.attemptSpectrometerConnection)
        
        # Automatic connection to the Rotation Stage
        
        self.cnectSampleBtn.clicked.connect(self.connectToSampleStage)
        
        # Measurement acquisition
        # Measurement acquisition is left on the main thread as the measurement should not be
        # interrupted by other moves made on the same GUI
        
        self.measButton.clicked.connect(self.enterAcquisitionMode)
        
    def connectToSampleStage(self):
        
        self.sampleRotatingStage = apt.Motor(self.ThorStageSerial)
        self.sampleRotatingStage.set_move_home_parameters(2,1,10,4)        
        self.sampleRotatingStage.set_velocity_parameters(0,10,10)
                       
        self.SampleOrientationLCD.display(self.sampleRotatingStage.position)
        
        self.Log.append('Homing Sample Rotating Stage...')
        self.sampleRotatingStage.move_home()
        
        self.SampleOrientationUpdtBtn.clicked.connect(self.updatePositionSampleStage)
        self.SampleOrientationGoTo.clicked.connect(self.askForRotationSampleStage)
        self.connectedToSampleStage()
        
    def attemptRotatingStageConnection(self):
        
        if self.isTopConnected == False and self.isBottomConnected ==  False:
                  
            #initialize connection on the top thread, perform initial step/angle reading

            top_thread = rs.RotatingStageQThread(self.identifierTop)
            top_connect_worker = rs.ConnectionWorker(self.identifierTop)
            top_thread.setObjectName('toparm_thread') 
            self.topThreadName = top_thread.objectName
            top_connect_worker.moveToThread(top_thread)
            top_thread.started.connect(top_connect_worker.connection) 
            self.sigInitTest.connect(top_connect_worker.initialTest) 
                
            top_thread.start()
                
            top_connect_worker.sig_msg.connect(self.react)
            top_connect_worker.sig_stepsangles.connect(self.updateAnglesAndSteps)
            top_connect_worker.sig_success.connect(self.connectedToEquipment)
            top_connect_worker.sig_disconnection.connect(self.succesfulDisconnection)
    
            top_thread.finished.connect(top_thread.finishedWithId)
                                 
            self.__threads.append((top_thread, top_connect_worker))
    
            #initialize connection on the bottom thread, perform initial step/angle reading 
    
            bt_thread = rs.RotatingStageQThread(self.identifierBt)
            bt_thread.setObjectName('btmarm_thread')          
            self.btThreadName = bt_thread.objectName
            bt_connect_worker = rs.ConnectionWorker(self.identifierBt)
            bt_connect_worker.moveToThread(bt_thread) 
            bt_thread.started.connect(bt_connect_worker.connection) 
            self.sigInitTest.connect(bt_connect_worker.initialTest) 
                
            bt_thread.start()
                
            bt_connect_worker.sig_msg.connect(self.react)
            bt_connect_worker.sig_stepsangles.connect(self.updateAnglesAndSteps)
            bt_connect_worker.sig_success.connect(self.connectedToEquipment)
            bt_connect_worker.sig_disconnection.connect(self.succesfulDisconnection)
    
            bt_thread.finished.connect(bt_thread.finishedWithId)
                
            self.__threads.append((bt_thread, bt_connect_worker))
                
            if self.hasAlreadyRanOnce == False:
                
                self.sig_disconnectRS.connect(top_connect_worker.disconnectFromEquipment)
                self.sig_askForMove.connect(top_connect_worker.moveTo)   
                self.sig_disconnectRS.connect(bt_connect_worker.disconnectFromEquipment)
                self.sig_askForMove.connect(bt_connect_worker.moveTo)      
            
             
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
            
            spccdPlugin.sig_msg.connect(self.react)
                               
            spectro_thread.start()                           
            self.__threads.append((spectro_thread, spccdPlugin)) 
            
    def enterAcquisitionMode(self):
        
        #this is where the acquirer receives his first information about work to come
        #for now the acquirer is not yet in a new thread as its execution is not confirmed
        #it can therefore directly share its information with the main thread
        
        self.acquirer = Acquirer.acquirer(self.startThetaPrompt.toPlainText(), self.endThetaPrompt.toPlainText(), self.startPhiPrompt.toPlainText(), self.endPhiPrompt.toPlainText(), self.stepTPrompt.toPlainText(), self.stepPPrompt.toPlainText()) 
        
        #the acquirer then transmits the estimation to the pop up awaiting confirmation
        
        self.confirmMeasStartPopUp = ConfirmMeasStartPopUp.confirmMeasStartPopUp()
        
        self.fillConfirmMeasStartPopUp()
        
        self.confirmMeasStartPopUp.show()
        
        self.confirmMeasStartPopUp.ConfirmAcquisition.clicked.connect(self.whereToSave)
                
    def whereToSave(self):
        
        self.confirmMeasStartPopUp.close()
        
        self.whereToSavePopUp = promptSavePopUp.promptPopUp()
        
        self.whereToSavePopUp.savePathButton.clicked.connect(self.rawfolderCreation)
        
        self.whereToSavePopUp.savePathButton.clicked.connect(self.askForReference)
        
    def rawfolderCreation(self):
        
        if not os.path.exists(self.whereToSavePopUp.pathToFolderPrompt.toPlainText()):
            
            os.mkdir(self.whereToSavePopUp.pathToFolderPrompt.toPlainText())
            
            os.mkdir(self.whereToSavePopUp.pathToFolderPrompt.toPlainText()+'\Raw')

            self.acquisitionFolder = self.whereToSavePopUp.pathToFolderPrompt.toPlainText()+'\Raw'
            
            self.whereToSavePopUp.pathToFolderPrompt.setText("Directory created.")
            
            self.whereToSavePopUp.close()
            
            return
            
        else: 
            
            self.whereToSavePopUp.pathToFolderPrompt.setText("Directory already exists. ")
            
            return     
        
    def fillConfirmMeasStartPopUp(self):
        
        self.confirmMeasStartPopUp.NumberOfStepsValueLabel.setText('{} steps'.format(self.acquirer.totalNumberOfSteps))
        
        self.totalNumberOfMeasSteps = self.acquirer.totalNumberOfSteps
             
        estimatedTime = str(datetime.timedelta(seconds=self.acquirer.estimatedTime))
        
        self.estimatedAcqTime = self.acquirer.estimatedTime
        
        finishTime = str(datetime.datetime.now() + datetime.timedelta(seconds=self.estimatedAcqTime))
        
        self.estimatedAcqFinishTime = finishTime
        
        self.confirmMeasStartPopUp.EstimatedAcTimeValueLabel.setText(estimatedTime) 
        
        self.confirmMeasStartPopUp.finishTimeValueLabel.setText(self.estimatedAcqFinishTime)  
        
    def askForReference(self):
    
    #the reference measurement is performed at all degrees where the experiment is performed, current lowest angle interval
    #is 0.5, can be improved by simulating more angles for the reference.
        
        self.whereToSavePopUp.close()
        
        #the arms are both set at 90 degrees to align the reference, the reference should cut the beam in 2.
        
        self.alignmentPopUp = AlignmentConfirmation.AlignmentPopUp()
        
        self.alignmentPopUp.show()
        
        self.alignmentPopUp.ConfirmAcquisition.clicked.connect(self.confirmedAcquisitionExecution)
      
    def confirmedAcquisitionExecution(self):
        
        self.acquirer.polarizationDirection = self.alignmentPopUp.PolarizerOrientationTxtPrompt.toPlainText()
         
        self.alignmentPopUp.close()  
        
        self.triggerMeasThreads()
        
        self.measPopUp = MeasPopUp.measPopUp()
        
        self.measPopUp.show()
        
        self.initializeMeasPopUp()
        
    def triggerMeasThreads(self):
  
        acquirer_thread = QThread()
        acquirer_thread.setObjectName('acquirer_thread') 
        
        #this is where the acquirer is disconnected from the main thread
        acquirer = self.acquirer  
        self.acquirer = []
        
        #and connected to the acquirer thread
        acquirer.moveToThread(acquirer_thread)
        
        if acquirer.polarizationDirection == 'H':
        
            if os.path.exists('C:\\Users\\leroux\\Documents\\CurrentRef\\UseMeTM'):
           
                self.usePreviousReference = True       
            
            else:
            
                self.usePreviousReference = False
                
        if acquirer.polarizationDirection == 'V':
                
            if os.path.exists('C:\\Users\\leroux\\Documents\\CurrentRef\\UseMeTE'):
                   
                self.usePreviousReference = True       
                    
            else:
                    
                self.usePreviousReference = False
 
        self.sigReference.connect(acquirer.askForReference)
        
        acquirer.sig_msg.connect(self.reactAcqAc)
        acquirer.sig_stepPerformed.connect(self.stepHasBeenPerformed)
        acquirer.sig_time.connect(self.updateEstimate)
        
        self.sigReference.emit(self.usePreviousReference, acquirer.polarizationDirection)
            
        self.sigReadyforMainAcquisition.connect(acquirer.acquire)
        acquirer.sigAskToPlaceSample.connect(self.placeSample)
        acquirer.sig_askForMovePhi.connect(self.rotateSampleStageTo)
        
        #this thread is the data handler thread
        
        datahandler_thread = QThread()
        datahandler_thread.setObjectName('data_handler_thread')
        self.datahandlerThreadName = datahandler_thread.objectName
        
        #the data handler is connected to its own thread and work on the computer
        #side to handle all the data collection
        
        datahandler = WLRDataHandler(self.acquisitionFolder)
        
        datahandler.moveToThread(datahandler_thread)
        
        datahandler.sig_msg.connect(self.reactAcqAc)
        acquirer.sig_Spectrum.connect(datahandler.saveLastSpectrum)
        acquirer.sig_SpectrumRef.connect(datahandler.saveReference)
        acquirer.sig_askForCopyRef.connect(datahandler.copyRefFolder)
        
        #this thread is dedicated to making the preview
        
        preview_thread = QThread()
        preview_thread.setObjectName('preview_thread') 
        
        preview = dataPreviewer(acquirer, self.acquisitionFolder)
        
        #and connected to the preview thread
        
        preview.moveToThread(preview_thread) 
        
        preview_thread.started.connect(preview.firstConnection)
        
        datahandler.sig_askForRefAnalysis.connect(preview.AnalyzeRef)
        datahandler.sig_askForDataTreatment.connect(preview.analyzeData)
        #self.sig_previewProgress.connect(preview.makePreviewImage)
        
        #this thread connects the last recorded spectrum to the spectrum plot
        #and to the data handler
        
        for thread, worker in self.__threads:
            
            if thread.objectName == self.spectroThreadName:

                worker.sig_spectrum.connect(self.updateSpectrumPlot)
                worker.sig_spectrum.connect(acquirer.spectrumReceived)       
                worker.sig_msg.connect(self.reactAcqAc)   
                
                acquirer.sig_requestSpectrum.connect(worker.recordSpectrum)  
                               
            if thread.objectName == self.btThreadName:
                
                acquirer.sig_askForMove.connect(worker.moveTo)
                
            if thread.objectName == self.topThreadName:
                    
                acquirer.sig_askForMove.connect(worker.moveTo)
                
        #All the threads are then started
        
        datahandler_thread.start()
        self.__threads.append((datahandler_thread, datahandler))
        
        preview_thread.start()
        self.__threads.append((preview_thread, preview))
                           
        acquirer_thread.start()                           
        self.__threads.append((acquirer_thread, acquirer))    
        
    def initializeMeasPopUp(self):
        
        self.progressPercentage = 0
        
        self.progressSteps = 0
        
        self.measPopUp.Log.append('Starting Acquisition.')
        
        #this should initialize the values on the pop up given that it is faster than the first step
        
        self.finishTime = (datetime.datetime.now() + datetime.timedelta(seconds=self.estimatedAcqTime))
            
        self.measPopUp.finishTimeValueLabel.setText(str(self.finishTime))
            
        self.measPopUp.remainingTimeValueLabel.setText(str(self.finishTime - datetime.datetime.now()))
            
        self.measPopUp.progressValueLabel.setText('{}%, {} steps out of {}\n \n steps have been performed'.format(round(self.progressPercentage,1), self.progressSteps, self.totalNumberOfMeasSteps))    
    
    
    @pyqtSlot()
    
    def placeSample(self):
    
        self.placeSamplePopUp = AlignmentConfirmation.placeSamplePopUp()

        self.placeSamplePopUp.show()
        
        self.placeSamplePopUp.ConfirmAcquisition.clicked.connect(self.Sampleplaced)
        
    def Sampleplaced(self):
        
        self.placeSamplePopUp.close()
        
        self.sigReadyforMainAcquisition.emit()
        
    @pyqtSlot(float)
        
    def updateEstimate(self, estimatedTime:float):
        
        self.estimatedAcqTime = estimatedTime
        
        self.finishTime = (datetime.datetime.now() + datetime.timedelta(seconds=self.estimatedAcqTime))
        
        self.measPopUp.finishTimeValueLabel.setText(str(self.finishTime))
        
        self.measPopUp.remainingTimeValueLabel.setText(str(self.finishTime - datetime.datetime.now()))
        
    @pyqtSlot(int, int)
        
    def stepHasBeenPerformed(self, currentStepTheta:int, currentStepPhi:int):
        
        self.progressPercentage = ((currentStepTheta*(currentStepPhi+1))/self.totalNumberOfMeasSteps)*100 
            
        self.measPopUp.progressValueLabel.setText('{}%, {} steps out of {}\n \nsteps have been performed'.format(round(self.progressPercentage,1), (currentStepTheta*(currentStepPhi+1)), self.totalNumberOfMeasSteps))   
    
    @pyqtSlot(Spectrometry.Spectrum)
    
    def updateSpectrumPlot(self, lastSpectrum: Spectrometry.Spectrum):
        
        self.measPopUp.static_canvas.figure.clf() 
        self.measPopUp.static_canvas.figure.subplots().plot(lastSpectrum.wvl, lastSpectrum.inte, ".")  
        self.measPopUp.static_canvas.draw()
        
    @pyqtSlot(ImageQt.ImageQt)
    
    def updateAcqImage(self, acqimg: ImageQt.ImageQt):
           
        self.measPopUp.measSlot.updateImage(acqimg)
        self.measPopUp.show() 
        
    @pyqtSlot(str)   
    
    def react(self,string: str):
        
        self.Log.append(string)
        
    @pyqtSlot(str)   
    def reactAcqAc(self,string: str):
        
        self.measPopUp.Log.append(string)       
        
 #Rotating stage methods   
 
    @pyqtSlot()
                    
    def carryInitialTest(self):
            
        self.sigInitTest.emit()
            
    @pyqtSlot()
        
    def freeMove(self):
        
        self.freeMovePopUp = FreeMovePopUp.FreeMovePopUp(self.angleLCDTop.value(),self.angleLCDBt.value())
        self.freeMovePopUp.show()
        
        self.freeMovePopUp.pushButton.clicked.connect(self.freeMoveOrder) 
            
    def Reflection(self):
                 
        safePosition = 10
        maxPosition = 80
        
        self.ReflectionPopUp = ReflectionPopUp.ReflectionPopUp(safePosition, maxPosition)
        self.ReflectionPopUp.show()
        
        self.ReflectionPopUp.pushButton.clicked.connect(self.ReflectionOrder)
        
    @pyqtSlot(str)   
    def connectedToEquipment(self, arm_id: str):
        
        if arm_id == self.identifierTop:
            
            self.topArmButton.setPixmap(QPixmap(":/GreenButton.png"))
            self.isTopConnected = True
            
        if arm_id == self.identifierBt:
            
            self.btArmButton.setPixmap(QPixmap(":/GreenButton.png")) 
            self.isBottomConnected = True
            
        if self.isBottomConnected and self.isTopConnected:
        
            self.statusButton.setPixmap(QPixmap(":/GreenButton.png"))
            self.connectRStageButton.setText("Disconnect")
            self.connectRStageButton.clicked.disconnect()
            self.connectRStageButton.clicked.connect(self.disconnectFromEquipment)
    
    #Sample Stage

    
    @pyqtSlot()   
    def connectedToSampleStage(self):
        
            self.statusSampleStageButton.setPixmap(QPixmap(":/GreenButton.png"))
     
    @pyqtSlot()       
    def updatePositionSampleStage(self):
        
            self.SampleOrientationLCD.display(self.sampleRotatingStage.position)
                              
    def askForRotationSampleStage(self):
        
            self.rotateSampleStageTo(float(self.SampleOrientationGoToPrompt.toPlainText()))
    
    @pyqtSlot(float)
    def rotateSampleStageTo(self, targetAngle):

            self.Log.append('Moving sample to Phi:{} degrees'.format(targetAngle))
            self.sampleRotatingStage.move_to(targetAngle,True) 
            self.SampleOrientationLCD.display(self.sampleRotatingStage.position)
        
    @pyqtSlot()        
    def disconnectFromEquipment(self):
        
        self.sig_disconnectRS.emit()
        
        if self.BtHasAskedForDisconnection == False or self.topHasAskedForDisconnection == False:
            
            self.BtHasAskedForDisconnection = True
            self.topHasAskedForDisconnection = True
        
            
    def succesfulDisconnection(self):
         
        self.topArmButton.setPixmap(QPixmap(":/RedButton.png"))
        self.isTopConnected = False
            
        self.btArmButton.setPixmap(QPixmap(":/RedButton.png")) 
        self.isBottomConnected = False  
        
        self.angleLCDBt.display(0)
        self.angleLCDTop.display(0)
        
        self.stepLCDBt.display(0)
        self.stepLCDTop.display(0)

        self.Log.append("Succesful Disconnection")
        
        self.hasAlreadyRanOnce = True
        
        self.cnectButton.setText("Connect")  
        
        self.cnectButton.clicked.disconnect()
        self.cnectButton.clicked.connect(self.attemptConnections)          
            
    @pyqtSlot(str, float, float)
    def updateAnglesAndSteps(self, arm_id:str, steps:float, angle:float):  
        
        if arm_id == self.identifierTop:
            
            self.stepLCDTop.display(steps)
            self.angleLCDTop.display(angle)
        
        if arm_id == self.identifierBt:
                
            self.stepLCDBt.display(steps)
            self.angleLCDBt.display(angle)
            
    def freeMoveOrder(self):
        
        targetAngleTop = self.freeMovePopUp.topPrompt.toPlainText()
        
        targetAngleBottom = self.freeMovePopUp.btPrompt.toPlainText()
        
        currentAngleTop = (str(self.angleLCDTop.value()))
        
        currentAngleBottom = (str(self.angleLCDBt.value()))        
              
        for thread, worker in self.__threads:
                               
            if thread.objectName == self.btThreadName:
                
                btThread, btWorker = thread, worker
                
            if thread.objectName == self.topThreadName:             
                
                topThread, topWorker = thread, worker   
                
        if self.isTopConnected and targetAngleTop != currentAngleTop:
                            
            self.sig_askForMove.emit(self.identifierTop,float(targetAngleTop))
        
        if self.isBottomConnected and targetAngleBottom != currentAngleBottom:
                                         
            self.sig_askForMove.emit(self.identifierBt,float(targetAngleBottom))
                
    @pyqtSlot()  
    
    def ReflectionOrder(self):

        startAngle = self.ReflectionPopUp.startPrompt.toPlainText()

        endAngle = float(self.ReflectionPopUp.endPrompt.toPlainText())
        
        step = float(self.ReflectionPopUp.stepPrompt.toPlainText())
        
        if self.isTopConnected:
            
            if self.isBottomConnected:
                      
                for thread, worker in self.__threads:
                                       
                    if thread.objectName == self.btThreadName:
                        
                        btThread, btWorker = thread, worker
                        
                    if thread.objectName == self.topThreadName:             
                        
                        topThread, topWorker = thread, worker
            
                currentAngle = float(startAngle)
                
                # the arms first move to safe positions
                
                topWorker.moveToSafePosition()
                
                btWorker.moveToSafePosition()
                
                # the arms then perform the loop - to be implemented, 
                # interaction with the spectrograph
                
                while currentAngle <= endAngle :
                
                    self.sig_askForMove.emit(self.identifierTop,float(currentAngle))
                
                    self.sig_askForMove.emit(self.identifierBt,float(currentAngle))
                    
                    currentAngle = currentAngle + step
                    
                self.Log.append('The Reflection process has been performed, reaching a final angle of {}°' .format(round(currentAngle,3)))
            

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

   
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    NpGui = QMainWindow()
    ui = GUI(NpGui)
    NpGui.show()
    
    sys.exit(app.exec_())
    
   
   