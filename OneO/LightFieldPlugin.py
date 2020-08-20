# Import the .NET class library
import clr

# Import python sys module
import sys

# Import os module
import os

import glob

import time

# Import c compatible List and String
from System import String
from System.Collections.Generic import List

import random
from numpy import genfromtxt
from Spectrometry import Spectrum

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('System.IO')
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import ExperimentSettings

#PyQt imports
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot

#avoid crash with PyQt
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2


class LFPlugin(QObject):
    
    sig_msg = pyqtSignal(str)
    sigcnection = pyqtSignal(bool)
    sig_spectrum = pyqtSignal(Spectrum)

    def experiment_isReadyToRunChanged(self,sender, event_args):
        if (experiment.IsReadyToRun):
            # No Errors in LightField
            self.sig_msg.emit('\n\tLightField is Ready to Run\n')
        else:
            # For testing purposes set the exposure time
            # to a negative value (e.g. -9)
            self.sig_msg.emit('\n\tLightField is Not Ready to Run\n')
    
    def lightField_closing(self,sender, event_args):
        unhook_event()        
            
    def unhook_event(self):
        # Unhook the eventhandler for IsReadyToRunChanged
        # Will be called upon exiting
        experiment.IsReadyToRunChanged -= experiment_isReadyToRunChanged    
        auto.LightFieldClosing -= lightField_closing    
        self.sig_msg.emit("handlers unhooked")
    
    def device_found(self):
        # Find connected device
        for device in self.experiment.ExperimentDevices:
            if (device.Type == DeviceType.Camera):
                return True
         
        # If connected device is not a camera inform the user
        self.sig_msg.emit("Camera not found. Please add a camera and try again.")
        return False        
    
    
    def __init__(self):
        
        super().__init__()
        self.assignSavingFolder()

    def assignSavingFolder(self):
        
        #by default the spectrometer creates a new folder with the date and records its file in:
        
        defaultSpectrometerFolder = 'C:\\Users\\leroux\\Desktop\\Spectrometer Acquisition'
        
        from os import walk
        
        f=[]
        
        currentmax = 0
        
        savingFoldername = '0'
        
        for (dirpath, dirnames, filenames) in walk(defaultSpectrometerFolder):
        
            for dirname in dirnames:
                
                if int(dirname) >= currentmax:
                    
                    currentmax = int(dirname)+1

            savingFoldername = str(currentmax)
            
        os.makedirs('{}\\{}'.format(defaultSpectrometerFolder,savingFoldername))  
        
        self.savingFolder = '{}\\{}'.format(defaultSpectrometerFolder,savingFoldername)
        
    @pyqtSlot()
    def equipmentScanAndConnect(self):
            
        # Create the LightField Application (true for visible)
        # The 2nd parameter forces LF to load with no experiment 
        self.auto = Automation(True, List[String]())
        
        # Get experiment object
        self.experiment = self.auto.LightFieldApplication.Experiment
        
        # Set the folder for exported files
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationDirectory, self.savingFolder)	          
        
        # Set the base file name
        self.experiment.SetValue(
                ExperimentSettings.FileNameGenerationBaseFileName,
                'Measurement')
    
        # Option to Increment, set to false will not increment
        self.experiment.SetValue(
                ExperimentSettings.FileNameGenerationAttachIncrement,
                True)
    
        # Option to add date
        self.experiment.SetValue(
                ExperimentSettings.FileNameGenerationAttachDate,
                True)
    
        # Option to add time
        self.experiment.SetValue(
                ExperimentSettings.FileNameGenerationAttachTime,
                True)            
        
        if (self.device_found()==True):        
            # Hook the eventhandler for IsReadyToRunChanged
            self.experiment.IsReadyToRunChanged += self.experiment_isReadyToRunChanged
        
            # Hook the eventhandler for LightField Closing
            #.auto.LightFieldClosing += self.lightField_closing  
        
        self.sigcnection.emit(True)
    
    @pyqtSlot()    
    def recordSpectrum(self):
        
        spectrumFileName = self.AcquireReturningName()
            
        data = genfromtxt(spectrumFileName, delimiter=',')
            
        recordedSpectrum = Spectrum(data[:,0],data[:,1])
            
        self.sig_spectrum.emit(recordedSpectrum)  
        
    def AcquireReturningName(self):
        
        self.experiment.Acquire()

        time.sleep(5)
        
        list_of_files = glob.glob('{}\\*.csv'.format(self.savingFolder)) # * means all if need specific format then *.csv
        
        latest_file = max(list_of_files, key=os.path.getctime) 
        
        return latest_file
   
    @pyqtSlot()
    def close(self):    
        
        #necessary to not crash   
        os.system("taskkill /f /im  AddInProcess.exe")
        
        self.sig_msg.emit('LightField has correctly been turned off.')

        #Result: user informed when LightField is ready to run 
        
        

