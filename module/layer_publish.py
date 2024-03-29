import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from PyQt5.QtCore import pyqtSignal,QThread

from .utils import readSetting

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/publish_layer.ui'))

class LayerPublish(QtWidgets.QDialog, FORM_CLASS):

    refresh = pyqtSignal()

    def __init__(self,identifier,title,abstrack,aktif,advertised,style,nativename,tipe,parent=iface.mainWindow()): 
        super(LayerPublish, self).__init__(parent)
        self.setupUi(self)

        self.url = readSetting("url")   
        self.label_progress.setVisible(False)
        self.identifier = identifier
        self.title = title
        self.abstrack = abstrack
        if(aktif == "Ya"):
            self.aktif = True
        else:
            self.aktif = False
        if(advertised == "True"):
            self.advertised = True
        else:
            self.advertised = False
        self.style = style
        self.nativename = nativename
        self.tipe = tipe    

        #Menhandle publish dan unpublish data spasial
        if(self.aktif):
            self.label_layer.setText(f"Anda akan memunpublish layer {self.identifier}")
            self.label_unduh.setVisible(False)
            self.cmb_download.setVisible(False)
        else:
            self.label_layer.setText(f"Anda akan mempublish layer {self.identifier}")
            self.cmb_download.addItem("Pengunduhan data tidak diperbolehkan", "N")
            self.cmb_download.addItem("Pengunduhan data diperbolehkan", "Y")
            self.label_unduh.setVisible(True)
            self.cmb_download.setVisible(True)

        self.pushButton_proses.clicked.connect(self.upload)
        self.pushButton_tutup.clicked.connect(self.closeTab)

    def closeTab(self):
        self.close()

    #Menhandle proses publish
    def upload(self):
        self.thread = QThread()
        downloadable = self.cmb_download.currentData()
        self.label_progress.setVisible(True)
   
        self.label_progress.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;padding:4px")
        
        #Membedakan proses publish dan unpublish
        if(self.aktif):
            data = {"pubdata":
                {
                "id": self.identifier, 
                "title": self.title,
                "abstract":self.abstrack,
                "aktif":self.aktif,
                "advertised":self.advertised,
                "style":self.style,
                "nativename":self.nativename,
                "downloadable":"N",
                "tipe":self.tipe,
                }
            }
            self.label_progress.setText("Layer sedang diunpublish")
        else:
            data = {"pubdata":
                {
                "id": self.identifier, 
                "title": self.title,
                "abstract":self.abstrack,
                "aktif":self.aktif,
                "advertised":self.advertised,
                "style":self.style,
                "nativename":self.nativename,
                "downloadable":downloadable,
                "tipe":self.tipe,
                }
            }
            self.label_progress.setText("Layer sedang dipublish")
        data = json.dumps(data)

        self.worker = Worker(data,self.url,self.aktif)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.report)
        # print(data)
        # response = requests.post(urlUpload,data=f"dataPublish={data}")
        # print(response)
        # dataPublish = json.loads(response.content)
        # print(dataPublish)
        
    #Memberitahu tahap progress publish data
    def report(self,dataPublish):
        self.label_progress.setVisible(True)

        self.close()

        if(dataPublish == False):
            return

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
                "Layer gagal dipublish",
            )
        

class Worker(QThread):

    finished = pyqtSignal(object)
    
    def __init__(self, data, url ,aktif):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False 
        
        # initialize the stop variable
        self.url = url
        self.data = data
        self.aktif = aktif

    def run(self):
        """Long-running task."""
        urlUpload = self.url + "/api/layer/adv"
        try:
            response = requests.post(urlUpload,data=f"dataPublish={self.data}")
            dataPublish = json.loads(response.content)
            self.finished.emit(dataPublish)
        except Exception as err:
            if(self.aktif):
                QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    "Layer gagal diunpublish",
                )
            else:
                QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    "Layer gagal dipublish",
                )
            self.finished.emit(False)

          
        
       
        