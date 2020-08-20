# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

import math as m
import numpy as np
import time
from Spectrometry import Spectrum
import AlignmentConfirmation

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

class acquirer(QObject):          
        
        sig_msg = pyqtSignal(str)
        sig_stepPerformed = pyqtSignal(int, int)
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
        
        sig_Spectrum = pyqtSignal(Spectrum, float, float)
        sig_SpectrumRef = pyqtSignal(Spectrum, float, str)
        sig_askForCopyRef = pyqtSignal(str)

        #Sample Rotation
        sig_askForMovePhi = pyqtSignal(float)        

        def __init__(self, startAngleTheta, lastAngleTheta, startAnglePhi, lastAnglePhi, stepTheta, stepPhi):
                
                super().__init__()
                
                self.stageSleepTime = 2.3
                
                self.usePreviousReference = False
                
                self.identifierTop = 'Top Arm'       
                self.identifierBt = 'Bottom Arm'
                
                self.polarizationDirection = ''
        
                self.startAngleTheta = float(startAngleTheta)
                self.lastAngleTheta = float(lastAngleTheta)
                
                self.startAnglePhi = float(startAnglePhi)
                self.lastAnglePhi = float(lastAnglePhi)
                
                self.stepTheta = float(stepTheta)
                self.stepPhi = float(stepPhi)
                
                #this second time includes the time for the stage to move properly
                
                self.estimatedTimePerStep = 8.25
                
                #if the number can not be divided, the stage will adjust the angle to a lower angle and perform the full range
                
                self.numberOfStepsTheta = m.ceil((self.lastAngleTheta - self.startAngleTheta) / self.stepTheta) + 1
                self.numberOfStepsPhi = m.ceil((self.lastAnglePhi - self.startAnglePhi) / self.stepPhi) + 1
                
                self.totalNumberOfSteps = self.numberOfStepsTheta * self.numberOfStepsPhi
                
                #isMoveSuccess is a boolean that turns true once the stage has confirmed
                #its position to inform the acquirer that it can safely ask the spectrometer
                #to record at this position
                
                self.isMoveSuccess = False
                
                #isSpectrumReceived is a boolean that turns true once the spectrometer
                #has sent its spectrum to inform the mapper that it can safely move on
                
                self.isSpectrumReceived = False
                
                self.currentSpectrum = Spectrum(0, 0)

                self.measurementIsDone = False
                
                self.refIsDone = False
                
                self.updateEstimatedTime(self.totalNumberOfSteps)
                
                AnglesTheta, AnglesPhi = self.formAngles()
                
                self.AnglesTheta = AnglesTheta
                
                self.AnglesPhi = AnglesPhi
                
                self.maxStepTheta = np.size(self.AnglesTheta) - 1
                
                self.maxStepPhi = np.size(self.AnglesPhi) - 1
                              
        def updateEstimatedTime(self, numberOfStepsLeft):
                
                self.estimatedTime = numberOfStepsLeft * self.estimatedTimePerStep
                
                self.sig_time.emit(self.estimatedTime)  
                
                        
        def formAngles(self):
                      
                AnglesTheta = np.linspace(self.startAngleTheta, self.lastAngleTheta, self.numberOfStepsTheta) 
                
                AnglesPhi = np.linspace(self.startAnglePhi, self.lastAnglePhi, self.numberOfStepsPhi)
                
                return AnglesTheta, AnglesPhi    
        
        @pyqtSlot(bool, str) 
        
        def askForReference(self, usePreviousRef, polarization):
                
                if usePreviousRef == False:
                        
                        self.sig_msg.emit('Reference Acquisition...')
                
                        self.acquireRef()
                
                        self.sig_msg.emit('The reference has been acquired.')
                        
                if usePreviousRef == True:
                        
                        self.sig_msg.emit('Preparing Reference Folder based on previous data.')
                        
                        self.sig_askForCopyRef.emit(polarization)
                
                self.sigAskToPlaceSample.emit()
                
                self.askForMove(40)
                              
        def acquire(self):
                
                self.askForMove(self.AnglesTheta[0])
                
                self.askForMovePhi(self.AnglesPhi[0])
                
                self.sig_msg.emit('Initializing real measurement')
                
                time.sleep(20)
                
                numberOfStepsLeft = self.totalNumberOfSteps
                
                self.currentStepTheta = 0
                
                self.currentStepPhi = 0
                
                changeInThetaOnly = True
                              
                while not self.measurementIsDone:

                        QCoreApplication.processEvents()
                        
                        self.updateEstimatedTime(numberOfStepsLeft)
                        
                        self.nextStep(changeInThetaOnly) 
                        
                        if self.currentStepTheta < self.maxStepTheta: 
                        
                                self.currentStepTheta = self.currentStepTheta + 1
                                
                                changeInThetaOnly = True
                                
                        else:
                                if self.currentStepPhi < self.maxStepPhi:
                                        
                                        self.currentStepPhi = self.currentStepPhi + 1
                                        
                                        self.currentStepTheta = 0
                                        
                                        changeInThetaOnly = False
                                        
                                else:
                                        
                                        self.measurementIsDone = True
                        
                        numberOfStepsLeft = numberOfStepsLeft - 1
                        
                        self.updateEstimatedTime(numberOfStepsLeft)
                        
                        self.sig_stepPerformed.emit(self.currentStepTheta, self.currentStepPhi) 
                
                self.sig_msg.emit('Acquisition successful.')
                
                return
        
        def acquireRef(self):   
                
                #the Ref is only acquired at Phi = 0 as it is normally a mirror with normal symmetry
                
                self.askForMove(self.AnglesTheta[0])
                
                self.sig_msg.emit('Initializing real measurement')
                
                time.sleep(10)                
                
                numberOfStepsLeft = self.numberOfStepsTheta
                
                self.currentStepRef = 0             
                              
                while not self.refIsDone:

                        QCoreApplication.processEvents()
                        
                        self.nextStepRef() 
                        
                        self.currentStepRef = self.currentStepRef + 1
                        
                        numberOfStepsLeft = numberOfStepsLeft - 1
                
                self.sig_msg.emit('Reference Acquisition successful.')
                
                return        
               
                                
        def nextStep(self, changeInThetaOnly):
                             
                if changeInThetaOnly:
                        
                        self.askForMove(self.AnglesTheta[self.currentStepTheta])
                        
                        self.sig_msg.emit('moving to Theta: {}, Phi still at: {}'.format(self.AnglesTheta[self.currentStepTheta], self.AnglesPhi[self.currentStepPhi]))
                
                if changeInThetaOnly is False:
                        
                        self.askForMove(self.AnglesTheta[self.currentStepTheta])
                
                        self.askForMovePhi(self.AnglesPhi[self.currentStepPhi])
                        
                        time.sleep(5)
                        
                        #print('Allowing more time to return to initial angle.')
        
                        self.sig_msg.emit('moving to Theta: {}, to Phi: {}'.format(self.AnglesTheta[self.currentStepTheta], self.AnglesPhi[self.currentStepPhi]))
                                          
                #wait for the stage to be in position

                self.acquireDataSafely() 
                
                return
        
        def nextStepRef(self):
                        
                self.askForMove(self.AnglesTheta[self.currentStepRef])
                
                self.sig_msg.emit('moving to Angle: {}'.format(self.AnglesTheta[self.currentStepRef]))
  
                self.acquireDataForRefSafely()
                                                   
                #check for termination
                                                       
                if self.currentStepRef == self.numberOfStepsTheta-1:
                        
                #at the very last position

                        self.refIsDone = True
                
                return        
        
        def acquireDataForRefSafely(self):
                
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
                                
                                self.sig_msg.emit('Spectrum recorded.')
                                
                                QCoreApplication.processEvents()
        
                                self.sig_SpectrumRef.emit(self.currentSpectrum, self.AnglesTheta[self.currentStepRef], self.polarizationDirection)
        
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
                                
                                self.sig_msg.emit('Spectrum recorded.')
                                
                                QCoreApplication.processEvents()
        
                                self.sig_Spectrum.emit(self.currentSpectrum, self.AnglesTheta[self.currentStepTheta],self.AnglesPhi[self.currentStepPhi])
        
                                self.isSpectrumReceived = False 
                                
                                loopcontrol = 0 
                                
        @pyqtSlot(Spectrum)
        
        def spectrumReceived(self, spectrum:Spectrum):              
                
                self.currentSpectrum = spectrum
                
                self.isSpectrumReceived = True
                
        def askForMove(self, angle:float):
        
                self.sig_askForMove.emit(self.identifierTop, angle)
                self.sig_askForMove.emit(self.identifierBt, angle)
                
        def askForMovePhi(self, angle:float):
        
                self.sig_askForMovePhi.emit(angle)
                        
                        
                        
                                 
                
                
                
                
                