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

class measPopUp(QtWidgets.QWidget):
    
    def __init__(self):
        
        super().__init__()
        self.setupUi()
        
    def setupUi(self):
        
        self.setObjectName("Map Acquisition")
        self.setWindowTitle("Map Acquisition")
        self.setMinimumSize(QtCore.QSize(1000, 950))
        self.setMaximumSize(QtCore.QSize(1000, 950))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("border-color: rgb(206, 206, 206);") 
        font.setFamily("Verdana")    
        
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setGeometry(QtCore.QRect(0,0,1000, 950))
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
        
        self.lastSpectrumLabel = QtWidgets.QLabel(self.centralWidget)
        fontl = font
        fontl.setBold(True)
        self.lastSpectrumLabel.setFont(fontl)
        self.lastSpectrumLabel.setText('Last Recorded Spectrum:')
        self.lastSpectrumLabel.setGeometry(QtCore.QRect(130, 385, 250, 200)) 
        
        self.previewParamLabel = QtWidgets.QLabel(self.centralWidget)
        fontl = font
        fontl.setBold(True)
        self.previewParamLabel.setFont(fontl)
        self.previewParamLabel.setText('Preview Parameters:')
        self.previewParamLabel.setGeometry(QtCore.QRect(670, 420, 250, 200))        
        
        self.previewAngleLabel = QtWidgets.QLabel(self.centralWidget)
        fontl = font
        fontl.setBold(True)
        self.previewAngleLabel.setFont(fontl)
        self.previewAngleLabel.setText('Angles (°)')
        self.previewAngleLabel.setGeometry(QtCore.QRect(700, 360, 250, 200))  
        
        self.previewEnergyLabel = QtWidgets.QLabel(self.centralWidget)
        fontl = font
        fontl.setBold(True)
        self.previewEnergyLabel.setFont(fontl)
        self.previewEnergyLabel.setText('E\n\n(eV)')
        self.previewEnergyLabel.setGeometry(QtCore.QRect(490, 150, 250, 200))  

        
        #Parameters Prompt   
        
        self.minReflectionPreviewLabel = QtWidgets.QLabel(self.centralWidget)
        self.minReflectionPreviewLabel.setGeometry(QtCore.QRect(520, 500, 200, 200))
        self.minReflectionPreviewLabel.setText('Min Reflection:')
        
        self.minReflectionPreviewTextEdit = QtWidgets.QTextEdit(self.centralWidget)
        self.minReflectionPreviewTextEdit.setGeometry(QtCore.QRect(665, 585, 60, 30))            
        
        self.maxReflectionPreviewLabel = QtWidgets.QLabel(self.centralWidget)
        self.maxReflectionPreviewLabel.setGeometry(QtCore.QRect(750, 500, 200, 200))
        self.maxReflectionPreviewLabel.setText('Max Reflection:')
        
        self.maxReflectionPreviewTextEdit = QtWidgets.QTextEdit(self.centralWidget)
        self.maxReflectionPreviewTextEdit.setGeometry(QtCore.QRect(895, 585, 60, 30))          
        
        
        #Log
        
        self.frameLog = QtWidgets.QFrame(self.centralWidget)
        self.frameLog.setGeometry(QtCore.QRect(50, 270, 400, 160))
        self.frameLog.setAutoFillBackground(True)
        self.frameLog.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 255, 255);")
        self.frameLog.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameLog.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frameLog.setLineWidth(4)
        self.frameLog.setObjectName("frameLog")
        
        
        self.Log = QtWidgets.QTextEdit(self.frameLog)
        self.Log.setGeometry(QtCore.QRect(7, 7, 393, 153))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.Log.setFont(font)
        self.Log.setFrameStyle(0)
        self.Log.setObjectName("Log")
        self.Log.setReadOnly(True)
        
        #progress displayer
        
        self.imgMaker = imd.QImageMaker()
        
        #measSlot
        
        self.measWidget = QtWidgets.QWidget(self.centralWidget) 
        self.measWidget.setGeometry(QtCore.QRect(550, 30, 400, 400))
                
        self.measSlot = imd.QImageDisplayer(self.measWidget,400,400)
        self.measSlot.updateImage(self.imgMaker.greyDefault())        
        
        #lastSpectrum
        
        self.lastSpectrumFrame = QtWidgets.QFrame(self.centralWidget)
        self.lastSpectrumFrame.setStyleSheet("border:1px solid rgb(200, 200, 200); ")
        self.lastSpectrumFrame.setGeometry(QtCore.QRect(50 , 520, 400, 400))
        
        self.lastSpectrumlayout = QtWidgets.QVBoxLayout(self.lastSpectrumFrame)

        self.static_canvas = FigureCanvas(Figure(figsize=(1, 1)))
        self.lastSpectrumlayout.addWidget(self.static_canvas)  
        
        #updatePreview

        self.previewButton = QtWidgets.QPushButton(self.centralWidget)
        self.previewButton.setGeometry(QtCore.QRect(550, 750, 400, 50))
        self.previewButton.setObjectName("previewButton")
        self.previewButton.setText("Update Preview")
        self.previewButton.setPalette(self.formPalette())
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.previewButton.setFont(font)
        self.previewButton.setStyleSheet("background-color: rgb(255, 255, 255);")   
        
        #preview Labels
        
        self.previewminAngleLabel = QtWidgets.QLabel(self.centralWidget)
        self.previewminAngleLabel.setGeometry(QtCore.QRect(550, 355, 200, 200))
        self.previewminAngleLabel.setText('Am')
        
        self.previewmaxAngleLabel = QtWidgets.QLabel(self.centralWidget)
        self.previewmaxAngleLabel.setGeometry(QtCore.QRect(935, 355, 200, 200))
        self.previewmaxAngleLabel.setText('AM')
        
        self.previewminEnergyLabel = QtWidgets.QLabel(self.centralWidget)
        self.previewminEnergyLabel.setGeometry(QtCore.QRect(497, 318, 200, 200))
        self.previewminEnergyLabel.setText('Em')
        
        self.previewmaxEnergyLabel = QtWidgets.QLabel(self.centralWidget)
        self.previewmaxEnergyLabel.setGeometry(QtCore.QRect(497, -60, 200, 200))
        self.previewmaxEnergyLabel.setText('EM')        
        
        
        
        #interruptAcquisition  
 
        self.interruptButton = QtWidgets.QPushButton(self.centralWidget)
        self.interruptButton.setGeometry(QtCore.QRect(550, 825, 400, 50))
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
    PopUp = measPopUp()
    PopUp.show()

    sys.exit(app.exec_())     


