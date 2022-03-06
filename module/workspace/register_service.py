import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from PyQt5.QtCore import pyqtSignal,QThread

from ..utils import readSetting

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui/register_metadata_service.ui'))

class RegisterService(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=iface.mainWindow()): 
        super(RegisterService, self).__init__(parent)
        self.setupUi(self)

        self.keyword =  readSetting("keyword")
        for x in self.keyword:
            self.cmb_keyword.addItem(x['keyword'])

        self.btn_save.clicked.connect(self.upload)

    def upload(self):
        pass