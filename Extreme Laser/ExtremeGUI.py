# -*- coding: utf-8 -*-

import resources
import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class mainGUI(QtCore.QObject):
    
    def __init__(self, ExtremeGUI):
        
        """Initialise mainwindow."""
        super().__init__()
        self.setupUi(ExtremeGUI)
        
    def setupUi(self, MainWindow):
        
        MainWindow.setWindowIcon(QtGui.QIcon(":/ExIcon.png"));
        MainWindow.setWindowTitle("Extreme Laser")
        
        MainWindow.setFixedSize(510, 550)
        
        font = QtGui.QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("border-color: rgb(206, 206, 206);")
        
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        
        self.frame = QtWidgets.QFrame(self.centralWidget)
        self.frame.setGeometry(QtCore.QRect(10, 70, 490, 185))
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        
        self.cnectStatusButton = QtWidgets.QLabel(self.centralWidget)
        self.cnectStatusButton.setGeometry(QtCore.QRect(20, 5, 55, 55))
        self.cnectStatusButton.setText("")
        self.cnectStatusButton.setPixmap(QtGui.QPixmap(":/RedButton.png"))
        self.cnectStatusButton.setScaledContents(True)
        self.cnectStatusButton.setObjectName("cnectStatusButton") 
        
        self.powerButton = QtWidgets.QPushButton(self.centralWidget)
        self.powerButton.setGeometry(QtCore.QRect(440, 15, 40, 40))
        self.powerButton.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 255, 255);")
        self.powerButton.setObjectName("powerButton")         
        
        self.frameLog = QtWidgets.QFrame(self.centralWidget)
        self.frameLog.setGeometry(QtCore.QRect(10, 340, 490, 185))
        self.frameLog.setAutoFillBackground(True)
        self.frameLog.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 255, 255);")
        self.frameLog.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameLog.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frameLog.setLineWidth(4)
        self.frameLog.setObjectName("frameLog")
        
        
        self.Log = QtWidgets.QTextEdit(self.frameLog)
        self.Log.setGeometry(QtCore.QRect(7, 7, 640, 170))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.Log.setFont(font)
        self.Log.setFrameStyle(0)
        self.Log.setObjectName("Log") 
        
        self.label = QtWidgets.QLabel(self.frame)
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
        
  
        self.readingsText = QtWidgets.QLabel(self.frame)
        self.readingsText.setGeometry(QtCore.QRect(220, -30, 150, 100))        
        self.readingsText.setFont(font)
        self.readingsText.setObjectName("parametersText") 
        
        self.promptText = QtWidgets.QLabel(self.frame)
        self.promptText.setGeometry(QtCore.QRect(380, -30, 150, 100))        
        self.promptText.setFont(font)
        self.promptText.setObjectName("promptText")     
        
        self.lcdWavelength = QtWidgets.QLCDNumber(self.frame)
        self.lcdWavelength.setStyleSheet("background-color: rgb(226, 239, 255);")        
        self.lcdWavelength.setObjectName('lcdWavelength')
        self.lcdWavelength.setGeometry(QtCore.QRect(225, 45, 100, 40))
        
        self.lcdPower = QtWidgets.QLCDNumber(self.frame)
        self.lcdPower.setStyleSheet("background-color: rgb(226, 239, 255);")        
        self.lcdPower.setObjectName('lcdPower')
        self.lcdPower.setGeometry(QtCore.QRect(225, 90, 100, 40))
        
        self.lcdFrequency = QtWidgets.QLCDNumber(self.frame)
        self.lcdFrequency.setStyleSheet("background-color: rgb(226, 239, 255);")        
        self.lcdFrequency.setObjectName('lcdFrequency')
        self.lcdFrequency.setGeometry(QtCore.QRect(225, 135, 100, 40))        
               
        self.wavelengthPrompt = QtWidgets.QTextEdit(self.frame)
        self.wavelengthPrompt.setObjectName("wavelengthPrompt")
        self.wavelengthPrompt.setGeometry(QtCore.QRect(380, 45, 80, 35))
        
        self.powerPrompt = QtWidgets.QTextEdit(self.frame)
        self.powerPrompt.setObjectName("powerPrompt")
        self.powerPrompt.setGeometry(QtCore.QRect(380, 90, 80, 35))

        self.frequencyPrompt = QtWidgets.QTextEdit(self.frame)
        self.frequencyPrompt.setObjectName("frequencyPrompt")
        self.frequencyPrompt.setGeometry(QtCore.QRect(380, 135, 80, 35))
             
        self.wavelengthText = QtWidgets.QLabel(self.frame)
        self.wavelengthText.setFont(font)
        self.wavelengthText.setObjectName("wavelengthText")
        self.wavelengthText.setGeometry(QtCore.QRect(20, 50, 170, 40))
        
        self.powerText = QtWidgets.QLabel(self.frame)
        self.powerText.setFont(font)
        self.powerText.setObjectName("powerText")
        self.powerText.setGeometry(QtCore.QRect(20, 95, 140, 40))
        
        self.frequencyText = QtWidgets.QLabel(self.frame)
        self.frequencyText.setFont(font)
        self.frequencyText.setObjectName("frequencyText")
        self.frequencyText.setGeometry(QtCore.QRect(20, 140, 170, 40)) 
        
        self.cnectButton = QtWidgets.QPushButton(self.centralWidget)
        self.cnectButton.setGeometry(QtCore.QRect(125, 10, 280, 50))
        self.cnectButton.setObjectName("cnectButton")
        self.cnectButton.setText("Connect")
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.cnectButton.setFont(font)
        self.cnectButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        self.applyButton = QtWidgets.QPushButton(self.centralWidget)
        self.applyButton.setGeometry(QtCore.QRect(125, 270, 280, 50))
        self.applyButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.applyButton.setObjectName("applyButton")
        self.applyButton.setText("Apply Changes")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(12)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.applyButton.setFont(fontapplyButton)          

        self.readingsText.setText("Readouts:")
        self.promptText.setText("Prompts:")
        self.wavelengthText.setText("Wavelength (nm)")
        self.powerText.setText("Power (%)")
        self.frequencyText.setText("Frequency (MHz)")
        
        MainWindow.setCentralWidget(self.centralWidget)        


if __name__ == "__main__":
        
        import sys
        app = QtWidgets.QApplication(sys.argv)
        ExtremeGUI = QtWidgets.QMainWindow()
        ui = mainGUI(ExtremeGUI)
        ExtremeGUI.show()
        sys.exit(app.exec_())
            
        # The code below has been generated from reading ui file 'UI_RsGUI.ui'

