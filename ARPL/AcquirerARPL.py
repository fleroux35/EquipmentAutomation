# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

import math as m
import numpy as np
import time
from Spectrometry import Spectrum
import AlignmentConfirmation

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

class acquirerARPL(QObject):          
        
        sig_msg = pyqtSignal(str)
        sig_stepPerformed = pyqtSignal(int)
        sig_time = pyqtSignal(float)
        
        #to communicate with the Image Displayer on the progress
        
        sig_requestImgProgress = pyqtSignal(int)

        #to communicate with the Rotating stage  
        sig_askForMove = pyqtSignal(str, float) 
        
        #to communicate with the main thread
        sigAskToPlaceSample = pyqtSignal()
        
        #to communicate with the spectrometer
        
        sig_requestSpectrum = pyqtSignal()
        
        #to communicate with the data handler
        
        sig_Spectrum = pyqtSignal(Spectrum, float)
        sig_SpectrumBckgd = pyqtSignal(Spectrum, float)
        sig_askForCopyBackground = pyqtSignal()        
        
        def __init__(self, startAngle, lastAngle, step, acquisitionTime):
                
                super().__init__()
                
                self.stageSleepTime = 3
                
                self.identifierTop = 'Top Arm'       
                self.identifierBt = 'Bottom Arm'
                
                self.polarizationDirection = ''
        
                self.startAngle = float(startAngle)
                self.lastAngle = float(lastAngle)
                self.step = float(step)
                
                #will have to be changed according to spectrometer
                self.acquisitionTime = 1
                
                #this second time includes the time for the stage to move properly
                
                self.estimatedTimePerStep = self.acquisitionTime + 5
                
                #if the number can not be divided, the stage will adjust the angle to a lower angle and perform the full range
                
                self.numberOfSteps = m.ceil((self.lastAngle - self.startAngle) / self.step) + 1
                
                #isMoveSuccess is a boolean that turns true once the stage has confirmed
                #its position to inform the acquirer that it can safely ask the spectrometer
                #to record at this position
                
                self.isMoveSuccess = False
                
                #isSpectrumReceived is a boolean that turns true once the spectrometer
                #has sent its spectrum to inform the mapper that it can safely move on
                
                self.isSpectrumReceived = False
                
                self.currentSpectrum = Spectrum(0, 0)

                self.measurementIsDone = False
                
                self.BackgroundIsDone = False
                
                self.updateEstimatedTime(self.numberOfSteps)
                
                self.Angles = self.formAngles()
                              
        def updateEstimatedTime(self, numberOfStepsLeft):
                
                self.estimatedTime = numberOfStepsLeft * self.estimatedTimePerStep
                
                self.sig_time.emit(self.estimatedTime)
                
        @pyqtSlot(bool) 
        
        def askForBackground(self, usePreviousBckgd):
                
                if usePreviousBckgd == False:
                        
                        self.sig_msg.emit('Background Acquisition...')
                
                        self.acquireBackground()
                
                        self.sig_msg.emit('The background has been acquired.')
                        
                if usePreviousBckgd == True:
                        
                        self.sig_msg.emit('Preparing Background Folder based on previous data.')
                        
                        self.sig_askForCopyBackground.emit()
                
                self.sigAskToPlaceSample.emit()               
                              
        def acquire(self):
                                
                numberOfStepsLeft = self.numberOfSteps           
                                   
                self.currentStep = 0
                
                self.sig_msg.emit('Waiting for initial positioning Measurement.')
                
                self.askForMove(self.Angles[0])
                
                time.sleep(5)
                              
                while not self.measurementIsDone:

                        QCoreApplication.processEvents()
                        
                        self.nextStep() 
                        
                        self.currentStep = self.currentStep + 1
                        
                        numberOfStepsLeft = numberOfStepsLeft - 1
                
                self.sig_msg.emit('Acquisition successful.')
                
                return  
        
        def acquireBackground(self):
                
                numberOfStepsLeft = self.numberOfSteps
                
                self.currentStepBckgd = 0
                
                self.sig_msg.emit('Waiting for initial positioning Bckgd.')
                
                self.askForMove(self.Angles[0])
                
                time.sleep(10)
                              
                while not self.BackgroundIsDone:

                        QCoreApplication.processEvents()
                        
                        self.nextStepBckgd() 
                        
                        self.currentStepBckgd = self.currentStepBckgd + 1
                        
                        numberOfStepsLeft = numberOfStepsLeft - 1
                
                self.sig_msg.emit('Background Acquisition successful.')
                
                return                
                        
        def formAngles(self):
                
                #this is where the step is automatically adjusted
                      
                Angles = np.linspace(self.startAngle, self.lastAngle, self.numberOfSteps) 
                
                for element in Angles:
                        
                        print(element)
                
                return Angles 
        
        def nextStepBckgd(self):
                        
                if self.currentStepBckgd != 0:
                        
                        self.askForMove(self.Angles[self.currentStepBckgd])
                
                        self.sig_msg.emit('moving to Angle: {}'.format(self.Angles[self.currentStepBckgd]))
  
                self.acquireDataForBckgdSafely()
                                                   
                #check for termination
                                                       
                if self.currentStepBckgd == self.numberOfSteps-1:
                        
                #at the very last position

                        self.BackgroundIsDone = True
                
                return         
                                
        def nextStep(self):
                
                if self.currentStep != 0:

                        self.askForMove(self.Angles[self.currentStep])
                
                        self.sig_msg.emit('moving to Angle: {}'.format(self.Angles[self.currentStep]))
  
                self.acquireDataSafely()
                                                   
                #check for termination
                                                       
                if self.currentStep == self.numberOfSteps-1:
                        
                #at the very last position

                        self.measurementIsDone = True
                
                return     
        
        def acquireDataForBckgdSafely(self):
                
                #the thread is put on hold to allow the stage to move
                
                QCoreApplication.processEvents()
                
                self.sig_msg.emit('The stage is moving...')
        
                time.sleep(self.stageSleepTime)
                
                self.sig_msg.emit('Waiting for spectrometer...')
                
                self.sig_requestSpectrum.emit()
                
                loopcontrol = 1
               
                while loopcontrol == 1:      
                        
                        QCoreApplication.processEvents()
        
                        if self.isSpectrumReceived == True:
                                
                                self.sig_msg.emit('Spectrum received on Acquirer.')
                                
                                QCoreApplication.processEvents()
        
                                self.sig_SpectrumBckgd.emit(self.currentSpectrum, self.Angles[self.currentStepBckgd])
        
                                self.isSpectrumReceived = False 
                                
                                loopcontrol = 0           
                                
        def acquireDataSafely(self):
                                                               
                #the thread is put on hold to allow the stage to move
                
                QCoreApplication.processEvents()
                
                self.sig_msg.emit('The stage is moving...')
        
                time.sleep(self.stageSleepTime)
                
                self.sig_msg.emit('Waiting for spectrometer...')
                
                self.sig_requestSpectrum.emit()
                
                loopcontrol = 1
               
                while loopcontrol == 1:      
                        
                        QCoreApplication.processEvents()
        
                        if self.isSpectrumReceived == True:
                                
                                self.sig_msg.emit('Spectrum received on Acquirer.')
                                
                                QCoreApplication.processEvents()
        
                                self.sig_Spectrum.emit(self.currentSpectrum, self.Angles[self.currentStep])
        
                                self.isSpectrumReceived = False 
                                
                                loopcontrol = 0 
                                
        @pyqtSlot(Spectrum)
        
        def spectrumReceived(self, spectrum:Spectrum):              
                
                self.currentSpectrum = spectrum
                
                self.isSpectrumReceived = True
                
        def askForMove(self, angle:float):
        
                self.sig_askForMove.emit(self.identifierBt, angle)
                        
                        
                        
                                 
                
                
                
                
                