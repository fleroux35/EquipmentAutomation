# -*- coding: utf-8 -*-

# Author: Florian Le Roux

import resources
import sys
import numpy as np

import random
from numpy import genfromtxt

class Spectrum():
    
    def __init__(self, Wavelength, Intensity):
        
        self.wvl = Wavelength
        self.inte = Intensity
        
    def toArray(self):
        
        wvlarray = np.asarray(self.wvl)
        
        intearray = np.asarray(self.inte)
        
        return self.customConcatenate(wvlarray,intearray)
    
    def customConcatenate(self,firstColumn: np.array, secondColumn: np.array):
        
        sizeColumn = int(np.size(firstColumn))
        
        result = np.zeros((sizeColumn,2), dtype = float)
        
        for idxfirst, firstel in enumerate(firstColumn):
            
            result[idxfirst,0] = firstel
            result[idxfirst,1] = secondColumn[idxfirst]   
            
        return result
    
if __name__ == "__main__":
    
    spectrumIdx = random.randint(0, 1)
    
    if spectrumIdx == 0:
        
        data = genfromtxt('SpectrumGlassy.csv', delimiter=',')  
        
    else:
        
        data = genfromtxt('SpectrumBeta.csv', delimiter=',')
        
    recordedSpectrum = Spectrum(data[:,0],data[:,1])
    
    SpectrumToWrite = recordedSpectrum.toArray()
    
    print('here to break')
