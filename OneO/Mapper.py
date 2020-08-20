# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

#Careful, the stage direction is opposite to the final output map
#The actual map records from the top left line by line horizontally
#when it changes line the direction is changed to ensure the stage is making
#small movements. The movements here are absolute to try and rely on the sensors.

import math as m
import numpy as np
import time
from Spectrometry import Spectrum

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

class mapper(QObject):          
        
        #estimated time for one step should be entered here (in seconds):
        
        step_time = 11
        stageSleepTime = 1 #this has to be defined according to the speed of the stage
        
        sig_msg = pyqtSignal(str)
        sig_stepPerformed = pyqtSignal(int)
        sig_time = pyqtSignal(float)
        
        #to communicate with the Image Displayer on the progress
        
        sig_requestImgProgress = pyqtSignal(int,int,int,int)
        sig_requestFinProgress = pyqtSignal()

        #to communicate with the stage  
        sig_askForMove = pyqtSignal(float,float,float) 
        
        #to communicate with the spectrometer
        
        sig_requestSpectrum = pyqtSignal()
        
        #to communicate with the data handler
        
        sig_Spectrum = pyqtSignal(Spectrum, int, int, float, float)
        
        def __init__(self, Xcentre, Ycentre, Xlength, Ylength, Xstep, Ystep, Zlock):
                
                super().__init__()
        
                self.Xcentre = float(Xcentre)
                self.Ycentre = float(Ycentre)
                self.Xlength = float(Xlength)
                self.Ylength = float(Ylength)
                
                #Zlock will try and maintain the focus in position using the stage
                self.Zlock = float(Zlock)
                
                #steps are received in nm, conversion is done here
                self.Xstep = float(Xstep) * m.pow(10,-3)
                self.Ystep = float(Ystep) * m.pow(10,-3)
                
                self.numberOfXCells = m.ceil(self.Xlength/self.Xstep) + 1
                
                self.numberOfYCells = m.ceil(self.Ylength/self.Ystep) + 1   
                
                self.numberOfSteps = self.numberOfXCells * self.numberOfYCells
                
                self.updateEstimatedTime(self.numberOfSteps)
                
                #isMoveSuccess is a boolean that turns true once the stage has confirmed
                #its position to inform the mapper that it can safely ask the spectrometer
                #to record at this position
                
                self.isMoveSuccess = False
                
                #isSpectrumReceived is a boolean that turns true once the spectrometer
                #has sent its spectrum to inform the mapper that it can safely move on
                
                self.isSpectrumReceived = False
                
                self.currentSpectrum = Spectrum(0, 0)

                self.mapIsDone = False
                
                self.currentDirection = 1
                
                #the currentDirection indicates what way the stage was going during the last move
                
                self.currentX = 0
                self.currentY = 0 
                
                
        def updateEstimatedTime(self, numberOfStepsLeft):
                
                self.estimatedTime = numberOfStepsLeft * self.step_time
                
                self.sig_time.emit(self.estimatedTime)
                           
        def acquiremap(self):
                
                self.XPositions, self.YPositions = self.formPositions()
                
                numberOfStepsLeft = self.numberOfSteps
                
                currentStep = 0
                              
                while not self.mapIsDone:

                        QCoreApplication.processEvents()
                        
                        self.updateEstimatedTime(numberOfStepsLeft)
                        
                        self.previousX, self.previousY = self.currentX, self.currentY
                        
                        self.currentX, self.currentY, self.currentDirection = self.nextStep() 
                        
                        self.sig_requestImgProgress.emit(self.previousX, self.previousY, self.numberOfXCells-1, self.numberOfYCells-1) 
                        
                        currentStep = currentStep + 1
                        
                        numberOfStepsLeft = numberOfStepsLeft - 1
                        
                        self.updateEstimatedTime(numberOfStepsLeft)
                        
                        self.sig_stepPerformed.emit(currentStep) 
                
                self.sig_requestFinProgress.emit()
                
                self.sig_msg.emit('Acquisition successful.')
                
                return
                        
        def formPositions(self):
                
                Xorigin = self.Xcentre - round(self.Xlength/2,2)
                
                Yorigin = self.Ycentre - round(self.Ylength/2,2)
                
                # the Positions in this matrix are the ones that will be sent to the stage
                
                XPositions = np.linspace(Xorigin, Xorigin + self.Xlength, self.numberOfXCells)                      
                
                YPositions = np.linspace(Xorigin, Yorigin + self.Ylength, self.numberOfYCells)  
                
                return XPositions, YPositions                   
                                
        def nextStep(self):
                
                ## in first position
                
                if self.currentX == 0 and self.currentY == 0: 
                        
                        self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                        
                        self.sig_msg.emit('moving to X:{}, Y:{}, first positions.'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
  
                        self.acquireDataSafely()
                        
                        self.currentX = self.currentX + 1
                        
                        return self.currentX, self.currentY, self.currentDirection
                             
                # at a position that is not the last Y line, at a position which is not the last X position
                
                if self.currentDirection == 1:
                
                        if self.currentY <= self.numberOfYCells-1 and self.currentX < self.numberOfXCells-1:
                                
                                self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                                
                                self.sig_msg.emit('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                
                                #print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                
                                self.acquireDataSafely()                              
                                
                                self.currentX = self.currentX + 1
                                                                                        
                                return self.currentX, self.currentY, self.currentDirection
                        
                        #At a position which is the last available Y position
                        
                        else:
                                
                                #check for the last line / termination
                                                       
                                if self.currentY < self.numberOfYCells-1:
                                        
                                        self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                                        
                                        self.sig_msg.emit('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                        
                                        #print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                        
                                        self.acquireDataSafely()
                                        
                                        self.currentY = self.currentY + 1
                                        
                                        #change of direction for the next line
                                        
                                        self.currentDirection = 1 - self.currentDirection
                                        
                                        return self.currentX, self.currentY, self.currentDirection
                                        
                                else:                        
                        
                                        #at the very last position
                                        
                                        self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                                        
                                        self.sig_msg.emit('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                        
                                        #print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))                                        
                                        
                                        self.acquireDataSafely()
                                        
                                        self.mapIsDone = True
                                        
                                        return 0 , 0, 0
                                
                if self.currentDirection == 0: 
                        
                        if self.currentY <= self.numberOfYCells-1 and self.currentX > 0:
                                
                                self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                                
                                self.sig_msg.emit('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                
                                #print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                
                                #fill up matrix with spectra
                                
                                self.acquireDataSafely()
                                
                                self.currentX = self.currentX - 1
                                                        
                                return self.currentX, self.currentY, self.currentDirection
                        
                        #At a position which is the last available Y position
                        
                        else:
                                
                                #check for the last line / termination
                                                       
                                if self.currentY < self.numberOfYCells-1:
                                        
                                        self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                                        
                                        self.sig_msg.emit('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                        
                                        #print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))

                                        self.acquireDataSafely()
                                        
                                        self.currentY = self.currentY + 1
                                        
                                        self.currentDirection = 1 - self.currentDirection
                                        
                                        return self.currentX, self.currentY, self.currentDirection                                
                                        
                                else:                        
                        
                                        #at the very last position
                                        
                                        self.sig_askForMove.emit(self.XPositions[self.currentX],self.YPositions[self.currentY],self.Zlock)
                                        
                                        self.sig_msg.emit('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                        
                                        #print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))                                        
                                        
                                        self.acquireDataSafely()
                                        
                                        self.mapIsDone = True
                                        
                                        return 0 , 0, 0
                                
        def acquireDataSafely(self):
                                                               
                #the thread is put on hold to allow the stage to move
                QCoreApplication.processEvents()
                
                self.sig_msg.emit('The stage is moving...')
        
                #time.sleep(self.stageSleepTime)
        
                #the thread then asks for the positions to be received
                #before asking the spectrometer to do anything.
                
                loopcontrol = 1
                
                while loopcontrol == 1:      
                        
                        QCoreApplication.processEvents()
                              
                        if self.isMoveSuccess == True:
                                
                                QCoreApplication.processEvents()
                                
                                self.sig_msg.emit('Positions read from stage before acquisition: X:{}, Y:{}, Z:{}, asking spectrometer to record...'.format(self.currentXPosition, self.currentYPosition, self.currentZPosition))
        
                                self.sig_requestSpectrum.emit()
        
                                self.isMoveSuccess = False
                                
                                loopcontrol = 0
        
                #the mapper then awaits the spectrum to be received
                #before sending the data to the handler and moving on.
                
                self.sig_msg.emit('Waiting for spectrometer...')
                
                loopcontrol = 1
               
                while loopcontrol == 1:      
                        
                        QCoreApplication.processEvents()
        
                        if self.isSpectrumReceived == True:
                                
                                self.sig_msg.emit('Spectrum recorded.')
                                
                                QCoreApplication.processEvents()
        
                                self.sig_Spectrum.emit(self.currentSpectrum, self.currentX, self.currentY, self.currentXPosition, self.currentYPosition)
        
                                self.isSpectrumReceived = False 
                                
                                loopcontrol = 0                             
                                
        @pyqtSlot(Spectrum)
        
        def spectrumReceived(self, spectrum:Spectrum):               
                
                self.currentSpectrum = spectrum
                
                self.isSpectrumReceived = True
                
        @pyqtSlot(float, float, float)
        
        def positionsReceived(self, X:float, Y:float, Z:float):
                
                self.currentXPosition = X
                self.currentYPosition = Y
                self.currentZPosition = Z
                
                self.isMoveSuccess = True
                      
                                
if __name__ == "__main__":
                        
        local_algo = mapper(100, 100, 1, 1, 50, 50)
                        
                        
                        
                                 
                
                
                
                
                