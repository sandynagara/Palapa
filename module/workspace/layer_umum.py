import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from PyQt5.QtCore import pyqtSignal,QThread
from qgis.core import QgsVectorLayer,QgsProject

from ..utils import readSetting
from ..models.dataset import Dataset
from ..informasi_layer_umum import InformasiLayer

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui/tab_layer_umum.ui'))

class LayerUmum(QtWidgets.QDialog, FORM_CLASS):

    UserLogout = pyqtSignal()

    def __init__(self, parent=iface.mainWindow()): 
        super(LayerUmum, self).__init__(parent)
        self.setupUi(self)
        
        self.btn_import.clicked.connect(self.downloadLayer)
        self.cariLayer.valueChanged.connect(self.findLayer)
        self.btn_informasi.clicked.connect(self.informasiLayer)
        self.refreshButton.clicked.connect(self.refresh_grid)
        self.pushButton_logout.clicked.connect(self.logout) 
        self.refresh_grid()

    #Handle logout
    def logout(self):
        self.UserLogout.emit()

    #Handle selected layer
    def get_selected_table(self):
        item = self.table.selectedItems()

        if(item == []):
            QtWidgets.QMessageBox.warning(
                None, "Palapa", "Pilih layer terlebih dahulu"
            )
            return

        row = item[0].row()
        dataSelect = []
    
        for x in range(self.table.columnCount()):
            dataSelect.append(self.table.item(row,x).text())
   
        return dataSelect

    #Menampilkan layer
    def informasiLayer(self):
        dataSelect = self.get_selected_table()

        if(dataSelect == None):
            return

        nativename = dataSelect[9]

        informasi = InformasiLayer(nativename)
        informasi.show()
    
    #Mendownload layer dan ditampilkan ke dalam QGIS melalui layanan WFS
    def downloadLayer(self):

        dataSelect = self.get_selected_table()

        if(dataSelect == None):
            return

        title = dataSelect[3]
        nativename = dataSelect[9]

        try:

            uri = f'{self.url}/geoserver/wms?service=WFS&version=1.0.0&request=GetFeature&typeName={nativename}'
            layer = QgsVectorLayer(uri, title, "WFS")
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

    # Mencari layer
    def findLayer(self):
        textto_find = self.cariLayer.value()
        result = [x for x in self.layerSpasial if x["layer_name"].lower().startswith(textto_find.lower()) and x["layer_aktif"]]
        print(textto_find)
        dataset = Dataset()
        table = dataset.add_table("Umum")
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
        
        for layer in result:
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

        dataset.render_to_qtable_widget("Umum", self.table,[0,5,7,8,9,10])

    # Merefresh tabel
    def refresh_grid(self):
        dataset = Dataset()
        table = dataset.add_table("Umum")
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

        self.url = readSetting("url")
        print(self.url)
        
        if(self.url is None):
            print(self.url)
            return

        response = requests.get(self.url+'/api/getWMSlayers')
        result = json.loads(response.content)
        self.layerSpasial = [x for x in result if x["layer_aktif"]]
        
        for layer in self.layerSpasial:
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

        dataset.render_to_qtable_widget("Umum", self.table,[0,5,7,8,9,10])

        
