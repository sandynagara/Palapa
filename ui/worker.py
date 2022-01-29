import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile
import logging

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

    def __init__(self, UserParam, Layer, SLD, SLDqgis, Metadata, MetaRun):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False # initialize the stop variable

        self.url = UserParam['url']
        self.simpulJaringan = UserParam['kodesimpul']
        self.grup = UserParam['grup']
        self.user = UserParam['user']
        self.pathMeta = Metadata
        self.MetaRun = MetaRun
        self.filesSld = SLD
        self.layerPath = Layer
        self.SLDqgis = SLDqgis

    def run(self):
            self.status.emit('mulai')
            self.progress.emit(0)
            try :
                # Upload SLD
                params = {"USER":self.user,"GRUP":self.grup,"KODESIMPUL":self.simpulJaringan}
                urlSld = self.url+"/api/styles/add"
                responseAPISld = requests.post(urlSld,files=self.filesSld,params=params)
                print(responseAPISld.text)
                print(self.filesSld)
                responseAPISldJSON = json.loads(responseAPISld.text)
                self.progress.emit(1)
                self.status.emit('SLD done')
                # if(responseAPISldJSON['MSG'] == 'Upload Success!'):
                #     self.status.emit('SLD done')
                # #    self.bar.pushMessage("SLD Berhasil diunggah!", responseAPISldJSON['RTN'], level=Qgis.Success, duration=0)
                # #    self.report(self.label_statusSLD, True, 'SLD Berhasil diunggah! ('+ responseAPISldJSON['RTN']+')')
                # else:
                #     self.bar.pushMessage("SLD Gagal diunggah!", f"{responseAPISldJSON['MSG']} ({responseAPISldJSON['RTN']})", level=Qgis.Critical, duration=0)
                # #    self.report(self.label_statusSLD, False, 'SLD Gagal diunggah! : '+responseAPISldJSON['MSG'] +' ('+ responseAPISldJSON['RTN']+')')
                
                # Upload Layer
                layerPath = self.layerPath
                # buat zip
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
                print(files)
                
                urlUpload = self.url+"/api/upload"
                responseAPIZip = requests.post(urlUpload,files=files,params=params)
                dataPublish = json.loads(responseAPIZip.text)
                print(dataPublish,"publish")
                self.progress.emit(2)
                self.status.emit('Layer done')

                # publish
                self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])
                self.linkStyleShp(dataPublish['LID'],dataPublish['ID'])

                # if(dataPublish['RTN'] == self.select_layer.currentText()+'.zip'):
                #     self.report(self.label_statusLayer, True, 'Layer Berhasil diunggah! : '+dataPublish['MSG']+' ('+dataPublish['RTN']+')')
                # else:
                #     self.report(self.label_statusLayer, False, 'Layer Gagal diunggah! : '+dataPublish['MSG'])            
                
                # metadata
                if (self.MetaRun):
                    print('uploadmetajalan',self.pathMeta)         
                    self.uploadMetadata(dataPublish['LID'])
                    
                self.progress.emit(4)
                self.status.emit('Meta done')
                
                if (self.SLDqgis is True):
                    self.filesSld['file'].close()
                    os.remove(self.filesSld['file'].name)
                files['file'].close() 
                os.remove(layerPath['shp'].split('.')[0]+'.zip')
                self.finished.emit()
                self.status.emit('aman')
            except Exception as err:
                print('ERROR DAB',err)
                self.finished.emit()
                self.status.emit('error')


    def publish(self,kodeEpsg,Lid,Tipe,id):
        url = self.url + "/api/publish"
        dataPublish = {"pubdata":{"LID": Lid, "TIPE": Tipe,"ID":id,"ABS":"","SEPSG":kodeEpsg,"USER":self.user,"GRUP":self.grup}}
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
   
    # upload Metadata
    def uploadMetadata(self, Lid) :
        metadataPath = self.pathMeta
        filesMeta = {'file': open(metadataPath,'rb')}
        params = {"akses":"PUBLIC","identifier":Lid,"KODESIMPUL":self.simpulJaringan}
        urlMeta = self.url+"/api/meta/link"
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