# Import the .NET class library
import clr

# Import python sys module
import sys

# Import os module
import os

# Import System.IO for saving and opening files
from System.IO import *

# Import c compatible List and String
from System import String
from System.Collections.Generic import List

KinesisPath = 'C:\Program Files\Thorlabs\Kinesis'
clr.AddReference('{}\Thorlabs.MotionControl.DeviceManagerCLI.dll'.format(KinesisPath));
clr.AddReference('{}\Thorlabs.MotionControl.KCube.DCServoCLI.dll'.format(KinesisPath));

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo

#The serial number of the stage is 27504894
device = KCubeDCServo.CreateKCubeDCServo(str(27504894));
device.connect(27504894)

        