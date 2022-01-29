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

#from .worker import Worker

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'report_dialog.ui'))

class ReportDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(ReportDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.reportReset()

    def report(self, label, result, message):
        if result is True:
            label.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;") 
        elif result == 'reset':
            label.setStyleSheet("background-color: none; border-radius: 4px;")
        elif result == 'caution':
            label.setStyleSheet("color: white; background-color: #F28F1E; border-radius: 4px;")
        else :
            label.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
        label.setText(message)

    def reportReset(self):
        self.report(self.label_statusSLD, 'reset', '')
        self.report(self.label_statusLayer, 'reset', '')
        self.report(self.label_statusMetadata, 'reset', '')
        self.report(self.label_statusPublish, 'reset', '')
        #self.report(self.label_statusbase, 'reset', '')