import os
import json
import requests

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QThreadPool

from ..publish.geoserver import Geoserver
from ..publish.worker import CheckConnectionWorker

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UploadPalapa_dialog.ui'))

class PalapaDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(PalapaDialog, self).__init__(parent)
        self.setupUi(self)
        #Tab1
        self.QPushButton_test_connection.clicked.connect(self.runConnectionTest)
        self.lineEdit_username.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_password.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_url.textChanged.connect(self.connectionValuesChanged)
        #Tab2
        self.upload.clicked.connect(self.import_layer)
        self.browse_metadata.clicked.connect(self.start_browse_metadata)
        self.browse_style.clicked.connect(self.start_browse_style)

        self.radioButton_StyleBrowse.toggled.connect(self.browse_style.setEnabled)
        self.radioButton_StyleBrowse.toggled.connect(self.lineEdit_style.setEnabled)

        self.threadpool = QThreadPool()
        self.check_worker = None
    
    def printError(self, ex):
        QgsMessageLog.logMessage(message=str(ex), tag='SimpleWebGis', level=Qgis.Critical)

    # Connection Test Tab1 
    def connectionValuesChanged(self):
        self.label_status.setText('')
        self.label_status.setStyleSheet("")       

    def connectionStatus(self, err_status):
        if err_status:
            self.label_status.setStyleSheet("background-color: rgb(255, 0, 0)")
            self.label_status.setText(err_status)
        else:
            self.label_status.setStyleSheet("background-color: lightgreen")
            self.label_status.setText('Terhubung')

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
        response_API = requests.post(url, login_payload)
        print(url)
        print(response_API.text)
        print(response_API.status_code)
        

    #Upload Tab2
    def import_layer(self):
        layerName = self.select_layer.currentText()
        print(layerName)
        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        layer.saveSldStyle(f'D:/{layerName}.sld')
        os.remove(f'D:/{layerName}.sld')

    def start_browse_metadata(self):
        filename1, _ = QFileDialog.getOpenFileName()
        print(filename1)
        self.lineEdit_metadata.setText(filename1)

    def start_browse_style(self):
        filename2, _ = QFileDialog.getOpenFileName()
        print(filename2)
        self.lineEdit_style.setText(filename2)


