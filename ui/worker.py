import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile
import logging
from .SLDHandler import SLDDialog

from qgis.PyQt import uic
from qgis.PyQt import QtCore
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject, Qgis
from qgis.PyQt.QtWidgets import QFileDialog


from PyQt5.QtCore import QThread, pyqtSignal

logging.basicConfig(format="%(message)s", level=logging.INFO)

class Worker(QThread):

    progress = pyqtSignal(int)
    status = pyqtSignal(object)
    #error = pyqtSignal(str)
    #killed = pyqtSignal()
    finished = pyqtSignal()
    sldRename = pyqtSignal(object)

    def __init__(self, parameter ,sldName=False):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False # initialize the stop variable

        self.sldName = sldName
        print(sldName)
        self.parameter = parameter
        print(self.parameter,self.parameter['user'])

    def run(self):
            self.status.emit('mulai')
            self.progress.emit(0)
            try :
                # Upload SLD

                params = {"USER":self.parameter['user'],"GRUP":self.parameter['grup'],"KODESIMPUL":self.parameter['kodesimpul']}
                if(self.sldName==False):
                    urlSld = self.parameter['url']+"/api/styles/add"
                    filesSld = {'file': open(self.parameter['sldPath'],'rb')}
                    responseAPISld = requests.post(urlSld,files=filesSld,params=params)
                    print("disini")
                    responseAPISldJSON = json.loads(responseAPISld.text)
                    if(responseAPISldJSON['MSG'] == 'Upload Success!'):
                        # self.report(self.label_statusSLD, True, 'SLD Berhasil diunggah! ('+ responseAPISldJSON['RTN']+')')
                        dataPublish = self.uploadShp(self.parameter['layerPath'],params)
                        self.progress.emit(2)
                        self.status.emit('Layer done')
                        self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])
                   
                        self.linkStyleShp(dataPublish['LID'],dataPublish['ID'])

                        if (self.parameter['pathMeta'] is not None and self.parameter['pathMeta'] != ''):     
                            self.uploadMetadata(dataPublish['LID'])
                        else:
                            self.minMeta(dataPublish['LID'])

                        if (self.parameter['sLDqgis']):
                            filesSld['file'].close()
                            os.remove(filesSld['file'].name)

                        self.progress.emit(4)
                        self.status.emit('Meta done')
                   
                        self.finished.emit()
                        self.status.emit('aman')
                        
                    else:
                        filesSld['file'].close()
                        self.finished.emit()
                        self.status.emit('error')
                        self.sldRename.emit(self.parameter['sldPath'])
                        # self.report(self.label_statusSLD, False, 'SLD Gagal diunggah! : '+responseAPISldJSON['MSG'] +' ('+ responseAPISldJSON['RTN']+')')
                
                else:
                    dataPublish = self.uploadShp(self.parameter['layerPath'],params)
                    self.progress.emit(2)
                    self.status.emit('Layer done')
                    self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])

                    if (self.parameter['pathMeta'] is not None and self.parameter['pathMeta'] != ''):     
                        self.uploadMetadata(dataPublish['LID'])
                    else:
                        self.minMeta(dataPublish['LID'])

                    self.progress.emit(4)
                    self.status.emit('Meta done')
                    self.linkStyleShp(dataPublish['LID'],self.sldName)
                    self.finished.emit()
                    self.status.emit('aman')
                
            except Exception as err:
                print('ERROR DAB',err)
                self.finished.emit()
                self.status.emit('error')
                
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
        
        urlUpload = self.parameter['url']+"/api/upload"
        responseAPIZip = requests.post(urlUpload,files=files,params=params)
        dataPublish = json.loads(responseAPIZip.text)

        print(dataPublish,"data")

        files['file'].close() 
        os.remove(layerPath['shp'].split('.')[0]+'.zip')

        return dataPublish

    def minMeta(self,id):
        data = {"pubdata":{"WORKSPACE":self.parameter['grup'],
                "KEYWORD":self.parameter['keyword'],
                "AKSES":self.parameter['akses'],
                "SELECTEDSIMPUL":self.parameter['kodesimpul'],
                "TITLE":self.parameter['title'],
                "ID":id,
                "ABSTRACT":self.parameter['abstrack'],
                "tanggal":self.parameter['date']}}
        data = json.dumps(data)
        print(data)
        urlMinMeta = self.parameter['url']+'/api/minmetadata'
        responseAPIMeta = requests.post(urlMinMeta,data=f"dataPublish={data}")
        print(responseAPIMeta.text)

    def publish(self,kodeEpsg,Lid,Tipe,id):
        url = self.parameter['url'] + "/api/publish"
        dataPublish = {"pubdata":{"LID": Lid, "TIPE": Tipe,"ID":id,"ABS":self.parameter['abstrack'],"SEPSG":kodeEpsg,"USER":self.parameter['user'],"GRUP":self.parameter['grup']}}
        dataPublish = json.dumps(dataPublish)
        respond = requests.post(url,data=f"dataPublish={dataPublish}")
        print(respond.text)
        respondJSON = json.loads(respond.text)
        self.progress.emit(3)
        self.status.emit('Publish done')
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

    def linkStyleShp(self,Lid,style):
        url = self.parameter['url'] + "/api/layers/modify"
        dataPublish = {"pubdata":{"id": Lid,"aktif":False, "tipe": "VECTOR","abstract":self.parameter['abstrack'],"nativename":f"{self.parameter['grup']}:{Lid}","style":style,"title":self.parameter['title']}}
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

    # upload Metadata
    def uploadMetadata(self, Lid) :
        metadataPath = self.parameter['pathmeta']
        filesMeta = {'file': open(metadataPath,'rb')}
        params = {"akses":self.parameter['akses'],"identifier":Lid,"KODESIMPUL":self.parameter['kodesimpul']}
        urlMeta = self.parameter['url']+"/api/meta/link"
        responseAPIMeta = requests.post(urlMeta,files=filesMeta,params=params)
        print(responseAPIMeta.text)
        #return responseAPIMeta.text
        responseAPIMetaJSON = json.loads(responseAPIMeta.text)
        # self.progress.emit(4)
        # self.status.emit('Meta done')
        # if(responseAPIMetaJSON['RTN']):
        #     self.report(self.label_statusMetadata, True, 'Metadata berhasil diunggah!')
        # else:
        #     self.report(self.label_statusMetadata, False, 'Metadata Gagal diunggah! : '+responseAPIMetaJSON['MSG'])