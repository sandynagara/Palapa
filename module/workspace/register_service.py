from ast import keyword
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

    refresh = pyqtSignal()

    def __init__(self, parent=iface.mainWindow()): 
        super(RegisterService, self).__init__(parent)
        self.setupUi(self)

        self.btn_save.clicked.connect(self.upload)

    #Check kelas user 
    def checkUser(self):
        try:
            self.cmb_keyword.clear()
            self.url = readSetting("url")
            self.keyword =  readSetting("keyword")
            self.grup =  readSetting("grup")
            
            for x in self.keyword:
                self.cmb_keyword.addItem(x['keyword'])
        except Exception as err:
            print(err)

    # Upload register service
    def upload(self):   
        alamatService = self.lineEdit_alamat.text()
        titleService = self.lineEdit_title.text()
        abstrack = self.textEdit_abstrak.toPlainText()
        tanggal = self.date_tanggal.dateTime()
        tanggal = tanggal.toString("ddd MMM dd yyyy HH:mm:ss")
        keyword = self.cmb_keyword.currentText()
        akses = self.cmb_constraint.currentText()

        urlUpload = self.url+"/api/minmetadataarc"
        data = {"pubdata":
            {
            "tanggal": tanggal, 
            "ID":alamatService,
            "TITLE":titleService,
            "KEYWORD":keyword,
            "AKSES":akses,
            "WORKSPACE":self.grup,
            }
        }
        data = json.dumps(data)
        response = requests.post(urlUpload,data=f"dataPublish={data}")
        dataPublish = json.loads(response.content)
        if(dataPublish["MSG"] == "Metadata service disimpan!"):
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                dataPublish["MSG"],
            )
            self.refresh.emit()
        else:
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Metadata service gagal disimpan",
            )