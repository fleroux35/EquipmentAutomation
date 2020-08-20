# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

#Careful, the stage direction is opposite to the final output map
#The actual map records from the top left line by line horizontally
#when it changes line the direction is changed to ensure the stage is making
#small movements. The movements here are absolute to try and rely on the sensors.

from Mapper import mapper
import ImageDisplayer as imd
from PIL import ImageQt, Image
import numpy as np
import os

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

class dataMapper(QObject):  
    
    sig_image = pyqtSignal(ImageQt.ImageQt)
    
    def __init__(self, current_mapper: mapper, rawFolder):

        super().__init__()
        
        self.numberOfXCells = current_mapper.numberOfXCells
        self.numberOfYCells = current_mapper.numberOfYCells
        
        self.rawFolder = rawFolder
        
        self.normalizeFolder = '{}\\Norm'.format(rawFolder[:-4])
        
        self.normalizefolderCreation()
        
        self.imageMaker = imd.QImageMaker()
        
    def normalizefolderCreation(self):
        
        if not os.path.exists(self.normalizeFolder):
            
            os.mkdir(self.normalizeFolder)
                     
            return
            
        else: 
            
            return     
        
    def firstConnection(self):
        
        self.sig_image.emit(self.imageMaker.greyDefault()) 
        
    @pyqtSlot(int,int)  
        
    def normalizeFile(self, X:int, Y:int):
        
        lookingforname = 'Xstep{}_Ystep{}'.format(X,Y)
        
        for filename in os.listdir(self.rawFolder):
            
            atposition = int(filename.find('@'))
            
            if filename[:atposition] == lookingforname:
                
                lookingforname = filename
        
                filepath = '{}\\{}'.format(self.rawFolder,filename)
                
                break
        
        fulldata = np.genfromtxt(filepath, delimiter=',')
        
        intensities = fulldata[:,1]
        
        maximum = np.amax(intensities)
        
        for idx, element in enumerate(intensities):
            
            fulldata[idx,1] = fulldata[idx,1]/maximum
        
        targetName = '{}\{}'.format(self.normalizeFolder,filename)
        
        np.savetxt(targetName, fulldata, delimiter=",")
    
    def makePreviewImage(self, wavelength: float):
        
        filelist = os.listdir(self.normalizeFolder)
        filecounter = len(filelist)
        
        if filecounter == 0:
            
            self.sig_image.emit(self.imageMaker.greyDefault()) 
            
            return
        
        else:
            
            img = Image.new( 'RGB', (self.numberOfXCells,self.numberOfYCells), "grey") # Create a new grey image
            
            pixels = img.load()
            
            #use the first file to find the correct Index
            
            firstpath = '{}\\{}'.format(self.normalizeFolder,filelist[0])
                            
            firstdata = np.genfromtxt(firstpath, delimiter=',')
            
            wvl = firstdata[:,0] 
            
            wvlIdx = self.find_nearest(wvl,wavelength)

            for filename in filelist:
                
                filepath = '{}\\{}'.format(self.rawFolder,filename)
                
                filedata = np.genfromtxt(filepath, delimiter=',') 
            
                YStepidx = int(filename.find('Ystep'))
                
                atposition = int(filename.find('@'))
                
                X = int(filename[5:(YStepidx-1)])
                
                Y = int(filename[YStepidx+5:atposition])
                
                pixels[X,Y] = self.colour(filedata[wvlIdx,1],0)
                
            #img.show()
                
            self.sig_image.emit(ImageQt.ImageQt(img))
            
            return
                
    def find_nearest(self, array, value):
            
        idx = (np.abs(array - value)).argmin()
            
        return idx
                
    def colour(self,value:float,colourmap): #the value is between 0 and 1, colourmap to be defined
        #for now purely red
    
        max = 255
        
        colourRedPix  = int(round(max * value))
        
        return (colourRedPix,0,0)
        
                             
if __name__ == "__main__":
    
    local_dataMapper = dataMapper(mapper(100, 100, 0.15, 0.15, 50, 50, 25), 'C:\\Users\\leroux\\Desktop\\Main\\Test\\1\\Raw')
    
    #local_dataMapper.normalizeFile(0, 0)
    
    local_dataMapper.makePreviewImage(424)
    
    local_dataMapper.makePreviewImage(438)
                        
    
                        
                        
                                 
                
                
                
                
                