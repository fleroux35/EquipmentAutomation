# -*- coding: utf-8 -*-

# Author: Florian Le Roux

import resources
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class mainGUI(QtCore.QObject):
    
    def __init__(self, OneGUI):
        
        """Initialise mainwindow."""
        super().__init__()
        self.setupUi(OneGUI)
        
    def setupUi(self, MainWindow):
        
        MainWindow.setWindowIcon(QtGui.QIcon(":/OneIcon.png"));
        MainWindow.setObjectName("OneGUI")
        MainWindow.resize(1900, 1100)
        MainWindow.setMinimumSize(QtCore.QSize(1600, 1020))
        MainWindow.setMaximumSize(QtCore.QSize(1600, 1020))
        font = QtGui.QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("border-color: rgb(206, 206, 206);")    
        
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName('statusBar')
        MainWindow.setStatusBar(self.statusBar)  
        
        self.statusButton = QtWidgets.QLabel(self.centralWidget)
        self.statusButton.setMaximumSize(QtCore.QSize(60, 60))
        self.statusButton.setGeometry(QtCore.QRect(475, 0, 60,60))
        self.statusButton.setText("")
        self.statusButton.setPixmap(QtGui.QPixmap(":/RedButton.png"))
        self.statusButton.setScaledContents(True)
        self.statusButton.setObjectName("statusButton")  
        
        self.logFrame = QtWidgets.QFrame(self.centralWidget)
        self.logFrame.setGeometry(QtCore.QRect(1100, 10, 480, 990))      
        
        self.logFrame.setAutoFillBackground(True)
        self.logFrame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.logFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.logFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.logFrame.setLineWidth(4)
        self.logFrame.setObjectName("LogFrame")
        
        self.Log = QtWidgets.QTextEdit(self.logFrame)
        self.Log.setGeometry(QtCore.QRect(7, 7, 473, 983))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.Log.setFont(font)
        self.Log.setFrameStyle(0)
        self.Log.setReadOnly(True)
        self.Log.setObjectName("Log")
        
        #Positioning Stage Widget
        
        
        self.positionFrame = QtWidgets.QFrame(self.centralWidget)
        self.positionFrame.setGeometry(QtCore.QRect(20, 70, 540, 400))
        self.positionFrame.setAutoFillBackground(True)
        self.positionFrame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.positionFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.positionFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.positionFrame.setLineWidth(2)
        self.positionFrame.setObjectName("positionFrame")          
        
        self.gridLayoutWidget = QtWidgets.QWidget(self.positionFrame)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 0, 520, 380))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setGeometry(QtCore.QRect(0, 0, 520, 380))
        self.gridLayout.setSpacing(20)      
                      
        self.XPosLabel = QtWidgets.QLabel(self.centralWidget)
        self.YPosLabel = QtWidgets.QLabel(self.centralWidget)
        self.ZPosLabel = QtWidgets.QLabel(self.centralWidget)   
        
        font.setFamily("Verdana")
        font.setBold(True)
        font.setWeight(75)        
        font.setPointSize(13)
        
        self.XPosLabel.setFont(font)
        self.XPosLabel.setObjectName("XPosLabel")
        self.gridLayout.addWidget(self.XPosLabel, 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.YPosLabel.setFont(font)
        self.YPosLabel.setObjectName("YPosLabel")
        self.gridLayout.addWidget(self.YPosLabel, 0, 2, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.ZPosLabel.setFont(font)
        self.ZPosLabel.setObjectName("ZPosLabel")
        self.gridLayout.addWidget(self.ZPosLabel, 0, 3, 1, 1, QtCore.Qt.AlignHCenter)            
        
        self.xPosLCD = QtWidgets.QLCDNumber(self.centralWidget)
        self.xPosLCD.setStyleSheet("\n"
                                   "background-color: rgb(226, 239, 255);")
        self.xPosLCD.setObjectName("xPosLCD")
        self.gridLayout.addWidget(self.xPosLCD, 1, 1, 1, 1)
        self.xPosLCD.setDigitCount(7)
        
        self.yPosLCD = QtWidgets.QLCDNumber(self.centralWidget)
        self.yPosLCD.setStyleSheet("\n"
                                   "background-color: rgb(226, 239, 255);")
        self.yPosLCD.setObjectName("yPosLCD")
        self.gridLayout.addWidget(self.yPosLCD, 1, 2, 1, 1)
        self.yPosLCD.setDigitCount(7)
        
        self.zPosLCD = QtWidgets.QLCDNumber(self.centralWidget)
        self.zPosLCD.setStyleSheet("\n"
                                   "background-color: rgb(226, 239, 255);")
        self.zPosLCD.setObjectName("zPosLCD")
        self.gridLayout.addWidget(self.zPosLCD, 1, 3, 1, 1)
        self.zPosLCD.setDigitCount(7)
        
        self.stepX = QtWidgets.QLabel(self.centralWidget)
        self.stepY = QtWidgets.QLabel(self.centralWidget)
        self.stepZ = QtWidgets.QLabel(self.centralWidget)
        
        self.stepX.setFont(font)
        self.stepX.setObjectName("stepX")
        self.gridLayout.addWidget(self.stepX, 2, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.stepY.setFont(font)
        self.stepY.setObjectName("stepY")
        self.gridLayout.addWidget(self.stepY, 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.stepZ.setFont(font)
        self.stepZ.setObjectName("stepZ")
        self.gridLayout.addWidget(self.stepZ, 2, 3, 1, 1, QtCore.Qt.AlignHCenter)           
 
        self.XStepPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.XStepPrompt.setObjectName("XStepPrompt")
        self.XStepPrompt.setFont(font)
        self.gridLayout.addWidget(self.XStepPrompt, 3, 1, 1, 1)
        
        self.YStepPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.YStepPrompt.setFont(font)
        self.YStepPrompt.setObjectName("YStepPrompt")
        self.gridLayout.addWidget(self.YStepPrompt, 3, 2, 1, 1)
        
        self.ZStepPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.ZStepPrompt.setFont(font)
        self.ZStepPrompt.setObjectName("ZStepPrompt")
        self.gridLayout.addWidget(self.ZStepPrompt, 3, 3, 1, 1) 
        
        
        #Go To Widget           
        
        self.goToX = QtWidgets.QLabel(self.centralWidget)
        self.goToY = QtWidgets.QLabel(self.centralWidget)
        self.goToZ = QtWidgets.QLabel(self.centralWidget)
        
        self.goToX.setFont(font)
        self.goToX.setObjectName("goToX")
        self.gridLayout.addWidget(self.goToX, 4, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.goToY.setFont(font)
        self.goToY.setObjectName("goToY")
        self.gridLayout.addWidget(self.goToY, 4, 2, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.goToZ.setFont(font)
        self.goToZ.setObjectName("goToZ")
        self.gridLayout.addWidget(self.goToZ, 4, 3, 1, 1, QtCore.Qt.AlignHCenter)           
 
        self.goToXPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.goToXPrompt.setFont(font)
        self.goToXPrompt.resize(QtCore.QSize(10,10))
        self.goToXPrompt.setObjectName("goToXPrompt")
        self.gridLayout.addWidget(self.goToXPrompt, 5, 1, 1, 1)
        
        self.goToYPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.goToYPrompt.setFont(font)
        self.goToYPrompt.setObjectName("goToYPrompt")
        self.gridLayout.addWidget(self.goToYPrompt, 5, 2, 1, 1)
        
        self.goToZPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.goToZPrompt.setFont(font)
        self.goToZPrompt.setObjectName("goToZPrompt")
        self.gridLayout.addWidget(self.goToZPrompt, 5, 3, 1, 1)     
        
        
        #gridLayout dimensions
        
        self.gridLayout.setRowStretch(0, 8);
        self.gridLayout.setRowStretch(1, 16);
        self.gridLayout.setRowStretch(2, 8);  
        self.gridLayout.setRowStretch(3, 8);
        self.gridLayout.setRowStretch(4, 4);
        self.gridLayout.setRowStretch(5, 8); 
        
        # In the central Widget
        
        self.cnectNpStageButton = QtWidgets.QPushButton(self.centralWidget)
        self.cnectNpStageButton.setGeometry(QtCore.QRect(20, 0, 410, 60))                      
        
        self.updatePos = QtWidgets.QLabel(self.centralWidget) 
        self.goToZeroLabel = QtWidgets.QLabel(self.centralWidget)
        self.goToCentreLabel = QtWidgets.QLabel(self.centralWidget)
        self.goToLabel = QtWidgets.QLabel(self.centralWidget)
        
        self.updatePosPushButton = QtWidgets.QPushButton(self.centralWidget)
        self.goToCentrePushButton = QtWidgets.QPushButton(self.centralWidget)
        self.goToZeroPushButton = QtWidgets.QPushButton(self.centralWidget)     
        self.goToPushButton = QtWidgets.QPushButton(self.centralWidget) 
        
        font.setPointSize(11)
        
        self.updatePos.setFont(font)
        self.updatePos.setObjectName("updatePos") 
        self.updatePos.setGeometry(QtCore.QRect(40,200,500,600))
        
        self.updatePosPushButton.setGeometry(QtCore.QRect(85,530,30,30))
        
        self.goToLabel.setFont(font)
        self.goToLabel.setObjectName("goToLabel") 
        self.goToLabel.setGeometry(QtCore.QRect(220,200,500,600)) 
        
        self.goToPushButton.setGeometry(QtCore.QRect(230,530,30,30))
        
        self.goToZeroLabel.setFont(font)
        self.goToZeroLabel.setObjectName("goToZero")  
        self.goToZeroLabel.setGeometry(QtCore.QRect(310,200,500,600))
        
        self.goToZeroPushButton.setGeometry(QtCore.QRect(340,530,30,30))
        
        self.goToCentreLabel.setFont(font)
        self.goToCentreLabel.setObjectName("goToCenter")  
        self.goToCentreLabel.setGeometry(QtCore.QRect(450,200,500,600))  
        
        self.goToCentrePushButton.setGeometry(QtCore.QRect(480,530,30,30))           
        
        self.palette = self.formPalette()
        self.cnectNpStageButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.cnectNpStageButton.setFont(font)
        self.cnectNpStageButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.cnectNpStageButton.setObjectName("cnectButton")

        MainWindow.setWindowTitle("OneO")
        
        self.XPosLabel.setText("X")
        self.YPosLabel.setText("Y")
        self.ZPosLabel.setText("Z")
        
        self.stepX.setText("X Step")
        self.stepY.setText("Y Step")
        self.stepZ.setText("Z Step")
        
        self.goToX.setText("Go To X")
        self.goToY.setText("Go To Y")
        self.goToZ.setText("Go To Z")        
        
        self.updatePos.setText("Update Position")
        self.goToZeroLabel.setText("Go To Zero")
        self.goToCentreLabel.setText("Go To Centre")
        self.goToLabel.setText("Go To")
        
        self.goToXPrompt.setText('1')
        self.goToYPrompt.setText('1')
        self.goToZPrompt.setText('1')
        
        self.XStepPrompt.setText('1')
        self.YStepPrompt.setText('1')
        self.ZStepPrompt.setText('1')
        
        self.cnectNpStageButton.setText("Connect To Piezo Stage")
        
        self.positionFrame.raise_()
        
    # Extreme Laser
       
        self.cnectLaserStatusButton = QtWidgets.QLabel(self.centralWidget)
        self.cnectLaserStatusButton.setGeometry(QtCore.QRect(20, 605, 55, 55))
        self.cnectLaserStatusButton.setText("")
        self.cnectLaserStatusButton.setPixmap(QtGui.QPixmap(":/RedButton.png"))
        self.cnectLaserStatusButton.setScaledContents(True)
        self.cnectLaserStatusButton.setObjectName("cnectStatusButton") 
        
        self.LaserPowerButton = QtWidgets.QPushButton(self.centralWidget)
        self.LaserPowerButton.setGeometry(QtCore.QRect(500, 615, 40, 40))
        self.LaserPowerButton.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 255, 255);")
        self.LaserPowerButton.setObjectName("powerButton")         

        
        self.label = QtWidgets.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        
        self.LaserFrame = QtWidgets.QFrame(self.centralWidget)
        self.LaserFrame.setGeometry(QtCore.QRect(20, 690, 540, 300))
        self.LaserFrame.setAutoFillBackground(True)
        self.LaserFrame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.LaserFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.LaserFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LaserFrame.setLineWidth(2)
        self.LaserFrame.setObjectName("LaserFrame")         
        
    
        self.readingsText = QtWidgets.QLabel(self.LaserFrame)
        self.readingsText.setGeometry(QtCore.QRect(220, -20, 150, 100))        
        self.readingsText.setFont(font)
        self.readingsText.setObjectName("parametersText") 
        
        self.promptText = QtWidgets.QLabel(self.LaserFrame)
        self.promptText.setGeometry(QtCore.QRect(380, -20, 150, 100))        
        self.promptText.setFont(font)
        self.promptText.setObjectName("promptText")     
        
        self.lcdWavelength = QtWidgets.QLCDNumber(self.LaserFrame)
        self.lcdWavelength.setStyleSheet("background-color: rgb(226, 239, 255);")        
        self.lcdWavelength.setObjectName('lcdWavelength')
        self.lcdWavelength.setGeometry(QtCore.QRect(225, 75, 100, 40))
        
        self.lcdPower = QtWidgets.QLCDNumber(self.LaserFrame)
        self.lcdPower.setStyleSheet("background-color: rgb(226, 239, 255);")        
        self.lcdPower.setObjectName('lcdPower')
        self.lcdPower.setGeometry(QtCore.QRect(225, 120, 100, 40))
        
        self.lcdFrequency = QtWidgets.QLCDNumber(self.LaserFrame)
        self.lcdFrequency.setStyleSheet("background-color: rgb(226, 239, 255);")        
        self.lcdFrequency.setObjectName('lcdFrequency')
        self.lcdFrequency.setGeometry(QtCore.QRect(225, 165, 100, 40))        
               
        self.wavelengthPrompt = QtWidgets.QTextEdit(self.LaserFrame)
        self.wavelengthPrompt.setObjectName("wavelengthPrompt")
        self.wavelengthPrompt.setGeometry(QtCore.QRect(380, 75, 110, 35))
        self.wavelengthPrompt.setFont(font)
        self.wavelengthPrompt.setText('400')        
        
        self.powerPrompt = QtWidgets.QTextEdit(self.LaserFrame)
        self.powerPrompt.setObjectName("powerPrompt")
        self.powerPrompt.setGeometry(QtCore.QRect(380, 120, 110, 35))
        self.powerPrompt.setFont(font)
        self.powerPrompt.setText('6')
    
        self.frequencyPrompt = QtWidgets.QTextEdit(self.LaserFrame)
        self.frequencyPrompt.setObjectName("frequencyPrompt")
        self.frequencyPrompt.setGeometry(QtCore.QRect(380, 165, 110, 35))
        self.frequencyPrompt.setFont(font)
        self.frequencyPrompt.setText('1')        
             
        self.wavelengthText = QtWidgets.QLabel(self.LaserFrame)
        self.wavelengthText.setFont(font)
        self.wavelengthText.setObjectName("wavelengthText")
        self.wavelengthText.setGeometry(QtCore.QRect(20, 80, 170, 40))
        
        self.powerText = QtWidgets.QLabel(self.LaserFrame)
        self.powerText.setFont(font)
        self.powerText.setObjectName("powerText")
        self.powerText.setGeometry(QtCore.QRect(20, 125, 140, 40))
        
        self.frequencyText = QtWidgets.QLabel(self.LaserFrame)
        self.frequencyText.setFont(font)
        self.frequencyText.setObjectName("frequencyText")
        self.frequencyText.setGeometry(QtCore.QRect(20, 170, 170, 40)) 
        
        self.cnectLaserButton = QtWidgets.QPushButton(self.centralWidget)
        self.cnectLaserButton.setGeometry(QtCore.QRect(120, 610, 320, 60))
        self.cnectLaserButton.setObjectName("cnectButton")
        self.cnectLaserButton.setText("Connect To Laser")
        self.cnectLaserButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.cnectLaserButton.setFont(font)
        self.cnectLaserButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        self.LaserApplyButton = QtWidgets.QPushButton(self.LaserFrame)
        self.LaserApplyButton.setGeometry(QtCore.QRect(140, 230, 280, 50))
        self.LaserApplyButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.LaserApplyButton.setObjectName("applyButton")
        self.LaserApplyButton.setText("Apply Changes")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(12)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.LaserApplyButton.setFont(fontapplyButton)          
    
        self.readingsText.setText("Readouts:")
        self.promptText.setText("Prompts:")
        self.wavelengthText.setText("Wavelength (nm)")
        self.powerText.setText("Power (%)")
        self.frequencyText.setText("Frequency (MHz)")
        
    # Spectrometer
    
        self.cnectSpectroButton = QtWidgets.QPushButton(self.centralWidget)
        self.cnectSpectroButton.setGeometry(QtCore.QRect(580, 0, 400, 60))
        self.cnectSpectroButton.setObjectName("cnectSpectroButton")
        self.cnectSpectroButton.setText("Connect To Spectrometer/CCD")
        self.cnectSpectroButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.cnectSpectroButton.setFont(font)
        self.cnectSpectroButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        self.spectroButton = QtWidgets.QLabel(self.centralWidget)
        self.spectroButton.setMaximumSize(QtCore.QSize(60, 60))
        self.spectroButton.setGeometry(QtCore.QRect(1010, 0, 60,60))
        self.spectroButton.setText("")
        self.spectroButton.setPixmap(QtGui.QPixmap(":/RedButton.png"))
        self.spectroButton.setScaledContents(True)
        self.spectroButton.setObjectName("spectroButton")
        
    # Map
   
        self.mapButton = QtWidgets.QPushButton(self.centralWidget)
        self.mapButton.setGeometry(QtCore.QRect(580, 485, 500, 65))
        self.mapButton.setObjectName("Start Map Acquisition")
        self.mapButton.setText("Start Map Acquisition")
        self.mapButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.mapButton.setFont(font)
        self.mapButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        self.mapparamFrame = QtWidgets.QFrame(self.centralWidget)
        self.mapparamFrame.setGeometry(QtCore.QRect(580, 70, 500, 400))
        self.mapparamFrame.setAutoFillBackground(True)
        self.mapparamFrame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.mapparamFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.mapparamFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mapparamFrame.setLineWidth(2)
        self.mapparamFrame.setObjectName("mapparamFrame")  
        
        self.mapLabel = QtWidgets.QLabel(self.mapparamFrame)
        self.mapLabel.setGeometry(QtCore.QRect(175 , -20, 150, 100))
        self.mapLabel.setFont(font)
        self.mapLabel.setText("Map Settings:")
        
        #Step Map Widget
        
        self.gridmapLayoutWidget = QtWidgets.QWidget(self.mapparamFrame)
        self.gridmapLayoutWidget.setGeometry(QtCore.QRect(10, 60, 480, 320))
        self.gridmapLayoutWidget.setObjectName("gridmapLayoutWidget")
        self.gridmapLayout = QtWidgets.QGridLayout(self.gridmapLayoutWidget)
        self.gridmapLayout.setGeometry(QtCore.QRect(0, 0, 380, 380))
        self.gridmapLayout.setSpacing(20)    
                      
        self.XmapLengthLabel = QtWidgets.QLabel(self.centralWidget)
        self.YmapLengthLabel = QtWidgets.QLabel(self.centralWidget) 
        
        font.setFamily("Verdana")
        font.setBold(True)
        font.setWeight(75)        
        font.setPointSize(13)          
        
        self.stepmapX = QtWidgets.QLabel(self.centralWidget)
        self.stepmapY = QtWidgets.QLabel(self.centralWidget)
        
        self.stepmapX.setFont(font)
        self.stepmapX.setObjectName("stepmapX")
        self.gridmapLayout.addWidget(self.stepmapX, 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.stepmapY.setFont(font)
        self.stepmapY.setObjectName("stepmapY")
        self.gridmapLayout.addWidget(self.stepmapY, 0, 2, 1, 1, QtCore.Qt.AlignHCenter)  
 
        self.XStepPromptmap = QtWidgets.QTextEdit(self.centralWidget)
        self.XStepPromptmap.setObjectName("XStepPromptmap")
        self.XStepPromptmap.setFont(font)
        self.gridmapLayout.addWidget(self.XStepPromptmap, 1, 1, 1, 1)
        
        self.YStepPromptmap = QtWidgets.QTextEdit(self.centralWidget)
        self.YStepPromptmap.setFont(font)
        self.YStepPromptmap.setObjectName("YStepPromptmap")
        self.gridmapLayout.addWidget(self.YStepPromptmap, 1, 2, 1, 1)
        
        
        #Length Widget           
        
        self.XLengthmap = QtWidgets.QLabel(self.centralWidget)
        self.YLengthmap = QtWidgets.QLabel(self.centralWidget)
        
        self.XLengthmap.setFont(font)
        self.XLengthmap.setObjectName("XLengthmap")
        self.gridmapLayout.addWidget(self.XLengthmap, 2, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.YLengthmap.setFont(font)
        self.YLengthmap.setObjectName("YLengthmap")
        self.gridmapLayout.addWidget(self.YLengthmap, 2, 2, 1, 1, QtCore.Qt.AlignHCenter)         
 
        self.XLengthPromptmap = QtWidgets.QTextEdit(self.centralWidget)
        self.XLengthPromptmap.setFont(font)
        self.XLengthPromptmap.resize(QtCore.QSize(10,10))
        self.XLengthPromptmap.setObjectName("XLengthPromptmap")
        self.gridmapLayout.addWidget(self.XLengthPromptmap, 3, 1, 1, 1)
        
        self.YLengthPromptmap = QtWidgets.QTextEdit(self.centralWidget)
        self.YLengthPromptmap.setFont(font)
        self.YLengthPromptmap.setObjectName("YLengthPromptmap")
        self.gridmapLayout.addWidget(self.YLengthPromptmap, 3, 2, 1, 1) 
              
        #Centre Widget           
        
        self.XCentreLabelmap = QtWidgets.QLabel(self.centralWidget)
        self.YCentreLabelmap = QtWidgets.QLabel(self.centralWidget)
        
        self.XCentreLabelmap.setFont(font)
        self.XCentreLabelmap.setObjectName("XCentreLabelmap")
        self.gridmapLayout.addWidget(self.XCentreLabelmap, 4, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.YCentreLabelmap.setFont(font)
        self.YCentreLabelmap.setObjectName("YCentreLabelmap")
        self.gridmapLayout.addWidget(self.YCentreLabelmap, 4, 2, 1, 1, QtCore.Qt.AlignHCenter)         
 
        self.XCentrePromptmap = QtWidgets.QTextEdit(self.centralWidget)
        self.XCentrePromptmap.setFont(font)
        self.XCentrePromptmap.resize(QtCore.QSize(10,10))
        self.XCentrePromptmap.setObjectName("XCentrePromptmap")
        self.gridmapLayout.addWidget(self.XCentrePromptmap, 5, 1, 1, 1)
        
        self.YCentrePromptmap = QtWidgets.QTextEdit(self.centralWidget)
        self.YCentrePromptmap.setFont(font)
        self.YCentrePromptmap.setObjectName("YCentrePromptmap")
        self.gridmapLayout.addWidget(self.YCentrePromptmap, 5, 2, 1, 1)  
        
        #Estimated Labels
        
        font.setPointSize(10)
        self.estimatedTimeLabel = QtWidgets.QLabel(self.centralWidget)
        self.estimatedTimeLabel.setFont(font)
        self.estimatedTimeLabel.setGeometry(QtCore.QRect(40, 340, 200, 200))
        self.estimatedTimeLabel.setText('Estimated Acquisition Time:')
        
        #Thorlab Stage
        
        self.cnectThorButton = QtWidgets.QPushButton(self.centralWidget)
        self.cnectThorButton.setGeometry(QtCore.QRect(580, 580, 400, 60))
        self.cnectThorButton.setObjectName("cnectThorButton")
        self.cnectThorButton.setText("Connect To Thorlabs Stage")
        self.cnectThorButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.cnectThorButton.setFont(font)
        self.cnectThorButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        self.cnectThorButtonLabel = QtWidgets.QLabel(self.centralWidget)
        self.cnectThorButtonLabel.setMaximumSize(QtCore.QSize(60, 60))
        self.cnectThorButtonLabel.setGeometry(QtCore.QRect(1010, 580, 60,60))
        self.cnectThorButtonLabel.setText("")
        self.cnectThorButtonLabel.setPixmap(QtGui.QPixmap(":/RedButton.png"))
        self.cnectThorButtonLabel.setScaledContents(True)
        self.cnectThorButtonLabel.setObjectName("cnectThorButton") 
        
        #Thorlabs/Fourier Panel
        
        self.ThorlabsFStageFrame = QtWidgets.QFrame(self.centralWidget)
        self.ThorlabsFStageFrame.setGeometry(QtCore.QRect(580, 660, 500, 325))
        self.ThorlabsFStageFrame.setAutoFillBackground(True)
        self.ThorlabsFStageFrame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.ThorlabsFStageFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.ThorlabsFStageFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ThorlabsFStageFrame.setLineWidth(2)
        self.ThorlabsFStageFrame.setObjectName("ThorlabsFStageFrame")             
        
        self.ThorPosLabel = QtWidgets.QLabel(self.ThorlabsFStageFrame)
        self.ThorPosLabel.setFont(font)
        self.ThorPosLabel.setObjectName("PositionThorlabStage")
        self.ThorPosLabel.setGeometry(QtCore.QRect(30, 10, 190, 100))
        self.ThorPosLabel.setText('Position (in mm):')
        
        self.ThorPosLCD = QtWidgets.QLCDNumber(self.ThorlabsFStageFrame)
        self.ThorPosLCD.setGeometry(QtCore.QRect(270, 35, 100, 40))
        self.ThorPosLCD.setStyleSheet("\n"
                                   "background-color: rgb(226, 239, 255);")
        self.ThorPosLCD.setObjectName("ThorPosLCD")
        self.ThorPosLCD.setDigitCount(7)   
        
        self.goToThorLabel = QtWidgets.QLabel(self.ThorlabsFStageFrame)
        self.goToThorLabel.setFont(font)
        self.goToThorLabel.setObjectName("goToThorLabel")
        self.goToThorLabel.setGeometry(QtCore.QRect(30, 60, 190, 100))
        self.goToThorLabel.setText('Go to (in mm):')
        
        self.goToThorPrompt = QtWidgets.QTextEdit(self.ThorlabsFStageFrame)
        fontPrompt = font
        fontPrompt.setBold(False)
        self.goToThorPrompt.setObjectName("goToThorPrompt")
        self.goToThorPrompt.setGeometry(QtCore.QRect(270, 85, 100, 40))
               
        self.goThorButton = QtWidgets.QPushButton(self.ThorlabsFStageFrame)
        self.goThorButton.setGeometry(QtCore.QRect(390, 85, 100, 40))
        self.goThorButton.setObjectName("goThorButton")
        self.goThorButton.setText("Go")
        self.goThorButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.goThorButton.setFont(font)
        self.goThorButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        self.updtThorButton = QtWidgets.QPushButton(self.ThorlabsFStageFrame)
        self.updtThorButton.setGeometry(QtCore.QRect(390, 35, 100, 40))
        self.updtThorButton.setObjectName("goThorButton")
        self.updtThorButton.setText("Updt")
        self.updtThorButton.setPalette(self.palette)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.updtThorButton.setFont(font)
        self.updtThorButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        
        #gridLayout dimensions
        
        self.gridmapLayout.setRowStretch(0, 8);
        self.gridmapLayout.setRowStretch(1, 16);
        self.gridmapLayout.setRowStretch(2, 8);  
        self.gridmapLayout.setRowStretch(3, 8);
        self.gridmapLayout.setRowStretch(4, 4);
        self.gridmapLayout.setRowStretch(5, 8);                       
        
        self.palette = self.formPalette()
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        
        self.stepmapX.setText("X Step (nm)")
        self.stepmapY.setText("Y Step (nm)")
        
        self.XLengthmap.setText("X Length (um)")
        self.YLengthmap.setText("Y Length (um)")
        
        self.XCentreLabelmap.setText("X Centre (um)")
        self.YCentreLabelmap.setText("Y Centre (um)")
        
        self.XLengthPromptmap.setText('0.15')
        self.YLengthPromptmap.setText('0.15')
        
        self.XCentrePromptmap.setText('100')
        self.YCentrePromptmap.setText('100')
        
        self.XStepPromptmap.setText('50')
        self.YStepPromptmap.setText('50')
        
        self.positionFrame.raise_()
        
        MainWindow.setCentralWidget(self.centralWidget) 
        
        
    def formPalette(self):
            
        palette = QtGui.QPalette()     
            
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        
        return palette
                        
        
if __name__ == "__main__":
    
    import sys
    app = QtWidgets.QApplication(sys.argv)
    NpGUI = QtWidgets.QMainWindow()
    mainGUI(NpGUI)
    NpGUI.show()
    sys.exit(app.exec_())
    
# The code below has been generated from reading ui file 'UI_RsGUI.ui'

