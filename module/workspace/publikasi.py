import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from PyQt5.QtCore import pyqtSignal,QThread

from ..models.dataset import Dataset
from ..utils import readSetting
from ..layer_publish import LayerPublish
from ..informasi_edit_layer import InformasiEditLayer

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui/publikasi_tab.ui'))

class Publikasi(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=iface.mainWindow()): 
        super(Publikasi, self).__init__(parent)
        self.setupUi(self)

        self.btn_informasi.clicked.connect(self.informasi)
        self.btn_edit.clicked.connect(self.edit)
        self.btn_publikasi.clicked.connect(self.publikasi)
        self.btn_hapus.clicked.connect(self.hapus)

    def checkUser(self):
        self.kelas = readSetting("kelas")
        self.grup = readSetting("grup")
        self.url = readSetting("url")
        self.refresh_grid()
        if(self.kelas != "admin"):
            self.btn_publikasi.setEnabled(False)
            self.btn_hapus.setEnabled(False)

    def get_selected_table(self):

        item = self.table_publikasi.selectedItems()

        if(item == []):
            QtWidgets.QMessageBox.warning(
                None, "Palapa", "Pilih layer terlebih dahulu"
            )
            return

        row = item[0].row()
        dataSelect = []
   
        for x in range(self.table_publikasi.columnCount()):
            dataSelect.append(self.table_publikasi.item(row,x).text())
   
        return dataSelect
    

    def refresh_grid(self):
        dataset = Dataset()
        table = dataset.add_table("Publikasi")
        table.add_column("identifier")
        table.add_column("Last Modified")
        table.add_column("Workspace")
        table.add_column("Layer Titel")
        table.add_column("Jenis")
        table.add_column("Aktif Terpublikasi")
        table.add_column("SRS")
        table.add_column("advertised")
        table.add_column("style")
        table.add_column("nativename")
        table.add_column("layer_abstract")
        
        response = requests.get(self.url+'/api/getWMSlayers')
        print(response.url)
        layerSpasial = json.loads(response.content)
        print(layerSpasial)
        
        for layer in layerSpasial:
            d_row = table.new_row()
            d_row["identifier"] = layer["layer_id"]
            d_row["Last Modified"] = layer["last_modified"]
            d_row["Workspace"] = layer["workspace"]
            d_row["Layer Titel"] = layer["layer_name"]
            d_row["Jenis"] = layer["layer_type"]
            if(layer["layer_aktif"]):
                d_row["Aktif Terpublikasi"] = "Ya"
            else:
                d_row["Aktif Terpublikasi"] = "Tidak"
            d_row["SRS"] = layer["layer_srs"]
            d_row["advertised"] = layer["layer_advertised"]
            d_row["style"] = layer["layer_style"]
            d_row["nativename"] = layer["layer_nativename"]
            d_row["layer_abstract"] = layer["layer_abstract"]

        dataset.render_to_qtable_widget("Publikasi", self.table_publikasi,[0,7,8,9,10])

    def publikasi(self):
        try:
            dataSelect = self.get_selected_table()
            print(dataSelect)

            if(dataSelect == None):
                return

            id = dataSelect[0]
            title = dataSelect[3]
            abstrack = dataSelect[10]
            aktif = dataSelect[5]
            advertised = dataSelect[7]
            style = dataSelect[8]
            nativename = dataSelect[9]
            tipe = dataSelect[4]

            layerPublish = LayerPublish(id,title,abstrack,aktif,advertised,style,nativename,tipe)
            layerPublish.show()
            layerPublish.refresh.connect(self.refresh_grid)
        except Exception as err:
            print(err)
         

    def informasi(self):
        dataSelect = self.get_selected_table()

        if(dataSelect == None):
            return

        id = dataSelect[0]
        title = dataSelect[3]
        abstrack = dataSelect[10]
        srs = dataSelect[6]
        style = dataSelect[8]
          
        informasiEditLayer = InformasiEditLayer("info",id,title,abstrack,srs,style)
        informasiEditLayer.show()
        informasiEditLayer.refresh.connect(self.refresh_grid)

    def hapus(self):
        self.thread = QThread()

        dataSelect = self.get_selected_table()

        if(dataSelect == None):
            return

        id = dataSelect[0]
        workspace = dataSelect[2]

        prmpt = f"Anda akan menghapus layer {id}"
        result = QtWidgets.QMessageBox.question(self, "Perhatian", prmpt)

        if(result != QtWidgets.QMessageBox.Yes):
            return

        data = {"pubdata":
                    {
                    "layer": id, 
                    "workspace": workspace,
                    }
                }
        data = json.dumps(data)

        self.worker = Worker(data,self.url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.runHapus)
        self.thread.start()
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.reportDelete)

    def reportDelete(self,dataPublish):
        self.refresh_grid()
        if(dataPublish["RTN"]):
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                dataPublish["MSG"],
            )
        
        else:
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Layer gagal dihapus",
        )

    def edit(self):
        dataSelect = self.get_selected_table()

        if(dataSelect == None):
            return

        id = dataSelect[0]
        title = dataSelect[3]
        abstrack = dataSelect[10]
        workspace = dataSelect[2]
        aktif = dataSelect[5]
        srs = dataSelect[6]
        style = dataSelect[8]
        nativename = dataSelect[9]
        tipe = dataSelect[4]
        
        if(workspace != self.grup and self.kelas != "admin"):
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Anda Tidak punya akses untuk mengedit file ini",
            )
            return

        informasiEditLayer = InformasiEditLayer("edit",id,title,abstrack,srs,style,nativename,tipe,aktif)
        informasiEditLayer.show()

class Worker(QThread):

    finished = pyqtSignal(object)
    
    def __init__(self, data, url):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False # initialize the stop variable

        self.url = url
        self.data = data

    def runHapus(self):
        """Long-running task."""
        urlUpload = self.url + "/api/layers/delete"
        response = requests.post(urlUpload,data=f"dataPublish={self.data}")
        print(response)
        dataPublish = json.loads(response.content)
        print(dataPublish)
        self.finished.emit(dataPublish)