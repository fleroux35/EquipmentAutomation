# -*- coding: utf-8 -*-
"""
Author: Florian Le Roux
"""
import serial
import time
import nplab.instrument.serial_instrument as si

class NpStageDriver(si.SerialInstrument):
    '''A simple class for the Piezo concept FOC100 nanopositioning system'''
    
    def __init__(self, port=None):
        self.termination_character = '\n'
        self.port_settings = {
                    'baudrate':115200,
                    'bytesize':serial.EIGHTBITS,
                    'parity':serial.PARITY_NONE,
                    'stopbits':serial.STOPBITS_ONE,
                    'timeout':0.2, #wait at most one second for a response
          #          'writeTimeout':1, #similarly, fail if writing takes >1s
           #         'xonxoff':False, 'rtscts':False, 'dsrdtr':False,
                    }
        si.SerialInstrument.__init__(self,port=port)
        self.recenter()
        
        self.XMAX = 200
        self.YMAX = 200
        self.ZMAX = 50
        
        self.XMIN = 0
        self.YMIN = 0
        self.ZMIN = 0
        
        
    def move_rel(self,value,unit="n"):
        '''A command for relative movement, where the default units is nm'''
        if unit == "n":
            multiplier=1
        if unit == "u":
            multiplier=1E3
            
        if (value*multiplier+self.position) > 1E5 or (value*multiplier+self.position) < 0:
            print('The value is out of range! 0-100 um (0-1E8 nm) (Z)')
        elif (value*multiplier+self.position) < 1E5 and (value*multiplier+self.position) >= 0:
            self.write("MOVRX "+str(value)+unit)
            self.position=(value*multiplier+self.position)
            
    def move_step(self,direction):
        self.move_rel(direction*self.stepsize)
        
    def recenter(self):
        ''' Moves the stage to the center position'''
        #self.move(50,unit = "u")
        #self.position = 50E3
        
    def INFO(self):
        
        return self.query("INFOS",multiline=True,termination_line= "\n \n \n \n",timeout=.1,)  
    
    def get_X(self):
        
        Xposition = self.query("GET_X",multiline=False,termination_line= "\n \n \n \n",timeout=.1,)
        Xposition = Xposition.replace('Ok\n', '')
        Xposition = Xposition.replace('um','')
        
        return (float(Xposition))

    
    def get_Y(self):
        
        Yposition = self.query("GET_Y",multiline=False,termination_line= "\n \n \n \n",timeout=.1,)
        Yposition = Yposition.replace('Ok\n', '')
        Yposition = Yposition.replace('um','')        
        
        return (float(Yposition))
    
    def get_Z(self):
        
        Zposition = self.query("GET_Z",multiline=False,termination_line= "\n \n \n \n",timeout=.1,)
        
        Zposition = Zposition.replace('Ok\n', '')
        Zposition = Zposition.replace('um','')        
        
        return (float(Zposition))
    
    def moveto_X(self, value):
        
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range default unit is nm'''
            
        if value > self.XMAX or value < self.XMIN:
            print('The value is out of range')
            
        else:
            self.write("MOVEX "+str(value)+'u')
            self.position = value

    def moverel_X(self, value):
        
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range default unit is nm'''
        
        currentX = self.get_X()      
            
        if value + currentX > self.XMAX or value + currentX < self.XMIN:
            print('The value is out of range')
            
        else:
            self.write("MOVRX "+str(value)+'u')
            self.position = value
            
    def moveto_Y(self, value):
        
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range default unit is nm'''
            
        if value > self.YMAX or value < self.YMIN:
            print('The value is out of range')
            
        else:
            self.write("MOVEY "+str(value)+'u')
            self.position = value

    def moverel_Y(self, value):
        
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range default unit is nm'''
        
        currentY = self.get_Y()      
            
        if value + currentY > self.YMAX or value + currentY < self.YMIN:
            print('The value is out of range')
            
        else:
            self.write("MOVRY "+str(value)+'u')
            self.position = value
            
    def moveto_Z(self, value):
        
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range default unit is nm'''
            
        if value > self.ZMAX or value < self.ZMIN:
            print('The value is out of range')
            
        else:
            self.write("MOVEZ "+str(value)+'u')
            self.position = value

    def moverel_Z(self, value):
        
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range default unit is nm'''
        
        currentZ = self.get_Z()      
            
        if value + currentZ > self.ZMAX or value + currentZ < self.ZMIN:
            print('The value is out of range')
            
        else:
            self.write("MOVRZ "+str(value)+'u')
            self.position = value    
                        
            
if __name__ == "__main__":
    
    '''Basic test, should open the Z stage and print its info before closing. 
    Obvisouly the comport has to be correct!'''
    
    Z = NpStageDriver(port = "COM11")
    
    print(Z.INFO())
    
    '''Will return the current position'''
    
    print('X positions')
    
    print(Z.get_X())

    Z.moveto_X(100)
    #Z.moveto_X(201)
    time.sleep(2)
    
    print(Z.get_X())
       
    Z.moverel_X(-10)
    #Z.moveto_X(1000)
    time.sleep(2)
    
    print(Z.get_X()) 
    
    print('Y positions')
    
    print(Z.get_Y()) 
    
    Z.moveto_Y(100)
    #Z.moveto_Y(201)
    time.sleep(2)
    
    print(Z.get_Y())
       
    Z.moverel_Y(-10)
    #Z.moveto_Y(1000)
    time.sleep(2)
    
    print(Z.get_Y()) 
    
    print('Z positions')
    
    print(Z.get_Z())
    
    Z.moveto_Z(25)
    #Z.moveto_Z(51)
    time.sleep(2)
    
    print(Z.get_Z())
       
    Z.moverel_Z(-10)
    #Z.moveto_Z(1000)
    time.sleep(2)
    
    print(Z.get_Z())  
    
    Z.close()
        
