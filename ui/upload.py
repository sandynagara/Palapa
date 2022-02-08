import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal

from .login import LoginDialog
from .SLDHandler import SLDDialog
from .worker import Worker
from .report import ReportDialog



#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UploadPalapa_main.ui'))

class UploadDialog(QtWidgets.QDialog, FORM_CLASS):

    UserLogout = pyqtSignal()
  
    def __init__(self, parent=None):
        """Constructor."""
        super(UploadDialog, self).__init__(parent)
        self.setupUi(self)
        self.login = LoginDialog()
     
        # self.login.UserSignal.connect(self.UserParam)
        self.upload.setEnabled(True)
        self.upload.clicked.connect(self.checking)
        self.browse_metadata.clicked.connect(self.start_browse_metadata)
        self.browse_style.clicked.connect(self.start_browse_style)
        self.url = None
        self.simpulJaringan=None
        self.grup = None
        self.user=None
        self.pathMeta = None
        self.pathSLD = None
        self.MetaRun = False
        self.pathSLD = None
        self.UserParams = None
        self.LayerParams = None
        self.filesSld = None
        self.SLDqgis = False
        self.lineEdit_metadata.setReadOnly(True)
        self.lineEdit_style.setReadOnly(True)
        self.radioButton_StyleBrowse.toggled.connect(self.browse_style.setEnabled)
        self.radioButton_StyleBrowse.toggled.connect(self.lineEdit_style.setEnabled)
        self.pushButton_clearStyle.clicked.connect(self.clearStyle)
        self.pushButton_clearMetadata.clicked.connect(self.clearMetadata)
        self.select_layer.currentTextChanged.connect(self.changeTitle)
        self.pushButton_logout.clicked.connect(self.logout)      


        self.ReportDlg = ReportDialog()
        #self.LoginDialog = LoginDialog
        #self.LoginDialog.UserSignal.connect(self.UserParam)

    def changeTitle(self):
        layerName = self.select_layer.currentText()
        self.lineEdit_layertitle.setText(layerName)

    def UserParam(self, signalpayload):
        print('signal nangkep',signalpayload)
        self.grup = signalpayload['grup']
        self.user = signalpayload['user']
        self.url = signalpayload['url']
        self.simpulJaringan = signalpayload['kodesimpul']
        layerName = self.select_layer.currentText()
        self.lineEdit_layertitle.setText(layerName)
        self.label_userdesc.setText(f"Anda masuk sebagai '{self.user}' pada '{self.url}'")
        urlKeyword = self.url+"/api/keyword/list"
        responseKeyword = requests.get(urlKeyword)
        self.comboBox_constraint.setCurrentIndex(0)
        self.comboBox_keyword.clear()
        for x in responseKeyword.json():
            self.comboBox_keyword.addItem(x['keyword'])
        self.comboBox_keyword.setCurrentIndex(0)
        print(signalpayload)
    
    def logout(self):
        self.UserLogout.emit()

    ### Cek kelengkapan
    def checking(self):
        self.checkEPSG()
        self.ReportDlg.reportReset()
        self.reportReset()
        self.report(self.label_statusbase, 'process', 'Mengecek data . . .')
        if((self.radioButton_StyleBrowse.isChecked() and self.pathSLD == '') or (self.radioButton_StyleBrowse.isChecked() and self.pathSLD == None)):
            self.report(self.label_statusbase, 'caution', 'Masukkan SLD atau gunakan SLD bawaan')
            print('masukkan SLD atau gunakan sld bawaan')
        else:
            layerPath = self.exportLayer()
            # define layer parameter
            self.LayerParams = layerPath
            if self.checkFileExist(layerPath['shp']) and self.checkFileExist(layerPath['dbf']) and self.checkFileExist(layerPath['shx']) and self.checkFileExist(layerPath['prj']) :
                print("file Lengkap")
                if(self.radioButton_StyleQgis.isChecked()):      
                    self.SLDqgis = True              
                    sldPath = self.exportSld()
                elif(self.radioButton_StyleBrowse.isChecked() and (self.pathSLD != '' or self.pathSLD != None)):    
                    sldPath = self.pathSLD
                # define SLD parameter
                self.filesSld = {'file': open(sldPath,'rb')}
                print(self.filesSld)
                if (self.pathMeta is not None and self.pathMeta != ''):
                    print('metajalan',self.pathMeta)         
                    self.MetaRun = True
                self.filesSld['file'].close()
                self.report(self.label_statusbase, True, 'Data lengkap, mulai mengunggah . . .')
                self.runUpload()
            else :
                print("file Tidak Lengkap")
                self.report(self.label_statusbase, False, 'File tidak lengkap')

    def runUpload(self,sldName=False):
        self.thread = QThread()
        title = self.lineEdit_layertitle.text()
        abstrack = self.textEdit_layerabstract.toPlainText() 
        tanggal = self.mDateTimeEdit.dateTime()
        tanggal = tanggal.toString("ddd MMM dd yyyy HH:mm:ss")
        keyword = self.comboBox_keyword.currentText()
        akses = self.comboBox_constraint.currentText()

        data = {"grup":self.grup,
                "user":self.user,
                "kodesimpul":self.simpulJaringan,
                "url":self.url,
                "title":title,
                "abstrack":abstrack,
                "layerPath":self.LayerParams,
                "sldPath":self.filesSld['file'].name,
                "sLDqgis":self.SLDqgis,
                "pathMeta":self.pathMeta,
                "MetaRun":self.MetaRun,
                "date":tanggal,
                "keyword":keyword,
                "akses":akses}

        self.worker = Worker(data,sldName)
        self.worker.sldRename.connect(self.sldRename)
        self.worker.moveToThread(self.thread) # move Worker-Class to a thread
        # Connect signals and slots:
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.status.connect(self.reportStatus)
        self.worker.progress.connect(self.reportProgress)

        self.thread.start() # finally start the thread
        self.ReportDlg.show()
        self.ReportDlg.accept.setEnabled(False)
        self.thread.finished.connect(self.reportFinish)

        self.pushButton_logout.setEnabled(False)        
        self.upload.setEnabled(False) # disable the start-upload button while thread is running
        self.thread.finished.connect(lambda: self.pushButton_logout.setEnabled(True))
        self.thread.finished.connect(lambda: self.upload.setEnabled(True))
        self.thread.finished.connect(lambda: self.ReportDlg.accept.setEnabled(True))
        # enable the start-thread button when thread has been finished              

    def sldRename(self,pathSld):
        print("SLD Rename")
        self.ReportDlg.hide()
        self.report(self.label_statusbase,'caution','Nama file SLD sudah ada, silakan rename atau gunakan SLD yang sudah ada')
        self.sldHandler = SLDDialog(self.user,self.grup,self.simpulJaringan,self.url,pathSld)
        self.sldHandler.uploadStyle.connect(self.runUpload)
        self.sldHandler.show()

    def clearStyle(self):
        self.lineEdit_style.setText('')
        self.filename1 = ''
        self.pathSLD = None

    def clearMetadata(self):
        self.lineEdit_metadata.setText('')
        self.filename1 = ''
        self.pathMeta = None

    def checkEPSG(self):
        layerName = self.select_layer.currentText()
        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        lyrCRS = layer.crs().authid()
        print(lyrCRS)
    
    def exportLayer(self):
        layerName = self.select_layer.currentText()
        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        source = layer.source()
  
        source = source.split("|")
  
        tipe = source[0].split(".")[-1]
        if (tipe=="shp"):
            sourceFile = self.replacePath(source[0],".shp")
        elif (tipe=="dbf"):
            sourceFile = self.replacePath(source[0],".dbf")
        elif (tipe=="shx"):
            sourceFile = self.replacePath(source[0],".shx")
        return sourceFile

    def replacePath(self,source,tipeFile):
        print(tipeFile)
        shp = source.replace(tipeFile, ".shp")
        shp = shp.replace("\\", "/")
        prj = source.replace(tipeFile, ".prj")
        prj = prj.replace("\\", "/")
        dbf = source.replace(tipeFile, ".dbf")
        dbf = dbf.replace("\\", "/")
        shx = source.replace(tipeFile, ".shx")
        shx = shx.replace("\\", "/")
        sourceFile = json.loads('{"shp":"%s","prj":"%s","dbf":"%s","shx":"%s"}'%(shp,prj,dbf,shx))
        print(sourceFile)
        return sourceFile
    
    def checkFileExist(self,filePath):
        fileExist = True
        if os.path.isfile(filePath):
            print ("File exist")
            fileExist = True
        else:
            print ("File not exist")
            fileExist = False
        return fileExist

    def exportSld(self):
        layerName = self.select_layer.currentText()
        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        source = layer.source()
        source = source.split("|")[0]
        tipe = source.split(".")[-1]
        if(tipe=="shp"):
            sldPath = source.replace(".shp", ".sld")
        elif(tipe=="shx"):
            sldPath = source.replace(".shx", ".sld")
        elif(tipe=="dbf"):
            sldPath = source.replace(".dbf", ".sld")
        sldPath = sldPath.replace("\\", "/")
        layer.saveSldStyle(sldPath)
        return sldPath
    
    def start_browse_metadata(self):
        filter = "XML files (*.xml)"
        filename1, _ = QFileDialog.getOpenFileName(None, "Import XML", "",filter)
        print(filename1)
        self.lineEdit_metadata.setText(filename1)
        self.pathMeta = filename1
        
    def start_browse_style(self):
        filter = "SLD files (*.sld)"
        filePath, _ = QFileDialog.getOpenFileName(None, "Import SLD", "",filter)
        print(filePath)
        self.lineEdit_style.setText(filePath)
        self.pathSLD = filePath


    # report upload
    def report(self, label, result, message):
        if result is True:
            label.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;") 
        elif result == 'reset':
            label.setStyleSheet("background-color: none; border-radius: 4px;")
        elif result == 'caution':
            label.setStyleSheet("color: white; background-color: #F28F1E; border-radius: 4px;")
        elif result == 'process':
            label.setStyleSheet("color: black; background-color: #92c9e8; border-radius: 4px;")
        else :
            label.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
        label.setText(message)
    
    def reportReset(self):
         self.report(self.label_statusbase, 'reset', '')
    
    def reportProgress(self, val):
        self.ReportDlg.progressBar.setValue(val/4*100)
    
    def reportStatus(self, status):
        type = status["type"]
        result = status["result"]
        message = status["msg"]
        if type == 'SLD':
            self.ReportDlg.report(self.ReportDlg.label_statusSLD, result, message)
        elif type == 'layer':
            self.ReportDlg.report(self.ReportDlg.label_statusLayer, result, message)
        elif type == 'publish':
            self.ReportDlg.report(self.ReportDlg.label_statusPublish, result, message)
        elif type == 'metadata':
            self.ReportDlg.report(self.ReportDlg.label_statusMetadata, result, message)
        elif type == 'general':
            self.ReportDlg.report(self.ReportDlg.label_statusgeneral, result, message)
            self.report(self.label_statusbase, result, message)

    def reportFinish(self):
        self.report(self.label_statusbase, 'reset', 'Proses Selesai')
        #self.reportStatus('general',True,'Proses Selesai')
    

