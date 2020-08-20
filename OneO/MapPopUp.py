# -*- coding: utf-8 -*-

# Author: Florian Le Roux

import resources
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import ImageDisplayer as imd

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class mapPopUp(QtWidgets.QWidget):
    
    def __init__(self):
        
        super().__init__()
        self.setupUi()
        
    def setupUi(self):
        
        self.setObjectName("Map Acquisition")
        self.setWindowTitle("Map Acquisition")
        self.setMinimumSize(QtCore.QSize(1000, 1100))
        self.setMaximumSize(QtCore.QSize(1000, 1100))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("border-color: rgb(206, 206, 206);") 
        font.setFamily("Verdana")    
        
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setGeometry(QtCore.QRect(0,0,1000, 1100))
        self.centralWidget.setObjectName("centralWidget")
        
        #labels
        
        self.progressLabel = QtWidgets.QLabel(self.centralWidget)
        self.progressLabel.setGeometry(QtCore.QRect(60, -110, 300, 300))
        self.progressLabel.setFont(font)
        self.progressLabel.setText('Progress:') 
        
        self.progressValueLabel = QtWidgets.QLabel(self.centralWidget)
        self.progressValueLabel.setGeometry(QtCore.QRect(150, -150, 400, 400))
        self.progressValueLabel.setFont(font)
        self.progressValueLabel.setText('Info Unavailable')  
        
        self.remainingTimeLabel = QtWidgets.QLabel(self.centralWidget)
        self.remainingTimeLabel.setGeometry(QtCore.QRect(60, -20, 300, 300))
        self.remainingTimeLabel.setFont(font)
        self.remainingTimeLabel.setText('Estimated Time Remaining:')
        
        self.remainingTimeValueLabel = QtWidgets.QLabel(self.centralWidget)
        self.remainingTimeValueLabel.setGeometry(QtCore.QRect(300, -20, 300, 300))
        self.remainingTimeValueLabel.setFont(font)
        self.remainingTimeValueLabel.setText('Info Unavailable')        

        self.finishTimeLabel = QtWidgets.QLabel(self.centralWidget)
        self.finishTimeLabel.setGeometry(QtCore.QRect(60, 50, 300, 300))
        self.finishTimeLabel.setFont(font)
        self.finishTimeLabel.setText('Estimated Finish Time:')
        
        self.finishTimeValueLabel = QtWidgets.QLabel(self.centralWidget)
        self.finishTimeValueLabel.setGeometry(QtCore.QRect(260, 50, 300, 300))
        self.finishTimeValueLabel.setFont(font)
        self.finishTimeValueLabel.setText('Info Unavailable')        
        
        self.wvlLabel = QtWidgets.QLabel(self.centralWidget)
        font.setBold(True)
        self.wvlLabel.setFont(font)
        self.wvlLabel.setText('Map Wavelength (nm):')
        self.wvlLabel.setGeometry(QtCore.QRect(490, 380, 220, 200)) 
        font.setBold(False)
        
        self.wvlPrompt = QtWidgets.QTextEdit(self.centralWidget)
        self.wvlPrompt.setFont(font)
        self.wvlPrompt.setGeometry(QtCore.QRect(720, 460, 60, 35)) 
        
        self.updatePreviewBtn = QtWidgets.QPushButton(self.centralWidget)
        font.setBold(True)
        self.updatePreviewBtn.setFont(font)
        font.setBold(False)
        self.updatePreviewBtn.setGeometry(QtCore.QRect(810, 450, 170, 50)) 
        self.updatePreviewBtn.setText('Update Preview')
        
        self.lastSpectrumLabel = QtWidgets.QLabel(self.centralWidget)
        fontl = font
        fontl.setBold(True)
        self.lastSpectrumLabel.setFont(fontl)
        self.lastSpectrumLabel.setText('Last Recorded Spectrum:')
        self.lastSpectrumLabel.setGeometry(QtCore.QRect(130, 385, 250, 200)) 
        
        #Log
        
        self.frameLog = QtWidgets.QFrame(self.centralWidget)
        self.frameLog.setGeometry(QtCore.QRect(50, 260, 400, 185))
        self.frameLog.setAutoFillBackground(True)
        self.frameLog.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 255, 255);")
        self.frameLog.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameLog.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frameLog.setLineWidth(4)
        self.frameLog.setObjectName("frameLog")
        
        
        self.Log = QtWidgets.QTextEdit(self.frameLog)
        self.Log.setGeometry(QtCore.QRect(7, 7, 393, 178))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.Log.setFont(font)
        self.Log.setFrameStyle(0)
        self.Log.setObjectName("Log")
        self.Log.setReadOnly(True)
        
        #progress displayer
        
        self.imgMaker = imd.QImageMaker()
        
        self.progressWidget = QtWidgets.QWidget(self.centralWidget) 
        self.progressWidget.setGeometry(QtCore.QRect(550, 20, 400, 400))
                
        self.progressSlot = imd.QImageDisplayer(self.progressWidget,400,400)
        self.progressSlot.updateImage(self.imgMaker.greyDefault())  
        
        #mapSlot
        
        self.mapWidget = QtWidgets.QWidget(self.centralWidget) 
        self.mapWidget.setGeometry(QtCore.QRect(550, 520, 400, 400))
                
        self.mapSlot = imd.QImageDisplayer(self.mapWidget,400,400)
        self.mapSlot.updateImage(self.imgMaker.greyDefault())        
        
        #lastSpectrum
        
        self.lastSpectrumFrame = QtWidgets.QFrame(self.centralWidget)
        self.lastSpectrumFrame.setStyleSheet("border:1px solid rgb(200, 200, 200); ")
        self.lastSpectrumFrame.setGeometry(QtCore.QRect(50 , 520, 400, 400))
        
        self.lastSpectrumlayout = QtWidgets.QVBoxLayout(self.lastSpectrumFrame)

        self.static_canvas = FigureCanvas(Figure(figsize=(1, 1)))
        self.lastSpectrumlayout.addWidget(self.static_canvas)  
        
        #interruptAcquisition  
 
        self.interruptButton = QtWidgets.QPushButton(self.centralWidget)
        self.interruptButton.setGeometry(QtCore.QRect(300, 950, 500, 100))
        self.interruptButton.setObjectName("interruptButton")
        self.interruptButton.setText("Interrupt Acquisition")
        self.interruptButton.setPalette(self.formPalette())
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.interruptButton.setFont(font)
        self.interruptButton.setStyleSheet("background-color: rgb(255, 255, 255);")
                


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

    app = QtWidgets.QApplication(sys.argv)
    PopUp = mapPopUp()
    PopUp.show()
    
    PopUp.progressSlot.updateImage(PopUp.imgMaker.greenDefault())

    sys.exit(app.exec_())     


