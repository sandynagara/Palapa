import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile

from qgis.PyQt import uic 
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog

from PyQt5.QtCore import QThread, pyqtSignal

from .upload import UploadDialog
from .login import LoginDialog