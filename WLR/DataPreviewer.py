# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

from Acquirer import acquirer
import ImageDisplayer as imd
from PIL import ImageQt, Image
import numpy as np
import os
import pickle

#all the different files are interpolated to ensure that they can be treated against each other
from scipy import interpolate

from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QCoreApplication

class dataPreviewer(QObject):  
    
    sig_image = pyqtSignal(ImageQt.ImageQt)
    
    def __init__(self, current_acquirer, rawFolder):

        super().__init__()
        
        self.rawFolder = rawFolder
        
        #refFolder is created by the dataHandler
        self.refFolder = '{}\\Ref'.format(self.rawFolder[:-4])
        
        self.imageMaker = imd.QImageMaker()
        
        self.AnglesTheta = current_acquirer.AnglesTheta
        
        self.AnglesPhi = current_acquirer.AnglesPhi
            
        self.spectraWFolder = '{}\\SpectraW'.format(rawFolder[:-4])
        
        self.folderCreation(self.spectraWFolder)
          
        self.spectraEFolder = '{}\\SpectraE'.format(rawFolder[:-4]) 
        
        self.folderCreation(self.spectraEFolder)
    
        self.pickleFolder = '{}\\Pickle'.format(rawFolder[:-4])  
        
        self.folderCreation(self.pickleFolder)
        
        #The spectra folders are dedicated to the measured reflection spectra in wavelength
        
        for phiangle in self.AnglesPhi:
            
            spectraWFolderAtPhi = '{}\\{}'.format(self.spectraWFolder, phiangle)
        
            self.folderCreation(spectraWFolderAtPhi)
        
            #The spectra folders are dedicated to the measured reflection spectra in energy
        
            spectraEFolderAtPhi = '{}\\{}'.format(self.spectraEFolder, phiangle)
        
            self.folderCreation(spectraEFolderAtPhi)        
        
            #The pickle folder is dedicated to compatibility with the TMM algorithm code
            
            pickleFolderAtPhi = '{}\\{}'.format(self.pickleFolder, phiangle)
        
            self.folderCreation(pickleFolderAtPhi)
        
    def folderCreation(self, folderPath):
        
        if not os.path.exists(folderPath):
            
            os.mkdir(folderPath)
                     
            return
            
        else: 
            
            return        
        
    def firstConnection(self):
        
        self.sig_image.emit(self.imageMaker.greyDefault()) 
        
    @pyqtSlot(float)       
    
    def AnalyzeRef(self, anglePosition):
        
        knownRef = np.genfromtxt(str(self.refFolder + '\\knownReferenceAt{}.csv'.format(anglePosition)), delimiter=",")
        
        measuredRef = np.genfromtxt(str(self.refFolder + '\\measuredReferenceAt{}.csv'.format(anglePosition)), delimiter=",") 
        
        #interpolation using spline
        
        interpKnownRef = interpolate.InterpolatedUnivariateSpline(knownRef[:,0], knownRef[:,1])
        
        interpMeasuredRef = interpolate.InterpolatedUnivariateSpline(measuredRef[:,0], measuredRef[:,1])
        
        MeasuredIntensities = measuredRef[:,1]
        
        #the saved file will be a file directly comparable to the current measurement (i.e. the spline is called
        #on all points where an intensity is read and saved)
        
        idealValuesComparison = measuredRef
        
        for idx, wvl in enumerate(measuredRef[:,0]): 
            
            idealValuesComparison[idx,1] = measuredRef[idx,1] * (1/interpKnownRef(wvl))
        
        IdealFilePath = str(self.refFolder + '\\IdealIntensityAt{}.csv'.format(anglePosition))
        
        np.savetxt(IdealFilePath, idealValuesComparison, delimiter=",")        
                   
    @pyqtSlot(float,float)  
        
    def analyzeData(self, angleTheta, anglePhi):
        
        self.rawPhiFolder = str(self.rawFolder + '\\{}'.format(anglePhi))
        
        lookingforname = '{}.csv'.format(str(angleTheta))
        
        for filename in os.listdir(self.rawPhiFolder):
            
            if filename == lookingforname:
        
                filepath = '{}\\{}'.format(self.rawPhiFolder,filename)
                
                break
        
        rawdata = np.genfromtxt(filepath, delimiter=',')
        
        intensities = rawdata[:,1]
        
        spectraWdata = rawdata
        
        #correct against the ideal intensity, will save in wavelength. The ref is supposed to be symmetric relative to the out of plane sample vector
     
        IdealFilePath = str(self.refFolder + '\\IdealIntensityAt{}.csv'.format(str(angleTheta)))
        
        idealValuesComparison = np.genfromtxt(IdealFilePath, delimiter=",")       
        
        for idx, element in enumerate(intensities):
            
            spectraWdata[idx,1] = spectraWdata[idx,1]/idealValuesComparison[idx,1]
            
        #conversion to energy
        
        spectraEdata = np.zeros_like(spectraWdata)
        
        spectraEdata[:,1] = spectraWdata[:,1]
        
        for idx, element in enumerate(intensities):
            
            spectraEdata[idx,0] = (1239.82/spectraWdata[idx,0])
            
        #flip the data to obtain increasing energies
        
        spectraEdata = np.flip(spectraEdata,0)
        
        #save the spectra in their respective folders
        
        targetNameW = '{}\\{}\\{}'.format(self.spectraWFolder, anglePhi, filename)
        
        targetNameE = '{}\\{}\\{}'.format(self.spectraEFolder, anglePhi, filename)
        
        np.savetxt(targetNameW, spectraWdata, delimiter=",")
        
        np.savetxt(targetNameE, spectraEdata, delimiter=",")
        
        #update the data as pickle for compatibility with the transfer matrix code
        
        pickleFolderAtPhi = '{}\\{}'.format(self.pickleFolder, anglePhi)
        
        if len(os.listdir(pickleFolderAtPhi)) > 0:
               
            with open(str(pickleFolderAtPhi + '\\data.txt'), 'rb') as f:
               
                packed = pickle.load(f)
                Z = packed[2]  
        
            #add the new Z column
            
            angleIdx  = self.returnAngleIdx(angleTheta)
            
            Z = self.replaceColumn(angleIdx, Z, spectraEdata[:,1])
            
            with open(str(pickleFolderAtPhi + '\\data.txt'), 'wb') as f:
                          
                packedData = self.AnglesTheta, spectraEdata[:,0], Z
                pickle.dump(packedData, f)
                
        else:
            
            Z = np.zeros((len(spectraEdata[:,0]),len(self.AnglesTheta)))             
            
            Z = self.replaceColumn(0, Z, spectraEdata[:,1])
            
            with open(str(pickleFolderAtPhi + '\\data.txt'), 'wb') as f:
                    
                packedData = self.AnglesTheta, spectraEdata[:,0], Z
                pickle.dump(packedData, f)
            
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
            
            for idxAngle, angle in enumerate(self.AnglesTheta):
                
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
            
        idx = (np.abs(array - value)).argmin()
            
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
        
        for idx, value in enumerate(self.AnglesTheta):
            
            if value == angle:
                
                return idx
            
    def replaceColumn(self, position, intensitiesAlreadyAcq, NewIntensities):                
        
        for idx, value in enumerate(NewIntensities):
            
            intensitiesAlreadyAcq[idx,position] = NewIntensities[idx]
            
        return intensitiesAlreadyAcq
    
if __name__ == "__main__":
    
    #testFolderPath = 'C:\\Users\\leroux\\Documents\\TestH3\\Raw'
        
    #local_acquirer = acquirer(10, 20, 1, 10)
        
    #local_previewer = dataPreviewer(local_acquirer, testFolderPath)
        
    #local_previewer.makePreviewImage()
    
    local_acquirer = acquirer(10, 70, 73, 183, 10, 10)
        
    local_previewer = dataPreviewer(local_acquirer, 'C:\\Users\\leroux\\Documents\\Experimental Data Treated\\S1E11TEFollowingPhi - Work On ref\\Raw')
    
    AnglesTheta = np.linspace(10, 70, 7)
    AnglesPhi = np.linspace(73, 183, 12) 
    
    for anglephi in AnglesPhi:
        
        for angletheta in AnglesTheta:
        
            local_previewer.analyzeData(angletheta,anglephi)

        
                        
                        
                                 
                
                
                
                
                