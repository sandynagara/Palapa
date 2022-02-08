from distutils.command.upload import upload
import os
import requests
import json
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import pyqtSignal

from math import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'SLDHandler.ui'))

class SLDDialog(QtWidgets.QDialog, FORM_CLASS):

    uploadStyle = pyqtSignal(object)
    
    def __init__(self,user,grup,simpulJaringan,url,sldPath,sldqgis,parent=None):
        super(SLDDialog, self).__init__(parent)
        self.setupUi(self)
        self.style_baru.toggled.connect(self.nama_file.setEnabled)
        self.accept.clicked.connect(self.SldName)
        self.user=user
        self.grup=grup
        self.simpulJaringan=simpulJaringan
        self.url=url
        self.sldPath = sldPath
        self.sldqgis = sldqgis
        self.namaLama = sldPath.split(".")[0].split("/")[-1]
        self.label.setText(f'Maaf ,Style dengan nama "{self.namaLama}" sudah ada')
        self.nama_file.setText(self.namaLama)
   
    def SldName(self):
        if self.style_baru.isChecked():
            self.show()
            filesSld = {'file': (f'{self.nama_file.text()}.sld', open(self.sldPath,'rb'))}
            title , open2 = filesSld["file"]
            params = {"USER":self.user,"GRUP":self.grup,"KODESIMPUL":self.simpulJaringan}
            urlSld = self.url+"/api/styles/add"
            responseAPISld = requests.post(urlSld,files=filesSld,params=params)
            responseAPISldJSON = json.loads(responseAPISld.text)
            print(responseAPISld)
            if(responseAPISldJSON['MSG'] == 'Upload Success!'):
                open2.close()
                if (self.sldqgis == True):
                    print('hapus sld')
                    os.remove(self.sldPath)
                self.uploadStyle.emit({"nama":self.nama_file.text(),"path":self.sldPath, "new":True})
                self.close()
            else:
                self.label.setText(f'Maaf ,Style dengan nama "{self.nama_file.text()}" sudah ada')
                print("file sama")
        else:
            self.close()
            if (self.sldqgis == True):
                print('hapus sld')
                os.remove(self.sldPath)
            self.uploadStyle.emit({"nama":self.nama_file.text(),"path":self.sldPath, "new":False})
            self.close()


    