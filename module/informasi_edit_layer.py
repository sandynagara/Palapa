import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from .utils import readSetting
from PyQt5.QtCore import pyqtSignal,QThread
from qgis.core import QgsVectorLayer,QgsProject,QgsDataSourceUri

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/info_edit_layer.ui'))

class InformasiEditLayer(QtWidgets.QDialog, FORM_CLASS):

    refresh = pyqtSignal()

    def __init__(self,tipe,id,title,abstract,srs,styleInput,nativeName=None,tipeLayer=None,aktif=False, parent=iface.mainWindow()): 
        super(InformasiEditLayer, self).__init__(parent)
        self.setupUi(self)

        self.nativeName = nativeName
        self.aktif = aktif
        self.tipeLayer = tipeLayer
        self.tipe = tipe
        self.title = title
        self.styleInput = styleInput

        self.lineEdit_id.setText(id)
        self.lineEdit_title.setText(title)
        self.textEdit_abstract.setText(abstract)
        self.lineEdit_srs.setText(srs)

        self.url = readSetting("url")
        self.user = readSetting("user")
        self.password = readSetting("password")

    # Mengandle tombol close
    def closeTab(self):
        self.close()

    def setupWorkspace(self):
        #Mendownload daftar style
        try:
            urlStyle= self.url+"/api/getstyles"
            response = requests.get(urlStyle)
            DaftarStyle = json.loads(response.content)

            #Memasuukan style ke dalam combo box
            for style in DaftarStyle:
                self.cmb_style.addItem(style['name'])

            #Mensetting combox box agar sesuai dengan yang dipilih user
            indexSytle = self.cmb_style.findText(self.styleInput)
            self.cmb_style.setCurrentIndex(indexSytle)

            #Mensetting agar id dan srs tidak bisa diedit
            self.lineEdit_id.setReadOnly(True)
            self.lineEdit_srs.setReadOnly(True)
            self.label_status.setVisible(False)
            if(self.tipe == "info"):
                self.download_layer.setText("Lihat Layer")
                self.lineEdit_title.setReadOnly(True)
                self.textEdit_abstract.setReadOnly(True)
                self.lineEdit_srs.setReadOnly(True)
                self.cmb_style.setEnabled(False)
                self.btn_save.setVisible(False)
            
            self.btn_tutup.clicked.connect(self.closeTab)
            self.btn_save.clicked.connect(self.updateLayer)
            self.download_layer.clicked.connect(self.downloadLayer)

            self.open()
        except Exception as err:
            self.close()
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Gagal mendapatkan informasi layer. Silahkan periksa koneksi internet anda",
            )
            
     
            


    # Mengimport layer ke dalam QGIS
    def downloadLayer(self):
        try:
            # Mengatur url 
            uri = QgsDataSourceUri()
            if(self.tipe == "info"):  
                uri = f'{self.url}/geoserver/wms?service=WFS&version=1.0.0&request=GetFeature&typeName={self.nativeName}'
                layer = QgsVectorLayer(uri, self.title, "WFS")
            else:
                uri.setParam('typename', self.nativeName)
                uri.setParam('srsName', 'EPSG:4326')
                uri.setParam('service', 'WFS')
                uri.setParam('version', '1.0.0')
                uri.setParam('request', 'GetFeature')
                uri.setUsername(self.user)
                uri.setPassword(self.password)
                uri.setParam('url', f'{self.url}/geoserver/wms')
                layer = QgsVectorLayer(uri.uri(), self.title, "WFS")
              
            # Menmassukan layer ka dalam QGIS sebagai layanan WFS
            
            QgsProject.instance().addMapLayer(layer)
            if not layer.isValid():
                print("Layer failed to load!")
            iface.actionZoomToLayer().trigger()
            QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    "Layer berhasil di import",
            )
        except Exception as err:
            print(err)
            QtWidgets.QMessageBox.warning(
                None, "Palapa", "Layer gagal di import"
            )

    # Handle update informasi layer
    def updateLayer(self):
        self.thread = QThread()
        id = self.lineEdit_id.text()
        title = self.lineEdit_title.text()
        abstract = self.textEdit_abstract.toPlainText() 
        style = self.cmb_style.currentText()

        self.label_status.setVisible(True)
        self.label_status.setText("Layer sedang diproses")
        self.label_status.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;")
        dataPublish = {"pubdata":{"id": id,"aktif":self.aktif, "tipe": self.tipeLayer,"abstract":abstract,"nativename":self.nativeName,"style":style,"title":title}}
        dataPublish = json.dumps(dataPublish)
    
        #Memindahkan proses update ke dalam Thread untuk menghindari freeze
        self.worker = Worker(dataPublish,self.url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.report)
        self.thread.start()

    #Menampilkan progress updating
    def report(self,dataPublish):
        self.close()


        if(dataPublish["RTN"]):
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
                "Layer gagal diedit",
            )
        

class Worker(QThread):

    finished = pyqtSignal(object)
    
    def __init__(self, data, url ,sldName=False):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False # initialize the stop variable
        self.url = url
        self.data = data

    def run(self):
        """Long-running task."""
        url = self.url + "/api/layers/modify"
        try:
            response = requests.post(url,data=f"dataPublish={self.data}")
            dataPublish = json.loads(response.content)
            self.finished.emit(dataPublish)
        except Exception as err:
            print(err)

