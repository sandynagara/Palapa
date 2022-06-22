import os
import json
from pickle import FALSE
import requests
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from .utils import readSetting

#from .login import LoginDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/Form_metadata.ui'))

class MetadataForm(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self,title, parent=iface.mainWindow()):
        super(MetadataForm, self).__init__(parent)
        self.setupUi(self)

        self.system = readSetting("system")

        self.pushButton_save.clicked.connect(self.save)
       
        if(self.system["organization"]):
            self.input_name_distributor.setText(self.system["organization"])
            self.input_organisation_distributor.setText(self.system["organization"])
            self.input_position_distributor.setText(self.system["organization"])
            self.input_phone_distributor.setText(self.system["phone"])
            self.input_fax_distributor.setText(self.system["fax"])
            self.input_delivery_distributor.setText(self.system["address"])
            self.input_email_distributor.setText(self.system["email"])
            self.input_country_distributor.setText(self.system["country"])
            self.input_linkage_distributor.setText(self.system["url"])
            self.input_house_distributor.setText(self.system["hoursofservice"])
            self.input_contact_distributor.setText(self.system["contactinstruction"])
            self.input_city_distributor.setText(self.system["city"])
            self.input_postal_distributor.setText(self.system["postalcode"])

        self.input_title_identification.setText(title)

    def getMetadata(self):
        
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

        data =  {
            # "tanggal": tanggal, 
            # "WORKSPACE": self.workspace,
            # "ABSTRACT":abstrack,
            # "KEYWORD":keyword,
            # "AKSES":akses,
            # "ID":self.identifer,
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

        return data

    def save(self):
        self.close()

    def setKeyword(self,keyword):
        self.metadata_constraint.setText(keyword)