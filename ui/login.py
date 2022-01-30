import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile
import codecs

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog

from PyQt5.QtCore import QThread, pyqtSignal

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UploadPalapa_login.ui'))

class LoginDialog(QtWidgets.QDialog, FORM_CLASS):

    UserSignal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """Constructor."""
        super(LoginDialog, self).__init__(parent)
        self.setupUi(self)
        #Tab1
        self.QPushButton_test_connection.clicked.connect(self.runConnectionTest)
        self.lineEdit_username.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_password.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_url.textChanged.connect(self.connectionValuesChanged)      

    # Connection Test Tab1 
    def connectionValuesChanged(self):
        self.label_status.setText('')
        self.label_status.setStyleSheet("")       

    def runConnectionTest(self):
        # Clean label
        self.connectionValuesChanged()

        # login
        url_login=self.lineEdit_url.text()
        user=self.lineEdit_username.text()
        password=self.lineEdit_password.text()

        login_payload = {"username": user, "password": password}
        login_json = json.dumps(login_payload)
        login_api = '/api/login'
        url = url_login+login_api

        try:
            response_API = requests.post(url, data = login_json)
            responseApiJson = json.loads(response_API.text)
            print(response_API.text)
            if response_API.status_code == 200:
                status = responseApiJson['MSG']
                if status == 'Valid Info':             
                    if(responseApiJson['Result']):
                        self.label_status.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;")
                        self.label_status.setText('Terhubung')
                        self.grup = responseApiJson['grup']
                        self.user = responseApiJson['user']
                        self.url = url_login
                        responseSimpul = requests.get(self.url+'/api/sisteminfo')
                        responseSimpul = json.loads(responseSimpul.text)
                        self.simpulJaringan = responseSimpul['kodesimpul'].split(",")[0]


                        signalsend = {"grup": self.grup, "user": self.user, "url": self.url, "kodesimpul": self.simpulJaringan}
                        self.UserSignal.emit(signalsend)
                        #self.close()
                        print(signalsend)

                    print(responseApiJson)
                else:
                    self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
                    self.label_status.setText(status)
            else:
                self.label_status.setText('Cek URL atau koneksi internet Anda')        
        except Exception as err:
            print(err)
            self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
            self.label_status.setText('Cek URL atau koneksi internet Anda')