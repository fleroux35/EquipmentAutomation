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

class WLRDataHandler(QObject): 
    
    sig_msg = pyqtSignal(str)
    sig_image = pyqtSignal(ImageQt.ImageQt)
    sig_askForDataTreatment = pyqtSignal(float,float)
    sig_askForRefAnalysis = pyqtSignal(float)
    
    #The reference folders are for the mirror for a polarizer either vertical or horizontal
    
    pathToRefVerticalPolarizer = 'C:\\Users\\leroux\\Desktop\\MainWLR\\V'
    pathToRefHorizontalPolarizer = 'C:\\Users\\leroux\\Desktop\\MainWLR\\H'
    previousRefFolderV = 'C:\\Users\\leroux\\Documents\\CurrentRef\\UseMeTE'
    previousRefFolderH = 'C:\\Users\\leroux\\Documents\\CurrentRef\\UseMeTM'
    
    def __init__(self, acquisitionFolder):

        super().__init__()

        self.acquisitionFolder = acquisitionFolder
        
        self.refFolder = '{}\\Ref'.format(self.acquisitionFolder[:-4])
        
        self.folderCreation(self.refFolder)         
        
    @pyqtSlot(Spectrum, float, str) 
        
    def saveReference(self, refSpectrum:Spectrum, anglePosition:float, polarizationDirection:str):
        
        #The ref folder is dedicated to the spectra of the reference
        
        if polarizationDirection == 'V':    
            
            self.knownReflection = self.findAngleRefFile(self.pathToRefVerticalPolarizer, anglePosition)
            
        else:
            
            self.knownReflection = self.findAngleRefFile(self.pathToRefHorizontalPolarizer, anglePosition)
        
        np.savetxt(str(self.refFolder + '\\knownReferenceAt{}.csv'.format(anglePosition)), self.knownReflection, delimiter=",")
        
        np.savetxt(str(self.refFolder + '\\measuredReferenceAt{}.csv'.format(anglePosition)), refSpectrum.toArray(), delimiter=",")
        
        self.sig_askForRefAnalysis.emit(anglePosition)
        
    @pyqtSlot(Spectrum, float, float)   
        
    def saveLastSpectrum(self,lastSpectrum:Spectrum, angleTheta:float, anglePhi:float):
        
        if os.path.exists(str(self.acquisitionFolder + '\\{}'.format(anglePhi))) is False:
            
            self.createPhiFolder(anglePhi)
        
        currentName = str(self.acquisitionFolder + '\\{}\\{}.csv'.format(anglePhi, angleTheta))
        
        np.savetxt(currentName, lastSpectrum.toArray(), delimiter=",")
        
        self.sig_msg.emit(currentName.strip()) 
        
        self.sig_askForDataTreatment.emit(angleTheta, anglePhi)
        
    def createPhiFolder(self, anglePhi):
        
        self.folderCreation(str(self.acquisitionFolder + '\\{}'.format(anglePhi)))
    
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
        
    @pyqtSlot(str)
              
    def copyRefFolder(self,polarization):
        
        if polarization == 'V':
        
            src = 'C:\\Users\\leroux\\Documents\\CurrentRef\\UseMeTE\\Ref'
            
        if polarization == 'H':
            
            src = 'C:\\Users\\leroux\\Documents\\CurrentRef\\UseMeTM\\Ref'
                
        oldref_files = os.listdir(src)
        
        for file_name in oldref_files:
            
            full_file_name = os.path.join(src, file_name)
            
            if os.path.isfile(full_file_name):
                
                shutil.copy(full_file_name,self.refFolder)

if __name__ == "__main__":
            
    dataHandler = WLRDataHandler('C:\\Users\\leroux\\Desktop\\MainWLR\\Test\\1\\Raw')
    
    refSpectrum = Spectrum([0], [0])
    dataHandler.saveReference(refSpectrum, 'H')