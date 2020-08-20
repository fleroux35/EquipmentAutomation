# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

import math as m
import numpy as np
import time
from PIL import ImageQt

from Spectrometry import Spectrum

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot

class mapDataHandler(QObject): 
    
    sig_msg = pyqtSignal(str)
    sig_image = pyqtSignal(ImageQt.ImageQt)
    sig_askForNorm = pyqtSignal(int,int)
    
    def __init__(self, acquisitionFolder):

        super().__init__()

        self.acquisitionFolder = acquisitionFolder 
        
    #@pyqtSlot(numpy.array, numpy.array)
    
    def receiveMapTable(self, X:np.array, Y:np.array):
        
        self.X = X
        self.Y = Y
        
        self.formMapTable
                  
    @pyqtSlot(Spectrum, int, int, float, float)   
        
    def saveLastSpectrum(self,lastSpectrum:Spectrum, X:int, Y:int, realX:float, realY:float):
        
        currentName = str(self.acquisitionFolder + '\\Xstep{}_Ystep{}@X{}_Y{}.csv'.format(X, Y, realX, realY))
        
        self.sig_msg.emit(currentName.strip())
        
        np.savetxt(currentName, lastSpectrum.toArray(), delimiter=",")
        
        self.sig_askForNorm.emit(X,Y)
        