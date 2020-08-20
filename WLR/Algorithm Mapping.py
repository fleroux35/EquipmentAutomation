# Author: Florian Le Roux
# -*- coding: utf-8 -*
#

#Careful, the stage direction is opposite to the final output map
#The actual map records from the top left line by line horizontally
#when it changes line the direction is changed to ensure the stage is making
#small movements. The movements here are absolute to try and rely on the sensors.

import math as m
import numpy as np
import time

class mapper():    
        
        def __init__(self, Xcentre, Ycentre, Xlength, Ylength, Xstep, Ystep):     
        
                self.Xcentre = Xcentre
                self.Ycentre = Ycentre
                self.Xlength = Xlength
                self.Ylength = Ylength
                
                #steps are received in nm, conversion is done here
                self.Xstep = Xstep * m.pow(10,-3)
                self.Ystep = Ystep * m.pow(10,-3)
                
                self.numberOfXCells = m.ceil(Xlength/self.Xstep) + 1
                
                self.numberOfYCells = m.ceil(Ylength/self.Ystep) + 1               

                self.mapIsDone = False
                
                self.map()
                
                
        def map(self):
                
                self.XPositions, self.YPositions = self.formPositions()
                
                self.currentDirection = 1
                
                self.currentX = 0
                
                self.currentY = 0
                
                while not self.mapIsDone:
                        
                        self.currentX, self.currentY, self.currentDirection = self.nextStep() 
                        
                print('the map is done.')
                        
        def formPositions(self):
                
                Xorigin = self.Xcentre + round(self.Xlength/2,2)
                
                Yorigin = self.Ycentre + round(self.Ylength/2,2)
                
                # the Positions in this matrix are the ones that will be sent to the stage
                
                XPositions = np.linspace(Xorigin, Xorigin - self.Xlength, self.numberOfXCells)                      
                
                YPositions = np.linspace(Xorigin, Yorigin - self.Ylength, self.numberOfYCells)  
                
                return XPositions, YPositions                   
                                
        def nextStep(self):
                
                ## in first position
                
                if self.currentX == 0 and self.currentY == 0:
                        
                                self.recordSpectrum()
                             
                # at a position that is not the last Y line, at a position which is not the last X position
                
                if self.currentDirection == 1:
                
                        if self.currentY <= self.numberOfYCells-1 and not self.currentX == self.numberOfXCells-1:
                                
                                print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX+1],self.YPositions[self.currentY]))
                                
                                #fill up matrix with spectra
                                
                                self.currentX = self.currentX + 1
                                
                                self.recordSpectrum()
                                
                                                        
                                return self.currentX, self.currentY, self.currentDirection
                        
                        #At a position which is the last available Y position
                        
                        else:
                                
                                #check for the last line / termination
                                                       
                                if self.currentY +1 < self.numberOfYCells-1:
                                        
                                        print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY+1]))
                                        
                                        self.currentY = self.currentY + 1
                                        
                                        self.recordSpectrum()
                                        
                                        self.currentX = 0
                                        
                                        #change of direction for the next line
                                        
                                        self.currentDirection = 1 - self.currentDirection
                                        
                                        return self.currentX, self.currentY, self.currentDirection                                
                                        
                                else:                        
                        
                                        #at the very last position
                                        
                                        self.mapIsDone = True
                                        
                                        return 0 , 0, 0
                                
                if self.currentDirection == 0: 
                        
                        if self.currentY <= self.numberOfYCells-1 and not self.currentX == 0:
                                
                                print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX+1],self.YPositions[self.currentY]))
                                
                                #fill up matrix with spectra
                                
                                self.currentX = self.currentX - 1
                                
                                print('recording spectrum at X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                                        
                                return self.currentX, self.currentY, self.currentDirection
                        
                        #At a position which is the last available Y position
                        
                        else:
                                
                                #check for the last line / termination
                                                       
                                if self.currentY +1 < self.numberOfYCells-1:
                                        
                                        print('moving to X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY+1]))
                                        
                                        self.currentY = self.currentY + 1
                                        
                                        print('recording spectrum at X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                                        
                                        self.currentZ = 0
                                        
                                        self.currentDirection = 1 - self.currentDirection
                                        
                                        return self.currentX, self.currentY, self.currentDirection                                
                                        
                                else:                        
                        
                                        #at the very last position
                                        
                                        self.mapIsDone = True
                                        
                                        return 0 , 0, 0    
                                
                                
        def recordSpectrum(self):
                
                print('recording spectrum at X:{}, Y:{}'.format(self.XPositions[self.currentX],self.YPositions[self.currentY]))
                print('updating position at the same time')
                time.sleep(0.1)

                        
                                
if __name__ == "__main__":
                        
        local_algo = Mapper(100, 100, 2.1, 2.2, 100, 100)    
                        
                        
                        
                                 
                
                
                
                
                