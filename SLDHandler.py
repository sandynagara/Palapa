import os
import requests
import json
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal

from math import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'SLDHandler.ui'))

class SLDDialog(QtWidgets.QDialog, FORM_CLASS):

    testing = pyqtSignal(object)
    
    def __init__(self, parent):
        super(SLDDialog, self).__init__(parent)
        self.setupUi(self)
        self.style_baru.toggled.connect(self.nama_file.setEnabled)
        self.accept.clicked.connect(self.panggil)

    def panggil(self):
        self.show()
        print("testing")
        self.testing.emit("tes")
        return "Testing"
   
    def SldName(self,sldPath,user,grup,simpulJaringan,url):
        self.show()
        filesSld = {'file': (f'{self.nama_file.text()}.sld', open(sldPath,'rb'))}
        params = {"USER":user,"GRUP":grup,"KODESIMPUL":simpulJaringan}
        urlSld = url+"/api/styles/add"
        responseAPISld = requests.post(urlSld,files=filesSld,params=params)
        responseAPISldJSON = json.loads(responseAPISld.text)
        if(responseAPISldJSON['MSG'] == 'Upload Success!'):
            return "ada file yang berbeda"
        else:
            return "ada file yang sama"
    