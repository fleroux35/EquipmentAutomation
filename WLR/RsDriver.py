"""
Module for interacting with the Rotating Stage

Authors:  Florian <florian dot leroux at physics dot ox dot ac dot uk> /Ross <peregrine dot warren at physics dot ox dot ac dot uk>
"""

from ctypes import *
import time
import os
import sys
import tempfile
import re

if sys.version_info >= (3,0):
    import urllib.parse
    
cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_package_dir = cur_dir
sys.path.append(ximc_package_dir)  # add ximc.py wrapper to python path
libdir = cur_dir
os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll

try: 
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the testpython.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    print ("Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    exit()      


class RsDriver():
    
    #Class for Rotating Stage Control.  
    
    def __init__(self, TopOrBottom):
        
        
        #Make instrument connection to Top or Bottom Axis on calling class.     
    
        # isTop is a boolean equal to 0 if Top axis or 1 Bottom axis
        
        self.lib = lib
        self.TopOrBottom = TopOrBottom 
        self.dev_count = 0
        self.devenum = 0
        self.currentAngle = 0
        self.SafePosition = 10 #minimum incidence angle in a reflection configuration where the optics are safe
        self.MaxPosition = 100 #safety in order to not go to far and damage the optics.
    
        
        if self.TopOrBottom == 0: #Top Axis
        
            self.NormalIncidenceStep = 0
        
        else: #Bottom Axis
        
            self.NormalIncidenceStep = 0

        try:
        
            self.scanDevices()
        
        except:
            
            print("ConnectionError: Scan Failed, please check connections or switch to XIlab for manual scan") 
        
        if self.dev_count > 0:
        
            try:
            
                self.makeConnection()
                
                if self.TopOrBottom == 0:
                    
                    print('Connection to Top Arm successful')
                    
                if self.TopOrBottom == 1:
                    
                    print('Connection to Bottom Arm successful')
            
            except: 
                
                print("ConnectionError: Could not reach the stepper motor, please check connections")   
                
        else:
            
            print ('Failed to connect to the stepper motors')
        

            time.sleep(3)
            exit()
    
    
    def scanDevices(self):
        
        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        
        sbuf = create_string_buffer(64)
        
        self.lib.ximc_version(sbuf)
        
        #print("Library version: " + sbuf.raw.decode().rstrip("\0"))
        
        self.lib.set_bindy_key(os.path.join(cur_dir, "keyfile.sqlite").encode("utf-8"))
        
        # This is device search and enumeration with probing. It gives more information about devices.
        
        probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
        
        enum_hints = b"addr=192.168.0.1,172.16.2.3"
        
        # enum_hints = b"addr=" # Use this hint string for broadcast enumerate
        
        self.devenum = self.lib.enumerate_devices(probe_flags, enum_hints)        
    
        self.dev_count = lib.get_device_count(self.devenum)
    
        
    def makeConnection (self):
        
        open_name = None
        
        if len(sys.argv) > 1:
            
            open_name = sys.argv[1]
            
        elif self.dev_count == 1: 
            
            #this situation will arise if the top arm is already connected, in that case, 
            #the bottom arm is now the first in the list.
            
            open_name = self.lib.get_device_name(self.devenum, 0)
            
        elif self.dev_count == 2:
            
            open_name = self.lib.get_device_name(self.devenum, self.TopOrBottom)
            
        elif sys.version_info >= (3,0):
            
            # use URI for virtual device when there is new urllib python3 API
            tempdir = tempfile.gettempdir() + "/testdevice.bin"
            
            if os.altsep:
                
                tempdir = tempdir.replace(os.sep, os.altsep)
                
            # urlparse build wrong path if scheme is not file
            
            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                    netloc=None, path=tempdir, params=None, query=None, fragment=None))
            
            open_name = re.sub(r'^file', 'xi-emu', uri).encode()
        
        if not open_name:
            
            exit(1)
        
        if type(open_name) is str:
            
            open_name = open_name.encode()
        
        print("Open device is {}" .format(open_name))
        
        self.device_id = lib.open_device(open_name)
        
        #print("Device id: " + repr(device_id))

    def getPositions(self):
        
        x_pos = get_position_t()
        
        result = self.lib.get_position(self.device_id, byref(x_pos))
            
        return x_pos.Position, x_pos.uPosition  
    
    def moveClockWise(self, degrees):
        
        #logic for the top arm
        
        if self.TopOrBottom == 0:
        
            self.startPosition, self.uStartPosition = self.getPositions()
        
            self.getCurrentAngleRelativeToNormal()
        
            if ((self.currentAngle + degrees) <= self.MaxPosition):
        
                #1 step correspond to 0.015 degrees
        
                distance = self.startPosition + round(degrees/0.015);
        
                #print("\nGoing to {0} steps, {1} microsteps".format(distance, self.startPosition))
        
                self.lib.command_move(self.device_id, distance, self.startPosition)
                
                self.wait_for_stop(100)
        
                return 'OK' 
        
            else:
            
                return 'Prompted angle is out of safety range'
                
        #logic for the bottom arm
        
        if self.TopOrBottom == 1:
    
            self.startPosition, self.uStartPosition = self.getPositions()
    
            self.getCurrentAngleRelativeToNormal()
    
            if ((self.currentAngle - degrees) >= self.SafePosition):
    
                #1 step correspond to 0.015 degrees
    
                distance = self.startPosition + round(degrees/0.015);
    
                #print("\nGoing to {0} steps, {1} microsteps".format(distance, self.startPosition))
    
                self.lib.command_move(self.device_id, distance, self.startPosition)
                
                self.wait_for_stop(100)
    
                return 'OK'
                
            else:
            
                return 'Prompted angle is out of safety range'       
        
        
    def moveAntiClockWise(self, degrees):
        
        #logic for the top arm
        
        if self.TopOrBottom == 0:
        
            self.startPosition, self.uStartPosition = self.getPositions()
        
            self.getCurrentAngleRelativeToNormal()
        
            if ((self.currentAngle - degrees) >= self.SafePosition):
        
                #1 step correspond to 0.015 degrees
        
                distance = self.startPosition - round(degrees/0.015);
        
                #print("\nGoing to {0} steps, {1} microsteps".format(distance, self.startPosition))
        
                self.lib.command_move(self.device_id, distance, self.startPosition)
                
                self.wait_for_stop(100)
        
                return 'OK' 
        
            else:
            
                return 'Prompted angle is out of safety range'
                
         #logic for the bottom arm
                
        if self.TopOrBottom == 1:

            self.startPosition, self.uStartPosition = self.getPositions()

            self.getCurrentAngleRelativeToNormal()

            if ((self.currentAngle + degrees) <= self.MaxPosition):

                #1 step correspond to 0.015 degrees

                distance = self.startPosition - round(degrees/0.015);

                #print("\nGoing to {0} steps, {1} microsteps".format(distance, self.startPosition))

                self.lib.command_move(self.device_id, distance, self.startPosition)
                
                self.wait_for_stop(100)
                
                return 'OK'
                
            else:
            
                return 'Prompted angle is out of safety range'            

                
    def moveToSafePosition(self):
        
        if self.TopOrBottom == 0:
             
            safetyStep = self.NormalIncidenceStep + round(self.SafePosition/0.015)
            
            self.lib.command_move(self.device_id, safetyStep, 0)
            
            self.wait_for_stop(100)
            
            return ('Safe position:{} degrees, reached on the Top Arm' .format(self.SafePosition))
            
        if self.TopOrBottom == 1:
        
            safetyStep = self.NormalIncidenceStep - round(self.SafePosition/0.015)
        
            self.lib.command_move(self.device_id, safetyStep, 0)
            
            self.wait_for_stop(100)
        
            return ('Safe position:{} degrees, reached on the Bottom Arm' .format(self.SafePosition))
            
    def moveToZero(self):

        self.lib.command_move(self.device_id, self.NormalIncidenceStep, 0)
        
        self.wait_for_stop(100)

        return ('Reached 0 degree position')


    def getCurrentAngleRelativeToNormal(self):
    
        
        if self.TopOrBottom == 0:
            
            self.startPosition, self.uStartPosition = self.getPositions()
        
            self.currentAngle = (abs(self.startPosition-self.NormalIncidenceStep))*0.015 
        
        if self.TopOrBottom == 1:
            
            self.startPosition, self.uStartPosition = self.getPositions()
        
            self.currentAngle = (abs(self.NormalIncidenceStep-self.startPosition))*0.015          
    
    
    def moveTo(self, targetDegrees):
        
        self.getCurrentAngleRelativeToNormal()
        
        toMove = targetDegrees - self.currentAngle
        
        if toMove >= 0:
        
            if self.TopOrBottom == 0:
        
                #Top will move Clockwise
        
                return self.moveClockWise(abs(toMove))
        
            else:
        
                #Bottom will move AntiClockwise
        
                return self.moveAntiClockWise(abs(toMove))
            
        if toMove <= 0:
            
            if self.TopOrBottom == 1:
            
                #Bottom will move Clockwise
            
                return self.moveClockWise(abs(toMove))
            
            else:
            
                #Top will move AntiClockwise
            
                return self.moveAntiClockWise(abs(toMove))
            
    def terminateConnection(self):
    
        self.lib.close_device(byref(cast(self.device_id, POINTER(c_int))))
        
    def wait_for_stop(self, interval):
            
        self.lib.command_wait_for_stop(self.device_id, interval)
 
        
        
if __name__ == "__main__":
    
    ##test connection to top arm
    localDriverTop = RsDriver(0)
    

    ##testLimitsTopArm
    #localDriverTop.moveClockWise(100)
    #localDriverTop.moveClockWise(45)
    #localDriverTop.moveAntiClockWise(100)
    #localDriverTop.moveAntiClockWise(35)
    #localDriverTop.moveTo(120)
    localDriverTop.moveTo(35)
    localDriverTop.moveTo(5)
    localDriverTop.moveToSafePosition() 
    localDriverTop.terminateConnection()  
    #localDriverTop.moveToZero()
    
    #test connection to bottom arm
    localDriverBottom = RsDriver(1)
    
    ##testLimitsBottomArm
    #localDriverBottom.moveAntiClockWise(100)
    #localDriverBottom.moveAntiClockWise(45)    
    #localDriverBottom.moveClockWise(100)
    #localDriverBottom.moveClockWise(75)
    #localDriverBottom.moveToSafePosition()
    localDriverBottom.moveTo(35)
    localDriverBottom.moveToSafePosition()
    localDriverBottom.terminateConnection()    

    
    
    