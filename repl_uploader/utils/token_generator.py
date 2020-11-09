# -*- coding: utf-8 -*-
import json
import logging
import os

from PyQt5 import QtCore, QtWidgets
from appdirs import AppDirs
from requests import Session

# Starting logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TokenUiDialog(object):
    def __init__(self, tgen):
        self.tgen = tgen
        # Initialize QT screen
        logger.debug("Initializing interface")
        self.app = QtWidgets.QApplication([])
        self.Dialog = QtWidgets.QDialog()
        self.setup_ui(self.Dialog)
        self.Dialog.show()

        logger.debug("Starting app")
        self.return_code = self.app.exec_()

    def setup_ui(self, dialog):
        dialog.setObjectName("Dialog")
        dialog.resize(344, 155)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 110, 291, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.password = QtWidgets.QLineEdit(dialog)
        self.password.setGeometry(QtCore.QRect(10, 30, 321, 21))
        self.password.setInputMethodHints(QtCore.Qt.ImhHiddenText)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("le_password")
        self.label = QtWidgets.QLabel(dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 191, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 131, 16))
        self.label_2.setObjectName("label_2")
        self.confirmation_code = QtWidgets.QLineEdit(dialog)
        self.confirmation_code.setEnabled(False)
        self.confirmation_code.setGeometry(QtCore.QRect(10, 80, 321, 21))
        self.confirmation_code.setInputMethodHints(QtCore.Qt.ImhNone)
        self.confirmation_code.setObjectName("confirmation_code")

        self.retranslate_ui(dialog)
        self.buttonBox.accepted.connect(lambda: self.accept(dialog))
        self.buttonBox.rejected.connect(dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog)
        self.password.setFocus()

    def accept(self, dialog):
        logger.debug("Executing accept trigger")
        if len(self.password.text()) == 0:
            return False

        if not self.confirmation_code.isEnabled():
            check = self.tgen.generate_mail_confirmation(self.password.text())
            if not check:
                self.password.setText("")
                return False

        if len(self.confirmation_code.text()) == 0:
            self.password.setEnabled(False)
            self.confirmation_code.setEnabled(True)
            self.confirmation_code.setFocus()
            return False
        else:
            check = self.tgen.generate_token(
                self.confirmation_code.text(), self.password.text()
            )
            if not check:
                self.confirmation_code.setText("")
                return False
        dialog.accept()

    def retranslate_ui(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(
            _translate("Dialog", "Please insert your replicon password:")
        )
        self.label_2.setText(_translate("Dialog", "Code Received by e-mail:"))


class TGen:
    def __init__(self, company_id="logicinfo", user="tweidman"):
        self.company_id = company_id
        self.user = user

        self.__dirs = AppDirs(appname="repl_uploader", appauthor="thiagoweidman")
        os.makedirs(self.__dirs.user_config_dir, exist_ok=True)
        self.__filename = "repl.token"
        self.file = os.path.join(self.__dirs.user_config_dir, self.__filename)

        logger.debug(f"Opening config file to check token - {self.file}")
        try:
            with open(self.file, "r") as f:
                self.token = f.read()
        except FileNotFoundError:
            self.token = None
        self.s = Session()

    def get_token(self):
        if not self.check_token():
            ui = TokenUiDialog(self)
        return self.token

    def generate_mail_confirmation(self, password):
        data = {
            "cid": self.company_id,
            "user": self.user,
            "password": password,
            "remember": "false",
            "initdata": "",
            "loginProvider": "",
        }
        response = self.s.post(
            "https://login.replicon.com/Login.ashx", data=data, allow_redirects=True
        )

        try:
            self.d = json.loads(response.json()["errorHtml"])
        except json.decoder.JSONDecodeError:
            return False

        data = {
            "cid": self.company_id,
            "user": self.user,
            "passwd": password,
            "initData": "",
            "emailMethods": json.dumps(self.d["mfaEmails"]),
            "totpMethods": "[]",
            "loginStateUri": self.d["loginStateUri"],
        }

        response = self.s.post(
            "https://login.replicon.com/TwoFactorLogin.aspx", data=data
        )
        return True

    def generate_token(self, verification_code, password):
        data = {
            "cid": self.company_id,
            "user": self.user,
            "password": password,
            "loginProvider": "Replicon",
            "initdata": "",
            "mfaVerificationCode": verification_code,
            "mfaMethodUri": self.d["mfaEmails"][0]["uri"],
            "loginStateUri": self.d["loginStateUri"],
        }

        response = self.s.post("https://login.replicon.com/Login.ashx", data=data)

        error_text = response.json()["errorHtml"]
        try:
            if error_text.__contains__("Unknown Verification"):
                return False
        except AttributeError:
            pass

        data = '{"identity":{"loginName":"tweidman"},"description":"Token for logic\'s repl_uploader","unitOfWorkId":4956}'

        headers = {
            "Connection": "keep-alive",
            "accept": "*/*",
            "DNT": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://na5.replicon.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://na5.replicon.com/services/docs/security.html",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = self.s.post(
            "https://na5.replicon.com/services/AuthenticationService1.svc/CreateAccessToken2",
            data=data,
            headers=headers,
        )

        self.token = response.json()["d"]["token"]
        self.write_file()

        return True

    def write_file(self):
        try:
            with open(self.file, "w") as f:
                f.write(self.token)
        except FileNotFoundError:
            with open(self.file, "a") as f:
                f.write(self.token)

    def check_token(self):
        if self.token is None:
            return False

        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}

        response = self.s.post(
            "https://na5.replicon.com/services/UserAccessControlService1.svc/GetMyIdentity",
            headers=headers,
        )

        if response.status_code == 200:
            return True

        self.token = None
        return False


if __name__ == "__main__" or __name__ == "__builtin__":
    tk = TGen()
    tk.get_token()

    # tk.token = None
    # tk.get_token()
