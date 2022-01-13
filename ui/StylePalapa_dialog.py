import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'StylePalapa_dialog_base.ui'))

class StylePalapaDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(StylePalapaDialog, self).__init__(parent)
        self.setupUi(self)
        self.upload.clicked.connect(self.import_layer)
        self.browse_metadata.clicked.connect(self.start_browse_metadata)
        self.browse_layer.clicked.connect(self.start_browse_layer)
        
    def import_layer(self):
        layerName = self.select_layer.currentText()
        print(layerName)
        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        layer.saveSldStyle(f'D:/{layerName}.sld')
        os.remove(f'D:/{layerName}.sld')

    def start_browse_metadata(self):
        filename1, _ = QFileDialog.getOpenFileName()
        print(filename1)
        self.lineEdit_metadata.setText(filename1)

    def start_browse_layer(self):
        filename2, _ = QFileDialog.getOpenFileName()
        print(filename2)