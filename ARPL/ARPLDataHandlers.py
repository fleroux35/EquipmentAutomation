# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

#the handler saves data and knows where the reference spectrum is stored,
#it handles its copy into the current acqusition folder

import math as m
import numpy as np
import time
import os
import shutil

from PIL import ImageQt

from Spectrometry import Spectrum

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot

class ARPLDataHandler(QObject): 
    
    sig_msg = pyqtSignal(str)
    sig_image = pyqtSignal(ImageQt.ImageQt)
    sig_askForDataTreatment = pyqtSignal(float) 
    
    previousBckgdFolder = 'C:\\Users\\leroux\\Documents\\CurrentBckgd\\UseMe'
    
    def __init__(self, acquisitionFolder):

        super().__init__()

        self.acquisitionFolder = acquisitionFolder
        
        self.bckgdFolder = '{}\\Bckgd'.format(self.acquisitionFolder[:-4])
        
        self.folderCreation(self.bckgdFolder)          
        
    @pyqtSlot(Spectrum, float)    
        
    def saveLastSpectrum(self, lastSpectrum:Spectrum, Angle:float):
        
        currentName = str(self.acquisitionFolder + '\\{}.csv'.format(Angle))
        
        self.sig_msg.emit(currentName.strip())
        
        np.savetxt(currentName, lastSpectrum.toArray(), delimiter=",")
        
        #self.sig_askForDataTreatment.emit(Angle)       
        
    @pyqtSlot(Spectrum, float) 
        
    def saveLastBckgd(self, bckgdSpectrum:Spectrum, anglePosition:float):

        currentName = str(self.bckgdFolder + '\\{}.csv'.format(anglePosition))
        
        self.sig_msg.emit(currentName.strip())
        
        np.savetxt(currentName, bckgdSpectrum.toArray(), delimiter=",")       
        
    def findAngleRefFile(self, pathToRef, anglePosition):
        
        nameToFind = str(pathToRef + '\\{}.csv'.format(anglePosition))
        
        print('Working on: {}'.format(anglePosition))
        
        fileToFind = np.genfromtxt(nameToFind, delimiter=",")
        
        return fileToFind
        
    def folderCreation(self, folderPath):
        
        if not os.path.exists(folderPath):
            
            os.mkdir(folderPath)
                     
            return
            
        else: 
            
            return  
        
    @pyqtSlot()
              
    def copyBckgdFolder(self):
        
        src = 'C:\\Users\\leroux\\Documents\\CurrentBckgd\\UseMe\\Bckgd'
        
        oldref_files = os.listdir(src)
        
        for file_name in oldref_files:
            
            full_file_name = os.path.join(src, file_name)
            
            if os.path.isfile(full_file_name):
                
                shutil.copy(full_file_name,self.bckgdFolder)
        
if __name__ == "__main__":
            
    print('write Unit Test.')