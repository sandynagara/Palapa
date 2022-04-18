import os
import json
import requests
from pickle import FALSE
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.PyQt.QtWidgets import QFileDialog
from .utils import readSetting
from datetime import datetime
#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/unggah_berkas_metadata.ui'))

class UnggahBerkas(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self,identifier,akses,workspace, parent=iface.mainWindow()):
        super(UnggahBerkas, self).__init__(parent)
        self.setupUi(self)

        self.identifer = identifier
        self.akses = akses
        self.url = readSetting("url")

        self.keyword =  readSetting("keyword")
        for x in self.keyword:
            self.cmb_keyword.addItem(x['keyword'])
        self.workspace = workspace

        self.setup_workspace()
        self.pushButton_save.clicked.connect(self.submit_edit)
        self.pushButton_close.clicked.connect(self.closeTab)

        self.browse_metadata.clicked.connect(self.start_browse_metadata)
        self.btn_update.clicked.connect(self.upload)
        self.btn_tutup.clicked.connect(self.closeTab)
        self.pushButton_save.clicked.connect(self.submit_edit)
        self.pushButton_close.clicked.connect(self.closeTab)

    def closeTab(self):
        self.close()

    def start_browse_metadata(self):
        filter = "XML files (*.xml)"
        filename1, _ = QFileDialog.getOpenFileName(None, "Import XML", "",filter)
        self.lineEdit_metadata.setText(filename1)
        self.pathMeta = filename1

    def setup_workspace(self):
        if self.url is None:
            return
            
        params = {"identifier":self.identifer}
        response = requests.get(self.url+'/api/meta/view_json',params=params)
        metaView = json.loads(response.content)

        try:
            self.tanggalku = metaView["gmd:MD_Metadata"]["gmd:dateStamp"]["gco:DateTime"]
        except:
            self.tanggalku = datetime()

        try:
            self.abstract = metaView["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:abstract"]["gco:CharacterString"]
        except:
            self.abstract = ""

        try:
            self.keyword_item = metaView["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:descriptiveKeywords"]["gmd:MD_Keywords"]["gmd:keyword"]["gco:CharacterString"]
        except:
            self.keyword_item = "Vegetasi"

        try:
            self.datausernote = metaView["gmd:MD_Metadata"]["gmd:metadataConstraints"]["gmd:MD_SecurityConstraints"]["gmd:userNote"]["gco:CharacterString"]
        except:
            self.datausernote = "PUBLIC"

        try:
            self.individualName = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:individualName"]["gco:CharacterString"]
        except:
            self.individualName = ""

        try:
            self.organisationName = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:organisationName"]["gco:CharacterString"]
        except:
            self.organisationName = ""

        try:
            self.positionName = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:positionName"]["gco:CharacterString"]
        except:
            self.positionName = ""

        try:
            self.phone = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:voice"]["gco:CharacterString"]
        except:
            self.phone = ""

        try:
            self.facsimile = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:facsimile"]["gco:CharacterString"]
        except:
            self.facsimile = ""

        try:
            self.deliveryPoint = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:deliveryPoint"]["gco:CharacterString"]
        except:
            self.deliveryPoint = ""

        try:
            self.city = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:city"]["gco:CharacterString"]
        except:
            self.city = ""

        try:
            self.postalCode = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:postalCode"]["gco:CharacterString"]
        except:
            self.postalCode = ""

        try:
            self.country = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:country"]["gco:CharacterString"]
        except:
            self.country = ""

        try:
            self.electronicMailAddress = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:electronicMailAddress"]["gco:CharacterString"]
        except:
            self.electronicMailAddress = ""

        try:
            self.linkage = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:onlineResource"]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"]
        except:
            self.linkage = ""

        try:
            self.hoursOfService = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:hoursOfService"]["gco:CharacterString"]
        except:
            self.hoursOfService = ""

        try:
            self.contactInstructions = metaView["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:contactInstructions"]["gco:CharacterString"]
        except:
            self.contactInstructions = ""

    
        # Identification Info
        try:
            self.title_identification = metaView["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:citation"]["gmd:CI_Citation"]["gmd:title"]["gco:CharacterString"]
        except:
            self.title_identification = ""
        
        try:
            self.Distributor_individualName = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:individualName"]["gco:CharacterString"]
        except:
            self.Distributor_individualName = ""
        
        try:
            self.Distributor_organisationName = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:organisationName"]["gco:CharacterString"]
        except:
            self.Distributor_organisationName = ""

        try:
            self.Distributor_positionName = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:positionName"]["gco:CharacterString"]
        except:
            self.Distributor_positionName = ""

        try:
            self.Distributor_phone = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:voice"]["gco:CharacterString"]
        except:
            self.Distributor_phone = ""

        try:
            self.Distributor_facsimile = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:facsimile"]["gco:CharacterString"]
        except:
            self.Distributor_facsimile = ""

        try:
            self.Distributor_deliveryPoint = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:deliveryPoint"]["gco:CharacterString"]
        except:
            self.Distributor_deliveryPoint = ""
        
        try:
            self.Distributor_city = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:city"]["gco:CharacterString"]
        except:
            self.Distributor_city = ""

        try:
            self.Distributor_postalCode = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:postalCode"]["gco:CharacterString"]
        except:
            self.Distributor_postalCode = ""

        try:
            self.Distributor_country = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:country"]["gco:CharacterString"]
        except:
            self.Distributor_country = ""

        try:
            self.Distributor_electronicMailAddress = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:electronicMailAddress"]["gco:CharacterString"]
        except:
            self.Distributor_electronicMailAddress = ""

        try:
            self.dataSetURI = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:onlineResource"]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"]
        except:
            self.dataSetURI = ""

        try:
            self.Distributor_hoursOfService = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:hoursOfService"]["gco:CharacterString"]
        except:
            self.Distributor_hoursOfService = ""

        try:
            self.Distributor_contactInstructions = metaView["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:contactInstructions"]["gco:CharacterString"]
        except:
            self.Distributor_contactInstructions = ""

        #Informasi Metadata
        indexKeyword = self.cmb_keyword.findText(self.keyword_item)
        self.cmb_keyword.setCurrentIndex(indexKeyword)

        indexConstraint = self.cmb_constraint.findText(self.datausernote)
        self.cmb_constraint.setCurrentIndex(indexConstraint)
        
        self.input_abstrack.setText(self.abstract)
        self.tanggal.setDateTime(datetime.fromisoformat(self.tanggalku))

        #Contact User
        self.input_city_name.setText(self.city)
        self.input_contact_name.setText(self.contactInstructions)
        self.input_country_name.setText(self.country)
        self.input_deliver_name.setText(self.deliveryPoint)
        self.input_email_name.setText(self.electronicMailAddress)
        self.input_fax_name.setText(self.facsimile)
        self.input_house_name.setText(self.hoursOfService)
        self.input_individual_name.setText(self.individualName)
        self.input_linkage_name.setText(self.linkage)
        self.input_organisation_name.setText(self.organisationName)
        self.input_phone_name.setText(self.phone)
        self.input_position_name.setText(self.positionName)
        self.input_postal_name.setText(self.postalCode)

        #Distribution User
        self.input_title_identification.setText(self.title_identification)
        self.input_name_distributor.setText(self.Distributor_individualName)
        self.input_organisation_distributor.setText(self.Distributor_organisationName)
        self.input_position_distributor.setText(self.Distributor_positionName)
        self.input_phone_distributor.setText(self.Distributor_phone)
        self.input_fax_distributor.setText(self.Distributor_facsimile)
        self.input_delivery_distributor.setText(self.Distributor_deliveryPoint)
        self.input_email_distributor.setText(self.Distributor_electronicMailAddress)
        self.input_country_distributor.setText(self.Distributor_country)
        self.input_linkage_distributor.setText(self.dataSetURI)
        self.input_house_distributor.setText(self.Distributor_hoursOfService)
        self.input_contact_distributor.setText(self.Distributor_contactInstructions)
        self.input_city_distributor.setText(self.Distributor_city)
        self.input_postal_distributor.setText(self.Distributor_postalCode)

    #Mengedit metadata
    def submit_edit(self):
        #Mengambil data dari line edit
        abstrack = self.input_abstrack.toPlainText() 
        tanggal = self.tanggal.dateTime()
        tanggal = tanggal.toString("ddd MMM dd yyyy HH:mm:ss")
        keyword = self.cmb_keyword.currentText()
        akses = self.cmb_constraint.currentText()

        input_city_name = self.input_city_name.text()
        input_contact_name = self.input_contact_name.text()
        input_country_name = self.input_country_name.text()
        input_deliver_name = self.input_deliver_name.text()
        input_email_name = self.input_email_name.text()
        input_fax_name = self.input_fax_name.text()
        input_house_name = self.input_house_name.text()
        input_individual_name = self.input_individual_name.text()
        input_linkage_name = self.input_linkage_name.text()
        input_organisation_name = self.input_organisation_name.text()
        input_phone_name = self.input_phone_name.text()
        input_position_name = self.input_position_name.text()
        input_postal_name = self.input_postal_name.text()

        input_title_identification = self.input_title_identification.text()
        input_name_distributor = self.input_name_distributor.text()
        input_organisation_distributor = self.input_organisation_distributor.text()
        input_position_distributor = self.input_position_distributor.text()
        input_phone_distributor = self.input_phone_distributor.text()
        input_fax_distributor = self.input_fax_distributor.text()
        input_delivery_distributor = self.input_delivery_distributor.text()
        input_email_distributor = self.input_email_distributor.text()
        input_country_distributor = self.input_country_distributor.text()
        input_linkage_distributor = self.input_linkage_distributor.text()
        input_house_distributor = self.input_house_distributor.text()
        input_contact_distributor = self.input_contact_distributor.text()
        input_city_distributor = self.input_city_distributor.text()
        input_postal_distributor = self.input_postal_distributor.text()

        #Mengedit upload metadata
        urlUpload = self.url+"/api/lengkapmetadata"
        data = {"pubdata":
            {
            "tanggal": tanggal, 
            "WORKSPACE": self.workspace,
            "ABSTRACT":abstrack,
            "KEYWORD":keyword,
            "AKSES":akses,
            "ID":self.identifer,
            "individualName":input_individual_name,
            "organisationName":input_organisation_name,
            "positionName":input_position_name,
            "phone":input_phone_name,
            "facsimile":input_fax_name,
            "deliveryPoint":input_deliver_name,
            "city":input_city_name,
            "postalCode":input_postal_name,
            "country":input_country_name,
            "electronicMailAddress":input_email_name,
            "linkage":input_linkage_name,
            "hoursOfService":input_house_name,
            "contactInstructions":input_contact_name,
            "title_identification":input_title_identification,
            "Distributor_individualName":input_name_distributor,
            "Distributor_organisationName":input_organisation_distributor,
            "Distributor_positionName":input_position_distributor,
            "Distributor_phone":input_phone_distributor,
            "Distributor_facsimile":input_fax_distributor,
            "Distributor_deliveryPoint":input_delivery_distributor,
            "Distributor_city":input_city_distributor,
            "Distributor_postalCode":input_postal_distributor,
            "Distributor_country":input_country_distributor,
            "Distributor_electronicMailAddress":input_email_distributor,
            "dataSetURI":input_linkage_distributor,
            "Distributor_hoursOfService":input_house_distributor,
            "Distributor_contactInstructions":input_contact_distributor,
            
            }
        }
        data = json.dumps(data)
        response = requests.post(urlUpload,data=f"dataPublish={data}")
        dataPublish = json.loads(response.content)
        if(dataPublish["MSG"] == "Metadata Berhasil disimpan!"):
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Metadata Berhasil disimpan",
            )
            self.close()
        else:
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Metadata gagal disimpan",
            )
    
    #Mengupload Metadata
    def upload(self):
        try:
            filesMeta = {'file': open(self.pathMeta,'rb')}
            params = {"akses":self.akses,"identifier":self.identifier}
            urlMeta = self.url+"/api/meta/link"
            response = requests.post(urlMeta,files=filesMeta,params=params)
            upload= json.loads(response.content)
            print(upload)
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                upload["MSG"],
            )
        except:
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Metadata gagal di update",
            )
