# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

from AcquirerARPL import acquirerARPL
import ImageDisplayer as imd
from PIL import ImageQt, Image
import numpy as np
import os
import pickle

#all the different files are interpolated to ensure that they can be treated against each other
from scipy import interpolate

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

class ARPLDataPreviewer(QObject):  
    
    sig_image = pyqtSignal(ImageQt.ImageQt)
    
    def __init__(self, current_acquirer, rawFolder):   

        super().__init__()
        
        #Planck Constant in m2 kg s-1
        
        #self.h = 6.62607004 * (1/(np.power(10,34)))
        self.h = 6.62
        
        #light speed in m s-1
        
        #self.c = 3*(np.power(10,8))
        self.c = 3
        
        #convert energy
        
        #self.ConvertEv = 1.60218 * (1/(np.power(10,19))))
        self.ConvertEv = 1.60218
        
        self.imageMaker = imd.QImageMaker()
        
        self.Angles = current_acquirer.Angles        
        
        self.rawFolder = rawFolder         
        
        #bckgdFolder is created by the dataHandler
        
        self.bckgdFolder = '{}\\Bckgd'.format(self.rawFolder[:-4])             
        
        #NormW Folder is created by the dataHandler
        
        self.NormWFolder = '{}\\NormW'.format(self.rawFolder[:-4])
        
        self.folderCreation(self.NormWFolder)
        
        #The spectraW folder is dedicated to the measured spectra in wavelength without correction, with background correction
        
        self.spectraWFolder = '{}\\SpectraW'.format(rawFolder[:-4])
        
        self.folderCreation(self.spectraWFolder)          
        
        #The spectraE folder is dedicated to the measured spectra in energy without Jacobian correction
        
        self.spectraEFolder = '{}\\SpectraE'.format(rawFolder[:-4])
        
        self.folderCreation(self.spectraEFolder)  
        
        #The spectraEJacob folder is dedicated to the measured spectra in energy with Jacobian correction
        
        self.spectraEJacobFolder = '{}\\SpectraEJacob'.format(rawFolder[:-4])
        
        self.folderCreation(self.spectraEJacobFolder)
        
        #The NormE folder is dedicated to the spectra normalised at their maxima in energy without Jacobian correction
        
        self.NormEFolder = '{}\\NormE'.format(rawFolder[:-4])
        
        self.folderCreation(self.NormEFolder)
        
        #The NormEJacob folder is dedicated to the spectra normalised at their maxima in energy without Jacobian correction
        
        self.NormEJacobFolder = '{}\\NormEJacobFolder'.format(rawFolder[:-4])
        
        self.folderCreation(self.NormEJacobFolder)  
        
        #The pickle folder is dedicated to compatibility with the TMM algorithm code
        
        self.pickleFolder = '{}\\Pickle'.format(rawFolder[:-4])
        
        self.folderCreation(self.pickleFolder)
                       
    def folderCreation(self, folderPath):
        
        if not os.path.exists(folderPath):
            
            os.mkdir(folderPath)
                     
            return
            
        else: 
            
            return        
        
    def firstConnection(self):
        
        self.sig_image.emit(self.imageMaker.greyDefault()) 
        
    @pyqtSlot(float)  
        
    def analyzeData(self, angle):
        
        lookingforname = '{}.csv'.format(str(angle))
        
        for filename in os.listdir(self.rawFolder):
            
            if filename == lookingforname:
        
                filepath = '{}\\{}'.format(self.rawFolder,filename)
                
                break
            
        for filename in os.listdir(self.bckgdFolder):
            
            if filename == lookingforname:
        
                filepathBckgd = '{}\\{}'.format(self.bckgdFolder,filename)
                
                break
        
        rawdata = np.genfromtxt(filepath, delimiter=',')
        
        backgrounddata = np.genfromtxt(filepathBckgd, delimiter=',')
        
        correctedData = np.zeros_like(rawdata)
        
        correctedData[:,0] = rawdata[:,0]
        
        #the very first correction looks for the corresponding background file and substracts 
        
        for IndexCorrection, element in enumerate(rawdata):
            
            correctedData[IndexCorrection,1] = np.absolute(rawdata[IndexCorrection,1] - backgrounddata[IndexCorrection,1])
        
        spectraWdata = correctedData       
        
        targetNameW = '{}\{}'.format(self.spectraWFolder,filename)  
        
        np.savetxt(targetNameW, spectraWdata, delimiter =",")
            
        #conversion to energy
        
        spectraEdata = np.zeros_like(spectraWdata)
        
        spectraEJacobdata = np.zeros_like(spectraWdata)
        
        spectraWNormdata = np.zeros_like(spectraWdata)
        
        spectraENormdata = np.zeros_like(spectraWdata)

        spectraENormJacobdata = np.zeros_like(spectraWdata)        
        
        spectraEdata[:,1] = spectraWdata[:,1]
                
        for idx, element in enumerate(spectraEdata[:,1]):
            
            spectraEdata[idx,0] = (1239.82 / spectraWdata[idx,0])
            
        #flip the data to obtain increasing energies
        
        spectraEdata = np.flip(spectraEdata, 0)
        
        #fill the Jacobian corrected data
        
        spectraEJacobdata[:,0] = spectraEdata[:,0]
        
        hc = (self.h * self.c)
        
        for idx, element in enumerate(spectraEdata[:,1]):
            
            spectraEJacobdata[idx,1] = (hc/((spectraEdata[idx,0] * self.ConvertEv) ** 2)) * spectraEJacobdata[idx,1]
            
        #perform the normalizations on the different sets
        
        # on Wavelength spectra
        
        spectraWNormdataValues = self.normalizeVals(spectraWdata[:,1])
        
        spectraWNormdata = np.zeros_like(spectraWdata)
        
        spectraWNormdata[:,0] = spectraWdata[:,0]
        
        spectraWNormdata[:,1] = spectraWNormdataValues
        
        # on Energy spectra without Jacobian correction
        
        spectraENormdataValues = self.normalizeVals(spectraEdata[:,1])
        
        spectraENormdata = np.zeros_like(spectraEdata)
        
        spectraENormdata[:,0] = spectraEdata[:,0]
        
        spectraENormdata[:,1] = spectraENormdataValues   
        
        # on Energy spectra with Jacobian correction
        
        spectraENormJacobdataValues = self.normalizeVals(spectraEJacobdata[:,1])
        
        spectraENormJacobdata = np.zeros_like(spectraEdata)
        
        spectraENormJacobdata[:,0] = spectraEdata[:,0]
        
        spectraENormJacobdata[:,1] = spectraENormJacobdataValues         
        
        #save the spectra in their respective folders
        
        targetNameE = '{}\{}'.format(self.spectraEFolder,filename)
        
        targetNameEJacob = '{}\{}'.format(self.spectraEJacobFolder,filename)
        
        targetNameNormW = '{}\{}'.format(self.NormWFolder, filename)
        
        targetNameNormE = '{}\{}'.format(self.NormEFolder, filename)
        
        targetNameNormEJacobData = '{}\{}'.format(self.NormEJacobFolder, filename)
        
        np.savetxt(targetNameE, spectraEdata, delimiter =",")
        
        np.savetxt(targetNameEJacob, spectraEJacobdata, delimiter =",")
        
        np.savetxt(targetNameNormEJacobData, spectraENormJacobdata, delimiter =",")   
        
        np.savetxt(targetNameNormE, spectraENormdata, delimiter =",")
        
        np.savetxt(targetNameNormW, spectraWNormdata, delimiter =",")          
        
        #update the data as pickle for compatibility with the transfer matrix code
        #will create all the corresponding pickle for the folders

        self.updatePickle('dataW', angle, spectraWdata)
        
        self.updatePickle('dataE', angle, spectraEdata)
        
        self.updatePickle('dataEJacob', angle, spectraEJacobdata)
        
        self.updatePickle('dataENormJacob', angle, spectraENormJacobdata)
        
        self.updatePickle('dataWNormJacob', angle, spectraWNormdata)
            
    @pyqtSlot(float)                           
    
    def makePreviewImage(self):
        
        filelist = os.listdir(self.spectraEFolder)
        
        filecounter = len(filelist)
        
        if filecounter == 0:
            
            self.sig_image.emit(self.imageMaker.greyDefault()) 
            
            return
        
        else:
            
            ##load first Angle
            
            firstAngle = self.Angles[0]
            
            lookingforname = '{}.csv'.format(str(firstAngle))
            
            for file in filelist:
                    
                    if file == lookingforname:
                
                        firstpath = '{}\\{}'.format(self.spectraEFolder, file)
                        
                        break  
                            
            firstdata = np.genfromtxt(firstpath, delimiter=',')
            
            #find the energies
            
            eN = firstdata[:,0] 
            
            #form the initial image
            
            self.numberOfEnergies = len(eN)
            
            self.numberOfAngles = len(self.Angles)
            
            img = Image.new( 'RGB', (self.numberOfEnergies,self.numberOfAngles), "grey") # Create a new grey image
            
            pixels = img.load()            
            
            #colour the first column
            
            toFillRed, toFillGreen, toFillBlue = self.colour(firstdata[:,1],0)
            
            for idX, toFill in enumerate(toFillRed):
        
                pixels[idX,0] = (int(toFill),0,0) 

            #work on following angles
            
            for idxAngle, angle in enumerate(self.Angles):
                
                if idxAngle > 0 :
                
                    lookingforname = '{}.csv'.format(str(angle))  
                    
                    filepath = 'none'
            
                    for file in filelist:
                    
                        if file == lookingforname:
                
                            filepath = '{}\\{}'.format(self.spectraEFolder, file)
                        
                        if filepath != 'none':
                            
                            data = np.genfromtxt(filepath, delimiter=',')          
            
                            #colour the column
            
                            toFillRed, toFillGreen, toFillBlue = self.colour(data[:,1],0)
            
                            for idX, toFill in enumerate(toFillRed):
        
                                pixels[idX,idxAngle] = (int(toFill),0,0) 
                                
            img.show()

            self.sig_image.emit(ImageQt.ImageQt(img))
            
            return
                
    def find_nearest(self, array, value):
            
        idx = (np.absolute(array - value)).argmin()
            
        return idx
                
    def colour(self, valuecolumn, colourmap): #the value is between 0 and 1, colourmap to be defined
        
        RedPixels = np.zeros_like(valuecolumn)
        otherColors = np.zeros
        
        for idxValue, value in enumerate(valuecolumn):
            
            if value > 1:
        
                value == 1
            
                #for now purely red
    
            max = 255
        
            RedPixels[idxValue]  = int(round(max * value))
        
        return (RedPixels,otherColors,otherColors)
    
    def returnAngleIdx(self,angle):
        
        for idx, value in enumerate(self.Angles):
            
            if value == angle:
                
                return idx
            
    def replaceColumn(self, position, intensitiesAlreadyAcq, NewIntensities):                
        
        for idx, value in enumerate(NewIntensities):
            
            intensitiesAlreadyAcq[idx,position] = NewIntensities[idx]
            
        return intensitiesAlreadyAcq
    
    def normalizeVals(self, intensities):
        
        normalizedIntensities = np.zeros_like(intensities)
        
        maximum = np.amax(intensities)
        
        for idx, element in enumerate(intensities):
            
            normalizedIntensities[idx] = intensities[idx]/maximum
        
        return normalizedIntensities
    
    def updatePickle(self, dataFileName, angle, spectradata):
        
        fileExists = False
        
        fileExists = self.lookForFile(dataFileName)
        
        if fileExists == True:
               
            with open(str(self.pickleFolder + '\\{}.txt'.format(dataFileName)), 'rb') as f:
               
                packed = pickle.load(f)
                Z = packed[2]  
        
            #add the new Z column
            
            angleIdx  = self.returnAngleIdx(angle)
            
            Z = self.replaceColumn(angleIdx, Z, spectradata[:,1])
            
            with open(str(self.pickleFolder + '\\{}.txt'.format(dataFileName)), 'wb') as f:
                          
                packedData = self.Angles, spectradata[:,0], Z
                pickle.dump(packedData, f)
                
        else:
            
            Z = np.zeros((len(spectradata[:,0]),len(self.Angles)))             
            
            Z = self.replaceColumn(0, Z, spectradata[:,1])
            
            with open(str(self.pickleFolder + '\\{}.txt'.format(dataFileName)), 'wb') as f:
                    
                packedData = self.Angles, spectradata[:,0], Z
                pickle.dump(packedData, f)   
                
    def lookForFile(self,dataFile):
        
        patht = str(self.pickleFolder + '\\{}.txt'.format(dataFile))
        
        if os.path.exists(patht):
            
            return True 
        
        else:
            
            return False
    
if __name__ == "__main__":
    
    #testFolderPath = 'C:\\Users\\leroux\\Documents\\TestH3\\Raw'
        
    #local_acquirer = acquirer(10, 20, 1, 10)
        
    #local_previewer = dataPreviewer(local_acquirer, testFolderPath)
        
    #local_previewer.makePreviewImage()
    
    #local_acquirer = acquirerARPL(10, 15, 5, 10)
        
    #local_previewer = ARPLDataPreviewer(local_acquirer, 'C:\\Users\\leroux\\Documents\\ARPL Data Treated\\tyhe\\Raw')
    
    #local_previewer.analyzeData(10.0)
    
    #local_previewer.analyzeData(15.0) 
    
    local_acquirer = acquirerARPL(-40, 60, 1, 10)
        
    local_previewer = ARPLDataPreviewer(local_acquirer, 'C:\\Users\\leroux\\Desktop\\Good Data\\FullDataSetsARPL\\RealB1Exp12TEExc450A75 - AcTime 1s\\Raw')
    
    Angles = np.linspace(-40, 60, 101) 
    
    for angle in Angles:
        
        local_previewer.analyzeData(angle)
    
        
        
                        
                        
                                 
                
                
                
                
                