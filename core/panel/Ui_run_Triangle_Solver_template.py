# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ahshoe/Desktop/Pyslvs-PyQt5/core/panel/run_Triangle_Solver_template.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(861, 663)
        Dialog.setMinimumSize(QtCore.QSize(861, 663))
        Dialog.setMaximumSize(QtCore.QSize(861, 663))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/TS.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setModal(True)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.templatePanel = QtWidgets.QGroupBox(Dialog)
        self.templatePanel.setObjectName("templatePanel")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.templatePanel)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.templateType = QtWidgets.QComboBox(self.templatePanel)
        self.templateType.setMinimumSize(QtCore.QSize(120, 0))
        self.templateType.setObjectName("templateType")
        self.templateType.addItem("")
        self.templateType.addItem("")
        self.verticalLayout_2.addWidget(self.templateType)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.templatePanel)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.triangleTable = QtWidgets.QTableWidget(self.groupBox_2)
        self.triangleTable.setObjectName("triangleTable")
        self.triangleTable.setColumnCount(4)
        self.triangleTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.triangleTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.triangleTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.triangleTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.triangleTable.setHorizontalHeaderItem(3, item)
        self.verticalLayout_4.addWidget(self.triangleTable)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.verticalLayout_6.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.previewPanel = QtWidgets.QGroupBox(Dialog)
        self.previewPanel.setObjectName("previewPanel")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.previewPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.templateImage = QtWidgets.QLabel(self.previewPanel)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.templateImage.sizePolicy().hasHeightForWidth())
        self.templateImage.setSizePolicy(sizePolicy)
        self.templateImage.setMinimumSize(QtCore.QSize(500, 400))
        self.templateImage.setText("")
        self.templateImage.setObjectName("templateImage")
        self.verticalLayout.addWidget(self.templateImage)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addWidget(self.previewPanel)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Parameters = QtWidgets.QGroupBox(Dialog)
        self.Parameters.setObjectName("Parameters")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Parameters)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.Parameters)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.parameterTable = QtWidgets.QTableWidget(self.Parameters)
        self.parameterTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.parameterTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.parameterTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.parameterTable.setObjectName("parameterTable")
        self.parameterTable.setColumnCount(2)
        self.parameterTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.parameterTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.parameterTable.setHorizontalHeaderItem(1, item)
        self.verticalLayout_3.addWidget(self.parameterTable)
        self.verticalLayout_5.addWidget(self.Parameters)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_5.addWidget(self.buttonBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Template"))
        self.templatePanel.setTitle(_translate("Dialog", "Template"))
        self.templateType.setItemText(0, _translate("Dialog", "4-bar linkage"))
        self.templateType.setItemText(1, _translate("Dialog", "8-bar linkage"))
        self.groupBox_2.setTitle(_translate("Dialog", "Triangles"))
        item = self.triangleTable.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Type"))
        item = self.triangleTable.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Point[1]"))
        item = self.triangleTable.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Point[2]"))
        item = self.triangleTable.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Point[3]"))
        self.previewPanel.setTitle(_translate("Dialog", "Preview"))
        self.Parameters.setTitle(_translate("Dialog", "Parameters"))
        self.label.setText(_translate("Dialog", "All points should not be repeated."))
        item = self.parameterTable.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Name"))
        item = self.parameterTable.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Point"))

import icons_rc
import preview_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

