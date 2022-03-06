import os
import json
import requests
from pickle import FALSE
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.PyQt.QtWidgets import QFileDialog
from .utils import readSetting
#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/unggah_berkas_metadata.ui'))

class UnggahBerkas(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self,identifier,akses, parent=iface.mainWindow()):
        super(UnggahBerkas, self).__init__(parent)
        self.setupUi(self)

        self.identifier = identifier
        self.akses = akses
        self.url = readSetting("url")

        self.browse_metadata.clicked.connect(self.start_browse_metadata)
        self.btn_update.clicked.connect(self.upload)
        self.btn_tutup.clicked.connect(self.closeTab)

    def closeTab(self):
        self.close()

    def start_browse_metadata(self):
        filter = "XML files (*.xml)"
        filename1, _ = QFileDialog.getOpenFileName(None, "Import XML", "",filter)
        self.lineEdit_metadata.setText(filename1)
        self.pathMeta = filename1

    def upload(self):
        try:
            filesMeta = {'file': open(self.pathMeta,'rb')}
            params = {"akses":self.akses,"identifier":self.identifier}
            urlMeta = self.url+"/api/meta/link"
            response = requests.post(urlMeta,files=filesMeta,params=params)
            upload= json.loads(response.content)
            print(upload)
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                upload["MSG"],
            )
        except:
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Metadata gagal di update",
            )
