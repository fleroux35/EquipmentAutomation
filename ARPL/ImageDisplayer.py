import sys
from PIL import Image, ImageQt
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, Qt, QRect
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QImage, QPixmap

class QImageDisplayer(QWidget):

    def __init__(self, parent, width, height):
        
        super(QImageDisplayer, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.label = QLabel(self)
        self.width = width
        self.height = height
        
    def updateImage(self, bitmapToDisplay):
        
        pixmapbf = QPixmap.fromImage(bitmapToDisplay)

        pixmap = pixmapbf.scaled(self.width, self.height)
        
        self.label.setPixmap(pixmap)  
        
        self.resize(pixmap.width(),pixmap.height())
        
        self.update()
            
class QImageMaker(QObject):
    
    sig_image = pyqtSignal(ImageQt.ImageQt) 
    
    def __init__(self):
        
        super().__init__()
        
    @pyqtSlot(int, int, int, int)
    
    def makeProgressImage(self, lastX, lastY, maxIndexX, maxIndexY):
    
        img = Image.new( 'RGB', (maxIndexX+1,maxIndexY+1), "grey") # Create a new grey image
        pixels = img.load() # Create the pixel map
             
        #the image is coloured according to the acquisition direction
        
        #if the last line is the first line, colour everything up to the last X from left to right
        
        if lastY == 0:
            
            for j in range(lastX+1):
                
                pixels[j,0] = (0, 255, 0) # Set the colour accordingly              
                
            if lastX == maxIndexX: #colour the next one in orange
                        
                pixels[lastX,lastY+1] = (255,165,0)
                    
            else:            
                    
                pixels[lastX+1,lastY] = (255,165,0)
                
            self.sig_image.emit(ImageQt.ImageQt(img))
            
            return

        
        #if the last line is not the first line
        
        for i in range(0, lastY):    # Colour every pixel of Y lines done in green
            
            for j in range(0, maxIndexX+1):
                
                pixels[j,i] = (0, 255, 0) # Set the colour accordingly 
        
        if lastY % 2 == 0:
            
            for j in range(0, lastX+1):
            
                pixels[j,lastY] = (0, 255, 0) # Set the colour
             
            if lastX == maxIndexX : #colour the next one in orange
                
                if lastY == maxIndexY:
                    
                    self.sig_image.emit(self.greenDefault())
                    
                    return
                    
                else:
                
                    pixels[lastX,lastY+1] = (255,165,0)
                    
                    self.sig_image.emit(ImageQt.ImageQt(img))
                    
                    return
                                        
            
            else:            
            
                pixels[lastX+1,lastY] = (255,165,0)
            
                self.sig_image.emit(ImageQt.ImageQt(img))
        
            return
                
        else:
            
            for j in range(lastX, maxIndexX+1):
            
                pixels[j,lastY] = (0, 255, 0) # Set the colour 
                
            #colour the current one in orange
                
            if lastX == 0: #colour the next one in orange
                
                if lastY == maxIndexY:
                    
                    self.sig_image.emit(self.greenDefault())
                    
                    return                
                    
                else:
                    
                    pixels[lastX,lastY+1] = (255,165,0)
                    
                    self.sig_image.emit(ImageQt.ImageQt(img))
                    
                    return
                
            else:            
                
                pixels[lastX-1,lastY] = (255,165,0)
                
                self.sig_image.emit(ImageQt.ImageQt(img))
            
            return
            
    def greyDefault(self):
        
        img = Image.new( 'RGB', (1,1), "grey") # Create a new grey image
        pixels = img.load()
        
        return ImageQt.ImageQt(img)
    
    def greenDefault(self):
        
        img = Image.new( 'RGB', (1,1), "green") # Create a new green image
        pixels = img.load()
        
        return ImageQt.ImageQt(img)
    
    def startDefault(self, maxIndexX, maxIndexY):
        
        img = Image.new( 'RGB', (maxIndexX+1,maxIndexY+1), "grey") # Create a new grey image
        pixels = img.load() # Create the pixel map
        
        pixels[0,0] = (255,165,0)
        
        return ImageQt.ImageQt(img)   
          
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    imageMaker = QImageMaker()
    mainWindow = QWidget()
    mainWindow.show()
    mainWindow.setGeometry(QRect(0,0,400,400))
    
    Qtimage = imageMaker.makeProgressImage(0,0,1,1)
    
    imgDisplayer = QImageDisplayer(mainWindow,400,400)
    imgDisplayer.updateImage(Qtimage) 
    
    Qtimage2 = imageMaker.makeProgressImage(2,2,3,3)
    
    imgDisplayer.updateImage(Qtimage2) 
    
    sys.exit(app.exec_())    