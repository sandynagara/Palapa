import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile
import codecs

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog
from .login import LoginDialog
from .SLDHandler import SLDDialog
from .worker import Worker

from PyQt5.QtCore import QThread, pyqtSignal

#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UploadPalapa_main.ui'))

class UploadDialog(QtWidgets.QDialog, FORM_CLASS):
  
    def __init__(self, parent=None):
        """Constructor."""
        super(UploadDialog, self).__init__(parent)
        self.setupUi(self)
        self.login = LoginDialog()
     
        # self.login.UserSignal.connect(self.UserParam)
        self.upload.setEnabled(True)
        self.upload.clicked.connect(self.uploadFile)
        self.browse_metadata.clicked.connect(self.start_browse_metadata)
        self.browse_style.clicked.connect(self.start_browse_style)
        self.url = None
        self.simpulJaringan=None
        self.grup = None
        self.user=None
        self.pathMeta = None
        self.pathSLD = None
        self.lineEdit_metadata.setReadOnly(True)
        self.lineEdit_style.setReadOnly(True)
        self.radioButton_StyleBrowse.toggled.connect(self.browse_style.setEnabled)
        self.radioButton_StyleBrowse.toggled.connect(self.lineEdit_style.setEnabled)
        self.pushButton_clearStyle.clicked.connect(self.clearStyle)
        self.pushButton_clearMetadata.clicked.connect(self.clearMetadata)
        self.select_layer.currentTextChanged.connect(self.changeTitle)
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
        self.label_userdesc.setText(f"Anda masuk sebagai {self.user} pada {self.url}")
        self.comboBox_constraint.setCurrentIndex(0)
        self.comboBox_keyword.setCurrentIndex(0)
        print(signalpayload)
    
    def logout(self):
        self.close()

    #Upload Tab2

    def checking(self):
        if((self.radioButton_StyleBrowse.isChecked() and self.pathSLD == '') or (self.radioButton_StyleBrowse.isChecked() and self.pathSLD == None)):
            # self.report(self.label_statusbase, 'caution', 'Masukkan SLD atau gunakan SLD bawaan')
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
                self.runUpload()
            else :
                print("file Tidak Lengkap")

    def runUpload(self):
        self.thread = QThread()
        self.worker = Worker(self.UserParams, self.LayerParams, self.filesSld, self.SLDqgis, self.pathMeta, self.MetaRun)
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
        self.progressBar.setValue(0)
        self.thread.finished.connect(self.reportFinish)
        self.upload.setEnabled(False) # disable the start-upload button while thread is running
        self.thread.finished.connect(lambda: self.upload.setEnabled(True)) # enable the start-thread button when thread has been finished              

    def uploadFile(self,sldName=False):
        # self.reportReset()
        if((self.radioButton_StyleBrowse.isChecked() and self.pathSLD == '') or (self.radioButton_StyleBrowse.isChecked() and self.pathSLD == None)):
            # self.report(self.label_statusSLD, 'caution', 'Masukkan SLD atau gunakan SLD bawaan')
            print('masukkan SLD atau gunakan sld bawaan')
        else:
            layerPath = self.exportLayer()
            title = self.lineEdit_layertitle.text()
            abstrack = self.textEdit_layerabstract.toPlainText() 
            params = {"USER":self.user,"GRUP":self.grup,"KODESIMPUL":self.simpulJaringan}
            if self.checkFileExist(layerPath['shp']) and self.checkFileExist(layerPath['dbf']) and self.checkFileExist(layerPath['shx']) and self.checkFileExist(layerPath['prj']) :
                print("file Lengkap")
                if(sldName==False):
                    if(self.radioButton_StyleQgis.isChecked()):
                        sldPath = self.exportSld()
                    elif(self.radioButton_StyleBrowse.isChecked() and (self.pathSLD != '' or self.pathSLD != None)):    
                        sldPath = self.pathSLD
                    filesSld = {'file': open(sldPath,'rb')}
                    urlSld = self.url+"/api/styles/add"
                    responseAPISld = requests.post(urlSld,files=filesSld,params=params)
                    print(filesSld)
                    responseAPISldJSON = json.loads(responseAPISld.text)
                    if(responseAPISldJSON['MSG'] == 'Upload Success!'):
                        # self.report(self.label_statusSLD, True, 'SLD Berhasil diunggah! ('+ responseAPISldJSON['RTN']+')')
                        dataPublish = self.uploadShp(layerPath,params)
                        self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])

                        if (self.radioButton_StyleQgis.isChecked()):
                            filesSld['file'].close()
                            os.remove(sldPath)

                        if (self.pathMeta is not None and self.pathMeta != ''):
                            print('upload meta jalan',self.pathMeta)         
                            self.uploadMetadata(dataPublish['LID'])
                        else:
                            self.minMeta(dataPublish['LID'],title,abstrack)

                        self.linkStyleShp(dataPublish['LID'],dataPublish['ID'],title,abstrack)
                        
                    else:
                        filesSld['file'].close()
                        self.sldHandler = SLDDialog(self.user,self.grup,self.simpulJaringan,self.url,sldPath)
                        self.sldHandler.uploadStyle.connect(self.uploadFile)
                        self.sldHandler.show()
                        # self.report(self.label_statusSLD, False, 'SLD Gagal diunggah! : '+responseAPISldJSON['MSG'] +' ('+ responseAPISldJSON['RTN']+')')
                else:
                    dataPublish = self.uploadShp(layerPath,params)
                    self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'],abstrack)
                    if (self.pathMeta is not None and self.pathMeta != ''):
                        print('upload meta jalan',self.pathMeta)         
                        self.uploadMetadata(dataPublish['LID'])
                    else:
                        self.minMeta(dataPublish['LID'],title,abstrack)
                    self.linkStyleShp(dataPublish['LID'],sldName['nama'],title,abstrack)
            
                # if(dataPublish['RTN'] == self.select_layer.currentText()+'.zip'):
                #     self.report(self.label_statusLayer, True, 'Layer Berhasil diunggah! : '+dataPublish['MSG']+' ('+dataPublish['RTN']+')')
                # else:
                #     self.report(self.label_statusLayer, False, 'Layer Gagal diunggah! : '+dataPublish['MSG'])            
                
                #metadata
            else :
                print("file Tidak Lengkap")

    def minMeta(self,id,title,abstrack):
        tanggal = self.mDateTimeEdit.dateTime()
        tanggal = tanggal.toString("ddd MMM dd yyyy HH:mm:ss")
        data = {"pubdata":{"WORKSPACE":self.grup,
                "KEYWORD":self.comboBox_keyword.currentText(),
                "AKSES":self.comboBox_constraint.currentText(),
                "SELECTEDSIMPUL":self.simpulJaringan,
                "TITLE":title,
                "ID":id,
                "ABSTRACT":abstrack,
                "tanggal":tanggal}}
        data = json.dumps(data)
        print(data)
        urlMinMeta = self.url+'/api/minmetadata'
        responseAPIMeta = requests.post(urlMinMeta,data=f"dataPublish={data}")
        print(responseAPIMeta.text)

    def uploadShp(self,layerPath,params):
        zipShp = ZipFile(f"{layerPath['shp'].split('.')[0]}"+'.zip', 'w')
        # Add multiple files to the zip
        print(layerPath['shp'].split('.')[0].split('/')[-1])
        zipShp.write(f"{layerPath['shp']}",os.path.basename(layerPath['shp']).replace(" ","_"))
        zipShp.write(f"{layerPath['dbf']}",os.path.basename(layerPath['dbf']).replace(" ","_"))
        zipShp.write(f"{layerPath['shx']}",os.path.basename(layerPath['shx']).replace(" ","_"))
        zipShp.write(f"{layerPath['prj']}",os.path.basename(layerPath['prj']).replace(" ","_"))
        # close the Zip File
        zipShp.close()
        
        files = {'file': open(f"{layerPath['shp'].split('.')[0]}"+'.zip','rb')}
        
        urlUpload = self.url+"/api/upload"
        responseAPIZip = requests.post(urlUpload,files=files,params=params)
        dataPublish = json.loads(responseAPIZip.text)

        print(dataPublish,"data")

        files['file'].close() 
        os.remove(layerPath['shp'].split('.')[0]+'.zip')

        return dataPublish

    def clearStyle(self):
        self.lineEdit_style.setText('')
        self.filename1 = ''
        self.pathSLD = None

    def clearMetadata(self):
        self.lineEdit_metadata.setText('')
        self.filename1 = ''
        self.pathMeta = None

    def publish(self,kodeEpsg,Lid,Tipe,id,abstack):
        url = self.url + "/api/publish"
        dataPublish = {"pubdata":{"LID": Lid, "TIPE": Tipe,"ID":id,"ABS":abstack,"SEPSG":kodeEpsg,"USER":self.user,"GRUP":self.grup}}
        dataPublish = json.dumps(dataPublish)
        respond = requests.post(url,data=f"dataPublish={dataPublish}")
        print(respond.text)
        respondJSON = json.loads(respond.text)

        print(respondJSON,"publish")
        # if(respondJSON['RTN']):
        #     self.report(self.label_statusPublish, True, 'Layer Berhasil dipublikasikan! : '+respondJSON['MSG'])
        # else:
        #     self.report(self.label_statusPublish, False, 'Layer Gagal dipublikasikan! : '+respondJSON['MSG'])
      
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

    def linkStyleShp(self,Lid,style,title,abstarck):
        url = self.url + "/api/layers/modify"
        dataPublish = {"pubdata":{"id": Lid,"aktif":False, "tipe": "VECTOR","abstract":abstarck,"nativename":f"{self.grup}:{Lid}","style":style,"title":title}}
        dataPublish = json.dumps(dataPublish)
        respond = requests.post(url,data=f"dataPublish={dataPublish}")
        print(respond.text)        
   
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

    # upload Metadata
    def uploadMetadata(self, Lid) :
        metadataPath = self.pathMeta
        filesMeta = {'file': open(metadataPath,'rb')}
        params = {"akses":"PUBLIC","identifier":Lid,"KODESIMPUL":self.simpulJaringan}
        urlMeta = self.url+"/api/meta/link"
        responseAPIMeta = requests.post(urlMeta,files=filesMeta,params=params)
        print (responseAPIMeta.text)
        #return responseAPIMeta.text
        responseAPIMetaJSON = json.loads(responseAPIMeta.text)
        # if(responseAPIMetaJSON['RTN']):
        #     self.report(self.label_statusMetadata, True, 'Metadata berhasil diunggah!')
        # else:
        #     self.report(self.label_statusMetadata, False, 'Metadata Gagal diunggah! : '+responseAPIMetaJSON['MSG'])

    # report upload
    def report(self, label, result, message):
        if result is True:
            label.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;") 
        elif result == 'reset':
            label.setStyleSheet("background-color: none; border-radius: 4px;")
        elif result == 'caution':
            label.setStyleSheet("color: white; background-color: #F28F1E; border-radius: 4px;")
        else :
            label.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
        label.setText(message)
    
    # def reportReset(self):
    #     self.report(self.label_statusSLD, 'reset', '')
    #     self.report(self.label_statusLayer, 'reset', '')
    #     self.report(self.label_statusMetadata, 'reset', '')
    #     self.report(self.label_statusPublish, 'reset', '')

