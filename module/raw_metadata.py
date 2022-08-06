import os
import json
from pickle import FALSE
import requests
from datetime import datetime
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.PyQt.QtWidgets import QTableWidgetItem
from .utils import readSetting
#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/raw_metadata.ui'))

class RawMetadata(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self,identifer,workspace, parent=iface.mainWindow()):
        super(RawMetadata, self).__init__(parent)
        self.setupUi(self)
        self._rows = []
        self.keyword =  readSetting("keyword")
        for x in self.keyword:
            self.cmb_keyword.addItem(x['keyword'])
        self.identifer = identifer
        self.workspace = workspace

    def setup_workspace(self):

        self.url = readSetting("url")

        if self.url is None:
            return

        try:
            params = {"identifier":self.identifer}
            response = requests.get(self.url+'/api/meta/view_json',params=params)
            metaView = json.loads(response.content)
        except Exception as err:
            self.close()
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Gagal mendapatkan informasi metadata. Silahkan periksa koneksi internet anda",
            )
            return

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

        self.open()



        


   
  
