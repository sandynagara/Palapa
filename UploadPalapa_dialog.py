import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile

from .SLDHandler import SLDDialog

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UploadPalapa_dialog.ui'))

class PalapaDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(PalapaDialog, self).__init__(parent)
        self.setupUi(self)
        self.sld = SLDDialog(parent)
        self.sld.testing.connect(self.tes)
        #Tab1
        self.QPushButton_test_connection.clicked.connect(self.runConnectionTest)
        self.lineEdit_username.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_password.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_url.textChanged.connect(self.connectionValuesChanged)
        #Tab2
        self.upload.setEnabled(False)
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
        
    def tes(self,text):
        print("tes",text)
    # Connection Test Tab1 
    def connectionValuesChanged(self):
        self.label_status.setText('')
        self.label_status.setStyleSheet("")       

    def runConnectionTest(self):
        # Clean label
        self.connectionValuesChanged()

        # login
        url_login=self.lineEdit_url.text()
        user=self.lineEdit_username.text()
        password=self.lineEdit_password.text()

        login_payload = {"username": user, "password": password}
        login_json = json.dumps(login_payload)
        login_api = '/api/login'
        url = url_login+login_api

        try:
            response_API = requests.post(url, data = login_json)
            responseApiJson = json.loads(response_API.text)
            print(response_API.text)
            if response_API.status_code == 200:
                status = responseApiJson['MSG']
                if status == 'Valid Info':             
                    if(responseApiJson['Result']):
                        self.label_status.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;")
                        self.label_status.setText('Terhubung')
                        self.label_status2.setText('')
                        self.grup = responseApiJson['grup']
                        self.user = responseApiJson['user']
                        self.url = url_login
                        responseSimpul = requests.get(self.url+'/api/sisteminfo')
                        responseSimpul = json.loads(responseSimpul.text)
                        self.simpulJaringan = responseSimpul['kodesimpul'].split(",")[0]
                        self.upload.setEnabled(True)
                    print(responseApiJson)
                else:
                    self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
                    self.label_status.setText(status)
                    self.disableUpload()
            else:
                self.label_status.setText('Cek URL atau koneksi internet Anda')
                self.disableUpload()             
        except Exception as err:
            print(err)
            self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
            self.label_status.setText('Cek URL atau koneksi internet Anda')
            self.disableUpload()

    def disableUpload(self):
        self.label_status2.setText('Hubungkan terlebih dahulu')
        self.upload.setEnabled(False) 


    #Upload Tab2
    def uploadFile(self,sld=None):
        self.reportReset()
        if((self.radioButton_StyleBrowse.isChecked() and self.pathSLD == '') or (self.radioButton_StyleBrowse.isChecked() and self.pathSLD == None)):
            self.report(self.label_statusSLD, 'caution', 'Masukkan SLD atau gunakan SLD bawaan')
            print('masukkan SLD atau gunakan sld bawaan')
        else:
            layerPath = self.exportLayer()
            if self.checkFileExist(layerPath['shp']) and self.checkFileExist(layerPath['dbf']) and self.checkFileExist(layerPath['shx']) and self.checkFileExist(layerPath['prj']) :
                print("file Lengkap")
                if (sld==None):
                    self.uploadStyle()
                zipShp = ZipFile(f"{layerPath['shp'].split('.')[0]}"+'.zip', 'w')

                # # Add multiple files to the zip
                # print(layerPath['shp'].split('.')[0].split('/')[-1])
                # zipShp.write(f"{layerPath['shp']}",os.path.basename(layerPath['shp']).replace(" ","_"))
                # zipShp.write(f"{layerPath['dbf']}",os.path.basename(layerPath['dbf']).replace(" ","_"))
                # zipShp.write(f"{layerPath['shx']}",os.path.basename(layerPath['shx']).replace(" ","_"))
                # zipShp.write(f"{layerPath['prj']}",os.path.basename(layerPath['prj']).replace(" ","_"))
                # # close the Zip File
                # zipShp.close()
                
                # files = {'file': open(f"{layerPath['shp'].split('.')[0]}"+'.zip','rb')}
                # print(files)
                
                # urlUpload = self.url+"/api/upload"
                # responseAPIZip = requests.post(urlUpload,files=files,params=params)
                # dataPublish = json.loads(responseAPIZip.text)
                # print(dataPublish,"publish")
                # self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])
                # self.linkStyleShp(dataPublish['LID'],dataPublish['ID'])
                # if(dataPublish['RTN'] == self.select_layer.currentText()+'.zip'):
                #     self.report(self.label_statusLayer, True, 'Layer Berhasil diunggah! : '+dataPublish['MSG']+' ('+dataPublish['RTN']+')')
                # else:
                #     self.report(self.label_statusLayer, False, 'Layer Gagal diunggah! : '+dataPublish['MSG'])            
                
                # #metadata
                # if (self.pathMeta is not None and self.pathMeta != ''):
                #     print('upload meta jalan',self.pathMeta)         
                #     self.uploadMetadata(dataPublish['LID'])
                
                # if (self.radioButton_StyleQgis.isChecked()):
                #     filesSld['file'].close()
                #     os.remove(sldPath)
                # files['file'].close() 
                # os.remove(layerPath['shp'].split('.')[0]+'.zip')
            else :
                print("file Tidak Lengkap")

    def uploadStyle(self):
        if(self.radioButton_StyleQgis.isChecked()):
            self.pathSLD = self.exportSld()
        elif(self.radioButton_StyleBrowse.isChecked() and (self.pathSLD != '' or self.pathSLD != None)):    
            self.pathSLD = self.pathSLD
        filesSld = {'file': open(self.pathSLD,'rb')}
        params = {"USER":self.user,"GRUP":self.grup,"KODESIMPUL":self.simpulJaringan}
        urlSld = self.url+"/api/styles/add"
        responseAPISld = requests.post(urlSld,files=filesSld,params=params)
        print(responseAPISld.text)
        responseAPISldJSON = json.loads(responseAPISld.text)
        if(responseAPISldJSON['MSG'] == 'Upload Success!'):
            self.report(self.label_statusSLD, True, 'SLD Berhasil diunggah! ('+ responseAPISldJSON['RTN']+')')
        else:
            self.sld.panggil()
            print(self.sld.SldName(self.pathSLD,self.user,self.grup,self.simpulJaringan,self.url))

            self.report(self.label_statusSLD, False, 'SLD Gagal diunggah! : '+responseAPISldJSON['MSG'] +' ('+ responseAPISldJSON['RTN']+')')    

    def renameSld(self):
        print(self.sld.SldName(self.pathSLD,self.user,self.grup,self.simpulJaringan,self.url))

    def clearStyle(self):
        self.lineEdit_style.setText('')
        self.filename1 = ''
        self.pathSLD = None

    def clearMetadata(self):
        self.lineEdit_metadata.setText('')
        self.filename1 = ''
        self.pathMeta = None

    def publish(self,kodeEpsg,Lid,Tipe,id):
        url = self.url + "/api/publish"
        dataPublish = {"pubdata":{"LID": Lid, "TIPE": Tipe,"ID":id,"ABS":"","SEPSG":kodeEpsg,"USER":self.user,"GRUP":self.grup}}
        dataPublish = json.dumps(dataPublish)
        respond = requests.post(url,data=f"dataPublish={dataPublish}")
        print(respond.text)
        respondJSON = json.loads(respond.text)
        if(respondJSON['RTN']):
            self.report(self.label_statusPublish, True, 'Layer Berhasil dipublikasikan! : '+respondJSON['MSG'])
        else:
            self.report(self.label_statusPublish, False, 'Layer Gagal dipublikasikan! : '+respondJSON['MSG'])
      
    def exportLayer(self):
        layerName = self.select_layer.currentText()
        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        source = layer.source()
  
        source = source.split("|")
        EPSGLayer = layer.crs().authid()
  
        tipe = source[0].split(".")[-1]
        if (tipe=="shp"):
            sourceFile = self.replacePath(source[0],".shp")
        elif (tipe=="dbf"):
            sourceFile = self.replacePath(source[0],".dbf")
        elif (tipe=="shx"):
            sourceFile = self.replacePath(source[0],".shx")
        return sourceFile

    def linkStyleShp(self,Lid,style):
        url = self.url + "/api/layers/modify"
        dataPublish = {"pubdata":{"id": Lid,"aktif":False, "tipe": "VECTOR","abstract":"","nativename":f"{self.grup}:{Lid}","style":style,"title":style}}
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
        if(responseAPIMetaJSON['RTN']):
            self.report(self.label_statusMetadata, True, 'Metadata berhasil diunggah!')
        else:
            self.report(self.label_statusMetadata, False, 'Metadata Gagal diunggah! : '+responseAPIMetaJSON['MSG'])

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
    
    def reportReset(self):
        self.report(self.label_statusSLD, 'reset', '')
        self.report(self.label_statusLayer, 'reset', '')
        self.report(self.label_statusMetadata, 'reset', '')

