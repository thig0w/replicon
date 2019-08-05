# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qrcode.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import logging

from CamReader import CamReader
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from Sefaz import Sefaz
from phantomjs_bin import executable_path
from selenium import webdriver

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Ui_Dialog(object):
    def __init__(self):
        MAX_THREADS = 1
        self.nfes = {}
        self.web_drivers = []

        for i in range(MAX_THREADS):
            self.web_drivers.append(
                webdriver.PhantomJS(executable_path=executable_path)
            )

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(632, 262)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(280, 220, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(260, 10, 361, 201))
        # self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 241, 201))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 10, 221, 181))
        self.label.setObjectName("Camera")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def populate_table(self):
        col = 0
        self.tableWidget.setRowCount(len(self.nfes))
        for nf in self.nfes.__iter__():
            item_url = QtWidgets.QTableWidgetItem(self.nfes[nf].url)
            item_url.setFlags(QtCore.Qt.ItemIsEnabled)
            item_date = QtWidgets.QTableWidgetItem(self.nfes[nf].date)
            item_date.setFlags(QtCore.Qt.ItemIsEnabled)
            item_total_value = QtWidgets.QTableWidgetItem(self.nfes[nf].total_value)
            item_total_value.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(col, 0, item_url)
            self.tableWidget.setItem(col, 1, item_date)
            self.tableWidget.setItem(col, 2, item_total_value)
            col = col + 1

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Loading Camera..."))

    # @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
        self.populate_table()

    # @pyqtSlot('QString')
    def set_url(self, url):
        if not (self.nfes.__contains__(url)):
            self.nfes[url] = Sefaz(url, self.web_drivers.pop())
            self.nfes[url].start()


if __name__ == "__main__" or __name__ == "__builtin__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    th = CamReader()
    th.change_pixmap.connect(ui.setImage)
    th.found_qr.connect(ui.set_url)
    th.start()
    sys.exit(app.exec_())
