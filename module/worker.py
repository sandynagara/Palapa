import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile
import logging
from pathlib import Path

from qgis.core import QgsProject

from PyQt5.QtCore import QThread, pyqtSignal

logging.basicConfig(format="%(message)s", level=logging.INFO)

class Worker(QThread):

    progress = pyqtSignal(float)
    status = pyqtSignal(object)
    finished = pyqtSignal()
    sldRename = pyqtSignal(object)

    def __init__(self, parameter ,sldName=False):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False # initialize the stop variable

        self.sldName = sldName
        self.parameter = parameter

    def run(self):
  
            self.progress.emit(0)
            report = self.reportload('general', 'process', 'Mulai mengunggah . . .')
            print(report)
            self.status.emit(report)
            try :
                params = {"USER":self.parameter['user'],"GRUP":self.parameter['grup'],"KODESIMPUL":self.parameter['kodesimpul']}
                if(self.sldName==False):
                    #### UPLOAD DENGAN SLD QGIS / CUSTOM ###
                    self.progress.emit(0.5)
                    report = self.reportload('SLD', 'process', 'Mengunggah SLD . . .')
                    self.status.emit(report)

                    urlSld = self.parameter['url']+"/api/styles/add"
                    filesSld = {'file': open(self.parameter['sldPath'],'rb')}
                    print(filesSld['file'], "(nama file sld)")

                    ### upload SLD
                    responseAPISld = requests.post(urlSld,files=filesSld,params=params)
 
                    responseAPISldJSON = json.loads(responseAPISld.text)
                    print(responseAPISldJSON,"SLD")
                    self.progress.emit(1)
                    if(responseAPISldJSON['MSG'] == 'Upload Success!'):
                        # Report upload SLD sukses
                        report = self.reportload('SLD',  True, 'SLD Berhasil diunggah! Menggunakan style:('+ responseAPISldJSON['RTN']+')')
                        self.status.emit(report)
                        ### upload layer
                        dataPublish = self.uploadShp(self.parameter['layerPath'],params)
                        ### publish layer
                        self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])
                        self.linkStyleShp(dataPublish['LID'],Path(responseAPISldJSON['RTN']).stem)
                        print(Path(responseAPISldJSON['RTN']).stem)
                        ### upload metadata
                        if (self.parameter['pathMeta'] is not None and self.parameter['pathMeta'] != ''):     
                            self.uploadMetadata(dataPublish['LID'])
                        else:
                            self.minMeta(dataPublish['LID'])
                        if (self.parameter['sLDqgis']):
                            filesSld['file'].close()
                            print('hapus sld')
                            os.remove(filesSld['file'].name)

                        report = self.reportload('general', True, 'Proses unggah selesai!')
                        self.status.emit(report)
                        self.finished.emit()
                        
                    else:
                        # report upload sld gagal / sudah ada 
                        filesSld['file'].close()
                        self.progress.emit(0)
                        self.finished.emit()
                        report = self.reportload('SLD', False, 'SLD Gagal diunggah! : '+responseAPISldJSON['MSG'] +' ('+ responseAPISldJSON['RTN']+')')
                        self.status.emit(report)
                        if responseAPISldJSON['MSG'] == 'Error, Style dengan nama yang sama sudah ada!':
                            self.sldRename.emit(self.parameter['sldPath'])
                
                else:
                    #### UPLOAD TANPA SLD / NAMA SLD BARU ###
                    self.progress.emit(1)
                    if (self.sldName["new"]):
                        report = self.reportload('SLD', True, f'SLD berhasil diunggah! Menggunakan style: ({self.sldName["nama"]})')
                        self.status.emit(report)                        
                    else:
                        report = self.reportload('SLD', 'caution', f'SLD tidak diunggah! Menggunakan style: ({self.sldName["nama"]})')
                        self.status.emit(report)

                    ### upload layer
                    dataPublish = self.uploadShp(self.parameter['layerPath'],params)

                    ### publish layer
                    self.publish(dataPublish['SEPSG'],dataPublish['LID'],dataPublish['TIPE'],dataPublish['ID'])
                    
                    self.linkStyleShp(dataPublish['LID'],self.sldName["nama"])
                    ### upload metadata
                    if (self.parameter["metadataLengkap"] is not None):
                        self.uploadMetadataLengkap(dataPublish['LID'])
                    elif (self.parameter['pathMeta'] is not None and self.parameter['pathMeta'] != ''):     
                        self.uploadMetadata(dataPublish['LID'])
                    else:
                        self.minMeta(dataPublish['LID'])

                    report = self.reportload('general', True, 'Proses unggah selesai!')
                    self.status.emit(report)                    
                    self.finished.emit()
                
            except Exception as err:
                print('ERROR DAB',err)
                self.finished.emit()
                report = self.reportload('general', False, f'ERROR : {err}')
                self.status.emit(report)       

    def reportload(self,type,result,msg):
        report = {"type":type, "result":result, "msg":msg}
        return report         
                
    def uploadShp(self,layerPath,params):
        self.progress.emit(1.5)
        report = self.reportload('layer', 'process', 'Mengunggah layer . . .')
        self.status.emit(report)        

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

        # report upload layer
        self.progress.emit(2)
        if(dataPublish['RTN'] == f"{layerPath['shp'].split('.')[0].split('/')[-1]}"+'.zip'):
            report = self.reportload('layer', True, 'Layer Berhasil diunggah! : '+dataPublish['MSG']+' ('+dataPublish['RTN']+')')
            self.status.emit(report)
        else:
            report = self.reportload('layer', False, 'Layer Gagal diunggah! : '+dataPublish['MSG'])   
            self.status.emit(report)

        return dataPublish

    def publish(self,kodeEpsg,Lid,Tipe,id):
        self.progress.emit(2.5)
        report = self.reportload('publish', 'process', 'Publish layer . . .')
        self.status.emit(report)

        url = self.parameter['url'] + "/api/publish"
        dataPublish = {"pubdata":{"LID": Lid, "TIPE": Tipe,"ID":id,"ABS":self.parameter['abstrack'],"SEPSG":kodeEpsg,"USER":self.parameter['user'],"GRUP":self.parameter['grup']}}
        dataPublish = json.dumps(dataPublish)
        respond = requests.post(url,data=f"dataPublish={dataPublish}")
        print(respond.text,"publish")
        respondJSON = json.loads(respond.text)
        self.progress.emit(3)

        # report publish layer
        self.progress.emit(3)
        if(respondJSON['RTN']):
            report = self.reportload('publish', True, f"Layer Berhasil dipublikasikan! : {respondJSON['MSG']}")
        else:
            report = self.reportload('publish', False, 'Layer Gagal dipublikasikan! : '+respondJSON['MSG'])
        self.status.emit(report)

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
        print(f"me-link-kan layer dengan style '{style}'")
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

    # upload Metadata minimal
    def minMeta(self,id):
        self.progress.emit(3.5)
        report = self.reportload('metadata', 'process', 'Mengunggah metadata . . .')
        self.status.emit(report)

        data = {"pubdata":{"WORKSPACE":self.parameter['grup'],
                "KEYWORD":self.parameter['keyword'],
                "AKSES":self.parameter['akses'],
                "SELECTEDSIMPUL":self.parameter['kodesimpul'],
                "TITLE":self.parameter['title'],
                "ID":id,
                "ABSTRACT":self.parameter['abstrack'],
                "tanggal":self.parameter['date']}}
        data = json.dumps(data)
        urlMinMeta = self.parameter['url']+'/api/minmetadata'
        responseAPIMeta = requests.post(urlMinMeta,data=f"dataPublish={data}")
        print(responseAPIMeta.text,"MinMeta")
        responseAPIMetaJSON = json.loads(responseAPIMeta.text)

        self.progress.emit(4)
        if(responseAPIMetaJSON['MSG'] == "Metadata minimal disimpan!"):
            report = self.reportload('metadata', True, 'Metadata berhasil disimpan!')
        else:
            report = self.reportload('metadata', False, 'Metadata Gagal diunggah! : '+responseAPIMetaJSON['MSG'])
        self.status.emit(report)

    # upload Metadata File
    def uploadMetadata(self, Lid) :
        self.progress.emit(3.5)
        report = self.reportload('metadata', 'process', 'Mengunggah file metadata . . .')
        self.status.emit(report)

        metadataPath = self.parameter['pathMeta']
        filesMeta = {'file': open(metadataPath,'rb')}
        params = {"akses":self.parameter['akses'],"identifier":Lid,"KODESIMPUL":self.parameter['kodesimpul']}
        urlMeta = self.parameter['url']+"/api/meta/link"
        responseAPIMeta = requests.post(urlMeta,files=filesMeta,params=params)
        print(responseAPIMeta.text)
        #return responseAPIMeta.text
        responseAPIMetaJSON = json.loads(responseAPIMeta.text)

        self.progress.emit(4)
        if(responseAPIMetaJSON['RTN']):
            report = self.reportload('metadata', True, 'Metadata berhasil diunggah!')
        else:
            report = self.reportload('metadata', False, 'Metadata Gagal diunggah! : '+responseAPIMetaJSON['MSG'])
        self.status.emit(report)

    def uploadMetadataLengkap(self,Lid):
        self.progress.emit(3.5)
        report = self.reportload('metadata', 'process', 'Mengunggah file metadata . . .')
        self.status.emit(report)

        # "tanggal": tanggal, 
        # "WORKSPACE": self.workspace,
        # "ABSTRACT":abstrack,
        # "KEYWORD":keyword,
        # "AKSES":akses,
        # "ID":self.identifer,
        urlUpload = self.parameter['url']+"/api/lengkapmetadata"

        metadataLengkap = self.parameter["metadataLengkap"]
        metadataLengkap["tanggal"] = self.parameter['date']
        metadataLengkap["WORKSPACE"] = self.parameter['grup']
        metadataLengkap["ABSTRACT"] = self.parameter['abstrack']
        metadataLengkap["KEYWORD"] = self.parameter['keyword']
        metadataLengkap["AKSES"] = self.parameter['akses']
        metadataLengkap["ID"] = Lid

        data = {"pubdata":metadataLengkap}
        data = json.dumps(data)
        print(data)
        response = requests.post(urlUpload,data=f"dataPublish={data}")
        print(response)
        dataPublish = json.loads(response.content)

        self.progress.emit(4)
        if(dataPublish['MSG'] == "Metadata Berhasil disimpan!"):
            report = self.reportload('metadata', True, 'Metadata berhasil diunggah!')
        else:
            report = self.reportload('metadata', False, 'Metadata Gagal diunggah! : '+dataPublish['MSG'])
        self.status.emit(report)
    
