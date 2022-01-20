import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QThreadPool

from ..publish.geoserver import Geoserver
from ..publish.worker import CheckConnectionWorker
#from ..StylePalapa import StylePalapa

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Connect_dialog.ui'))

class ConnectDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(ConnectDialog, self).__init__(parent)
        self.setupUi(self)
        self.QPushButton_test_connection.clicked.connect(self.runConnectionTest)
        self.QPushButton_connect.clicked.connect(self.connect)
        self.lineEdit_username.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_password.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_url.textChanged.connect(self.connectionValuesChanged)

        self.threadpool = QThreadPool()
        self.check_worker = None
    
    def printError(self, ex):
        QgsMessageLog.logMessage(message=str(ex), tag='SimpleWebGis', level=Qgis.Critical)

    # Connection Test    
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
        self.check_worker = CheckConnectionWorker(url=self.lineEdit_url.text(),
                                                  user=self.lineEdit_username.text(),
                                                  password=self.lineEdit_password.text())
        self.check_worker.signals.result.connect(self.connectionStatus)
        self.check_worker.signals.error.connect(self.printError)
        self.threadpool.start(self.check_worker)

    def connect(self):
        print("masyuk")


