# -*- coding: utf-8 -*-

import resources
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class FreeMovePopUp(QtWidgets.QWidget):
    
    def __init__(self, angleTop, angleBottom):
        
        """Initialise"""
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon(":/RsIcon.png"));
        self.setWindowTitle("FreeMovePopUp")
        
        self.setFixedSize(350, 200)
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("border-color: rgb(206, 206, 206);")
        
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 10, 330, 125))
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
        
        self.targetAngleText = QtWidgets.QLabel(self.frame)
        self.targetAngleText.setGeometry(QtCore.QRect(170, -30, 150, 100))
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        
        self.targetAngleText.setFont(font)
        self.targetAngleText.setObjectName("targetAngleText")        
        
        self.topPrompt = QtWidgets.QTextEdit(self.frame)
        self.topPrompt.setObjectName("topPrompt")
        self.topPrompt.setGeometry(QtCore.QRect(200, 40, 80, 30))
        self.topPrompt.setText(str(angleTop))
        
        self.btPrompt = QtWidgets.QTextEdit(self.frame)
        self.btPrompt.setObjectName("btPrompt")
        self.btPrompt.setGeometry(QtCore.QRect(200, 85, 80, 30))
        self.btPrompt.setText(str(angleBottom))
        
        self.tpAxisText = QtWidgets.QLabel(self.frame)
        self.tpAxisText.setFont(font)
        self.tpAxisText.setObjectName("tpAxisText")
        self.tpAxisText.setGeometry(QtCore.QRect(20, 40, 80, 30))
        
        self.btmAxisText = QtWidgets.QLabel(self.frame)
        self.btmAxisText.setFont(font)
        self.btmAxisText.setObjectName("btmAxisText")
        self.btmAxisText.setGeometry(QtCore.QRect(20, 85, 120, 30))
            
        self.tpAxisText.raise_()
        self.label.raise_()
        self.targetAngleText.raise_()
        self.topPrompt.raise_()
        self.btPrompt.raise_()
        self.btmAxisText.raise_()
        
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(90, 148, 180, 40))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Move")
        self.frame.raise_()
        self.pushButton.raise_()    
        
        self.tpAxisText.setText("Top Axis")
        self.targetAngleText.setText("Target Angle (°)")
        self.btmAxisText.setText("Bottom Axis")
        self.pushButton.setText("Move")        
    


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    PopUp = FreeMovePopUp(10,10)
    PopUp.show()
    sys.exit(app.exec_())

