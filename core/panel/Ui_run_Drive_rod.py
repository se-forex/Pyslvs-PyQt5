# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ahshoe/桌面/Pyslvs-PyQt5/core/panel/run_Drive_rod.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(485, 213)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Rod = QtWidgets.QComboBox(Form)
        self.Rod.setObjectName("Rod")
        self.horizontalLayout_2.addWidget(self.Rod)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.Distance_text = QtWidgets.QDoubleSpinBox(Form)
        self.Distance_text.setMinimum(0.01)
        self.Distance_text.setMaximum(1000.0)
        self.Distance_text.setSingleStep(10.0)
        self.Distance_text.setProperty("value", 10.0)
        self.Distance_text.setObjectName("Distance_text")
        self.horizontalLayout.addWidget(self.Distance_text)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.ResetButton = QtWidgets.QPushButton(Form)
        self.ResetButton.setObjectName("ResetButton")
        self.horizontalLayout.addWidget(self.ResetButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.distanceLayout = QtWidgets.QHBoxLayout()
        self.distanceLayout.setSpacing(0)
        self.distanceLayout.setObjectName("distanceLayout")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.distanceLayout.addWidget(self.label_3)
        self.Center = QtWidgets.QLabel(Form)
        self.Center.setObjectName("Center")
        self.distanceLayout.addWidget(self.Center)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.distanceLayout.addWidget(self.label_5)
        self.Distance = QtWidgets.QLabel(Form)
        self.Distance.setObjectName("Distance")
        self.distanceLayout.addWidget(self.Distance)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.distanceLayout.addWidget(self.label_7)
        self.Start = QtWidgets.QLabel(Form)
        self.Start.setObjectName("Start")
        self.distanceLayout.addWidget(self.Start)
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setObjectName("label_10")
        self.distanceLayout.addWidget(self.label_10)
        self.horizontalLayout.addLayout(self.distanceLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.Position = QtWidgets.QSlider(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Position.sizePolicy().hasHeightForWidth())
        self.Position.setSizePolicy(sizePolicy)
        self.Position.setMinimum(-99)
        self.Position.setOrientation(QtCore.Qt.Horizontal)
        self.Position.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.Position.setTickInterval(1000)
        self.Position.setObjectName("Position")
        self.horizontalLayout_3.addWidget(self.Position)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p>Drive the piston to the specified distance.</p></body></html>"))
        self.label_2.setText(_translate("Form", "Maxima:"))
        self.ResetButton.setText(_translate("Form", "Reset"))
        self.label_3.setText(_translate("Form", "Point"))
        self.Center.setText(_translate("Form", "0"))
        self.label_5.setText(_translate("Form", " is "))
        self.Distance.setText(_translate("Form", "0"))
        self.label_7.setText(_translate("Form", " unit from Point"))
        self.Start.setText(_translate("Form", "0"))
        self.label_10.setText(_translate("Form", "."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

