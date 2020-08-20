# -*- coding: utf-8 -*-

import resources
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class ReflectionPopUp(QtWidgets.QWidget):
    
    def __init__(self, safePosition, maxPosition):
        
        """Initialise"""
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon(":/RsIcon.png"));
        self.setWindowTitle("ReflectionPopUp")
        
        self.setFixedSize(350, 250)
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("border-color: rgb(206, 206, 206);")
        
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 10, 330, 185))
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        self.parametersText = QtWidgets.QLabel(self.frame)
        self.parametersText.setGeometry(QtCore.QRect(185, -30, 150, 100))
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        
        self.parametersText.setFont(font)
        self.parametersText.setObjectName("parametersText")        
        
        self.startPrompt = QtWidgets.QTextEdit(self.frame)
        self.startPrompt.setObjectName("startPrompt")
        self.startPrompt.setGeometry(QtCore.QRect(210, 50, 80, 30))
        self.startPrompt.setText(str(safePosition))
        
        self.endPrompt = QtWidgets.QTextEdit(self.frame)
        self.endPrompt.setObjectName("endPrompt")
        self.endPrompt.setGeometry(QtCore.QRect(210, 95, 80, 30))
        self.endPrompt.setText(str(maxPosition))
        
        self.stepPrompt = QtWidgets.QTextEdit(self.frame)
        self.stepPrompt.setObjectName("stepPrompt")
        self.stepPrompt.setGeometry(QtCore.QRect(210, 140, 80, 30))
        self.stepPrompt.setText(str(1))        
        
        self.startAngleText = QtWidgets.QLabel(self.frame)
        self.startAngleText.setFont(font)
        self.startAngleText.setObjectName("startAngleText")
        self.startAngleText.setGeometry(QtCore.QRect(20, 50, 140, 40))
        
        self.lastAngleText = QtWidgets.QLabel(self.frame)
        self.lastAngleText.setFont(font)
        self.lastAngleText.setObjectName("lastAngleText")
        self.lastAngleText.setGeometry(QtCore.QRect(20, 95, 140, 40))
        
        self.stepText = QtWidgets.QLabel(self.frame)
        self.stepText.setFont(font)
        self.stepText.setObjectName("stepText")
        self.stepText.setGeometry(QtCore.QRect(20, 140, 140, 40))        
            
        self.startAngleText.raise_()
        self.label.raise_()
        self.parametersText.raise_()
        self.startPrompt.raise_()
        self.endPrompt.raise_()
        self.stepText.raise_()
        
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(70, 200, 220, 40))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Start")
        self.frame.raise_()
        self.pushButton.raise_()    
        
        self.startAngleText.setText("Start Angle (°)")
        self.parametersText.setText("Parameters:")
        self.lastAngleText.setText("Last Angle (°)")
        self.stepText.setText("Step (°)")



if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    PopUp = ReflectionPopUp(10,10)
    PopUp.show()
    sys.exit(app.exec_())

