import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.PyQt.QtWidgets import QTableWidgetItem
from ..models.dataset import Dataset

from ..utils import readSetting
from ..raw_metadata import RawMetadata
from ..unggah_berkas_metadata import UnggahBerkas
#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui/metadata_tab.ui'))

class Metadata(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=iface.mainWindow()):
        super(Metadata, self).__init__(parent)
        self.setupUi(self)
        self._rows = []

        self.btn_raw_meta.clicked.connect(self.raw_metadata)
        self.btn_publish_csw.clicked.connect(self.publikasi_csw)
        self.btn_hapus_meta.clicked.connect(self.hapus_csw)
        self.btn_update_meta.clicked.connect(self.unggah_berkas)

    def checkUser(self):
        self.kelas = readSetting("kelas")
        self.grup = readSetting("grup")
        self.url = readSetting("url")
        self.refresh_grid()
        if(self.kelas != "admin"):
            self.btn_hapus_meta.setEnabled(False)
            self.btn_publish_csw.setEnabled(False)

    def get_selected_table(self):

        item = self.table_metadata.selectedItems()

        if(item == []):
            QtWidgets.QMessageBox.warning(
                None, "Palapa", "Pilih metadata terlebih dahulu"
            )
            return

        row = item[0].row()
        dataSelect = []
   
        for x in range(self.table_metadata.columnCount()):
            dataSelect.append(self.table_metadata.item(row,x).text())
   
        return dataSelect
    

    def refresh_grid(self):
        dataset = Dataset()
        table = dataset.add_table("Metadata")
        table.add_column("Workspace")
        table.add_column("Identifier")
        table.add_column("Ada Metadata")
        table.add_column("Akses")
        table.add_column("Metadata Terpublikasi")
        table.add_column("downloadable")
        
        response = requests.get(self.url+'/api/meta/list')
        metaList = json.loads(response.content)
        
        for metadata in metaList:
            d_row = table.new_row()
            d_row["Workspace"] = metadata["workspace"]
            d_row["Identifier"] = metadata["identifier"]
            d_row["Ada Metadata"] = metadata["metatick"]
            d_row["Akses"] = metadata["akses"]
            d_row["Metadata Terpublikasi"] = metadata["published"]
            d_row["downloadable"] = metadata["downloadable"]

        dataset.render_to_qtable_widget("Metadata", self.table_metadata,[])
    
    def raw_metadata(self):
        dataSelect = self.get_selected_table()

        if(dataSelect[2] != "Y"):
            QtWidgets.QMessageBox.information(
                        None,
                        "Palapa",
                        "Data tidak memiliki metadata",
            )
            return

        raw_meta = RawMetadata(dataSelect[1],dataSelect[0])
        raw_meta.show()

    def publikasi_csw(self):
        dataSelect = self.get_selected_table()

        if(dataSelect[2] != "Y"):
            QtWidgets.QMessageBox.information(
                        None,
                        "Palapa",
                        "Data tidak memiliki metadata",
            )
            return
        
        prmpt = f"Anda akan mempublish metadata {dataSelect[1]}"
        result = QtWidgets.QMessageBox.question(self, "Perhatian", prmpt)

        if(result != QtWidgets.QMessageBox.Yes):
            return
    
        # params = {"identifier":dataSelect[1]}
        # response = requests.get(self.url+'/api/meta/view',params=params)
        # metaView = json.loads(response.content)

        identifier = dataSelect[1]
        workspace = dataSelect[0]
        akses = dataSelect[3]
        downloadable = dataSelect[5]
        
        urlUpload = self.url+"/api/pycswRecord/insert"
        data = {"pubdata":
            {
            "identifier": identifier, 
            "workspace": workspace,
            "downloadable":downloadable,
            "akses":akses,
            }
        }
        try:
            data = json.dumps(data)
            response = requests.post(urlUpload,data=f"dataPublish={data}")
            metaCsw = json.loads(response.content)
            QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    metaCsw["MSG"],
            )
            self.refresh_grid()
        except:
            QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    "Metadata gagal dipublish servis CSW!",
            )

    def hapus_csw(self):
        dataSelect = self.get_selected_table()
        identifier = dataSelect[1]
        workspace = dataSelect[0]   

        prmpt = f"Yakin akan unpublish service CSW {dataSelect[1]}"
        result = QtWidgets.QMessageBox.question(self, "Perhatian", prmpt)

        if(result != QtWidgets.QMessageBox.Yes):
            return

        urlUpload = self.url+"/api/pycswRecord/delete"
        data = {"pubdata":
            {
            "identifier": identifier, 
            "workspace": workspace,
            }
        }

        try:
            data = json.dumps(data)
            response = requests.post(urlUpload,data=f"dataPublish={data}")
            hapusCsw = json.loads(response.content)

            QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    hapusCsw["MSG"],
            )
            print(hapusCsw)
            self.refresh_grid()

        except:
            QtWidgets.QMessageBox.information(
                    None,
                    "Palapa",
                    "Metadata gagal diunpublish servis CSW!",
            )
    
    def unggah_berkas(self):
        dataSelect = self.get_selected_table()

        workspace = dataSelect[0]

        if(workspace != self.grup and self.kelas != "admin"):
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Anda Tidak punya akses untuk mengedit metadata ini",
            )
            return

        unggahBerkas = UnggahBerkas(dataSelect[1],dataSelect[0])
        unggahBerkas.show()

   

