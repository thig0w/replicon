# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qrcode.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import logging
import sys
import threading

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from chromedriver_binary import chromedriver_filename
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from repl_uploader import replicon_ws
from repl_uploader.pyqt.CamReader import CamReader
from repl_uploader.pyqt.Sefaz import Sefaz

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UiDialog(object):
    def __init__(self):
        self.nfes = {}
        self.web_driver = None
        self.buttonBox = None
        self.tableWidget = None
        self.groupBox = None
        self.label = None
        self.webdriver_lock = threading.Lock()
        self.list_lock = threading.Lock()

        # Initialize QT screen
        logger.debug("Initializing interface")
        self.app = QtWidgets.QApplication(sys.argv)
        self.Dialog = QtWidgets.QDialog()
        self.setup_ui(self.Dialog)
        self.Dialog.show()
        self.th = CamReader()
        self.th.change_pixmap.connect(self.set_image)
        self.th.found_qr.connect(self.set_url)
        self.th.start()

        logger.debug("Starting app")
        self.return_code = self.app.exec_()

    def __del__(self):
        if self.web_driver is not None:
            logger.debug("Closing web driver!")
            self.web_driver.quit()

    def setup_ui(self, dialog):
        dialog.setObjectName("Dialog")
        dialog.resize(632, 262)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialog)
        self.buttonBox.setGeometry(QtCore.QRect(280, 220, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.tableWidget = QtWidgets.QTableWidget(dialog)
        self.tableWidget.setGeometry(QtCore.QRect(260, 10, 361, 201))
        # self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget.verticalHeader().setVisible(False)
        self.groupBox = QtWidgets.QGroupBox(dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 241, 201))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 10, 221, 181))
        self.label.setObjectName("Camera")

        self.retranslate_ui(dialog)
        self.buttonBox.accepted.connect(lambda: self.accept(dialog))
        self.buttonBox.rejected.connect(dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def accept(self, dialog):
        logger.debug("Executing accept trigger")
        list = []
        for i in self.nfes:
            list.append([self.nfes[i].date, self.nfes[i].total_value])
            self.nfes[i].save_image(replicon_ws.get_repl_folder())
        replicon_ws.fill_xl_from_list(list)
        # call replicon_ws to fill the excel and generate the images
        dialog.accept()

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

    def retranslate_ui(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Loading Camera..."))

    # @pyqtSlot(QImage)
    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
        self.populate_table()
        if self.web_driver is None:
            logger.debug("Initializing web browser")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.web_driver = webdriver.Chrome(
                executable_path=chromedriver_filename, chrome_options=chrome_options
            )

    # @pyqtSlot('QString')
    def set_url(self, url):
        self.list_lock.acquire()
        if (
            not (self.nfes.__contains__(url))
            and url is not None
            and str(url).startswith("http")
        ):
            logger.debug("Initializing Sefaz Class for url: %s", url)
            self.nfes[url] = Sefaz(url, self.web_driver, self.webdriver_lock)
            self.nfes[url].start()
        self.list_lock.release()


if __name__ == "__main__" or __name__ == "__builtin__":
    # app = QtWidgets.QApplication(sys.argv)
    # Dialog = QtWidgets.QDialog()
    # ui = Ui_Dialog()
    # ui.setupUi(Dialog)
    # Dialog.show()
    # th = CamReader()
    # th.change_pixmap.connect(ui.setImage)
    # th.found_qr.connect(ui.set_url)
    # th.start()
    # sys.exit(app.exec_())
    ui = UiDialog()
    sys.exit(ui.return_code)
