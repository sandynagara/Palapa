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

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/informasi_layer.ui'))

class InformasiLayer(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self,identifer,parent=iface.mainWindow()):
        super(InformasiLayer, self).__init__(parent)
        self.setupUi(self)
        self._rows = []
        self.identifer = identifer

    def setup_workspace(self):

        self.url = readSetting("url")

        if self.url is None:
            return
        
        #Mendapatkan metadata dari service CSW
        try:
            response = requests.get(self.url+f'/csw?service=CSW&version=2.0.2&request=GetRecordById&ElementSetName=full&Id={self.identifer}&outputSchema=http://www.isotc211.org/2005/gmd&outputFormat=application/json')
            metaView = json.loads(response.content)
        except Exception as err:
            self.close()
            QtWidgets.QMessageBox.information(
                None,
                "Palapa",
                "Gagal mendapatkan informasi layer. Silahkan periksa koneksi internet anda",
            )
            return

        baseIdentification = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]

        self.input_title_identification.setText(baseIdentification["gmd:citation"]["gmd:CI_Citation"]["gmd:title"]["gco:CharacterString"])
        self.input_Date_identification.setText(baseIdentification["gmd:citation"]["gmd:CI_Citation"]["gmd:date"]["gmd:CI_Date"]["gmd:date"]["gco:DateTime"])
        self.input_Abstract_identification.setText(baseIdentification["gmd:abstract"]["gco:CharacterString"])
        self.input_maintenance_identification.setText(baseIdentification["gmd:resourceMaintenance"]["gmd:MD_MaintenanceInformation"]["gmd:maintenanceAndUpdateFrequency"]["gmd:MD_MaintenanceFrequencyCode"]["#text"])
        self.input_Keywords_identification.setText(baseIdentification["gmd:descriptiveKeywords"]["gmd:MD_Keywords"]["gmd:keyword"]["gco:CharacterString"])
        self.input_Resource_identification.setText(baseIdentification["gmd:resourceConstraints"]["gmd:MD_LegalConstraints"]["gmd:accessConstraints"]["gmd:MD_RestrictionCode"]["#text"])
        self.input_spatial_type_identification.setText(baseIdentification["gmd:spatialRepresentationType"]["gmd:MD_SpatialRepresentationTypeCode"]["#text"])
        self.input_Language_identification.setText(baseIdentification["gmd:language"]["gmd:LanguageCode"]["#text"])
        self.input_character_identification.setText(baseIdentification["gmd:characterSet"]["gmd:MD_CharacterSetCode"]["#text"])
        self.input_topic_identification.setText(baseIdentification["gmd:topicCategory"]["gmd:MD_TopicCategoryCode"])
        self.input_west_identification.setText(baseIdentification["gmd:extent"]["gmd:EX_Extent"]["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]["gmd:westBoundLongitude"]["gco:Decimal"])
        self.input_east_identification.setText(baseIdentification["gmd:extent"]["gmd:EX_Extent"]["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]["gmd:eastBoundLongitude"]["gco:Decimal"])
        self.input_south_identification.setText(baseIdentification["gmd:extent"]["gmd:EX_Extent"]["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]["gmd:southBoundLatitude"]["gco:Decimal"])
        self.input_north_identification.setText(baseIdentification["gmd:extent"]["gmd:EX_Extent"]["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]["gmd:northBoundLatitude"]["gco:Decimal"])
        
        baseSummary = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]

        self.input_file_metadata.setText(baseSummary["gmd:fileIdentifier"]["gco:CharacterString"])
        self.input_language_metadata.setText(baseSummary["gmd:language"]["gmd:LanguageCode"]["#text"])
        self.input_character_metadata.setText(baseSummary["gmd:characterSet"]["gmd:MD_CharacterSetCode"]["#text"])
        self.input_hierarchy_metadata.setText(baseSummary["gmd:hierarchyLevel"]["gmd:MD_ScopeCode"]["#text"])
        self.input_date_metadata.setText(baseSummary["gmd:dateStamp"]["gco:DateTime"])
        self.input_standard_name_metadata.setText(baseSummary["gmd:metadataStandardName"]["gco:CharacterString"])
        self.input_standard_version_metadata.setText(baseSummary["gmd:metadataStandardVersion"]["gco:CharacterString"])
        self.input_dataset_metadata.setText(baseSummary["gmd:dataSetURI"]["gco:CharacterString"])
        self.input_frequency_metadata.setText(baseSummary["gmd:metadataMaintenance"]["gmd:MD_MaintenanceInformation"]["gmd:maintenanceAndUpdateFrequency"]["gmd:MD_MaintenanceFrequencyCode"]["#text"])
        self.input_note_metadata.setText(baseSummary["gmd:metadataMaintenance"]["gmd:MD_MaintenanceInformation"]["gmd:maintenanceNote"]["gco:CharacterString"])
        self.input_constraints_metadata.setText(baseSummary["gmd:metadataConstraints"]["gmd:MD_SecurityConstraints"]["gmd:userNote"]["gco:CharacterString"])
        
        baseSpatialInfo = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]["gmd:spatialRepresentationInfo"]["gmd:MD_VectorSpatialRepresentation"]

        self.input_topologi_spatial.setText(baseSpatialInfo["gmd:topologyLevel"]["gmd:MD_TopologyLevelCode"]["#text"])
        self.input_geometric_spatial.setText(baseSpatialInfo["gmd:geometricObjects"]["gmd:MD_GeometricObjects"]["gmd:geometricObjectType"]["gmd:MD_GeometricObjectTypeCode"]["#text"])
        
        baseReference = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]["gmd:referenceSystemInfo"]["gmd:MD_ReferenceSystem"]["gmd:referenceSystemIdentifier"]["gmd:RS_Identifier"]

        self.input_code_reference.setText(baseReference["gmd:code"]["gco:CharacterString"])
        self.input_version_reference.setText(baseReference["gmd:version"]["gco:CharacterString"])
        self.input_authority_reference.setText(baseReference["gmd:authority"]["gmd:CI_Citation"]["gmd:title"]["gco:CharacterString"])
        self.input_resource_reference.setText(baseReference["gmd:authority"]["gmd:CI_Citation"]["gmd:citedResponsibleParty"]["gmd:CI_ResponsibleParty"]["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:onlineResource"]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])

        baseTransfer = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:transferOptions"]["gmd:MD_DigitalTransferOptions"]["gmd:onLine"]

        self.input_protocol_raw.setText(baseTransfer[0]["gmd:CI_OnlineResource"]["gmd:protocol"]["gco:CharacterString"])
        self.input_url_row.setText(baseTransfer[0]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])
        self.input_protocol_wms.setText(baseTransfer[1]["gmd:CI_OnlineResource"]["gmd:protocol"]["gco:CharacterString"])
        self.input_url_wms.setText(baseTransfer[1]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])
        self.input_protocol_zip.setText(baseTransfer[2]["gmd:CI_OnlineResource"]["gmd:protocol"]["gco:CharacterString"])
        self.input_url_zip.setText(baseTransfer[2]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])
        self.input_protocol_wms_2.setText(baseTransfer[3]["gmd:CI_OnlineResource"]["gmd:protocol"]["gco:CharacterString"])
        self.input_url_wms_2.setText(baseTransfer[3]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])

        baseContact = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]["gmd:contact"]["gmd:CI_ResponsibleParty"]

        self.input_city_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:city"]["gco:CharacterString"])
        self.input_contact_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:contactInstructions"]["gco:CharacterString"])
        self.input_country_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:country"]["gco:CharacterString"])
        self.input_deliver_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:deliveryPoint"]["gco:CharacterString"])
        self.input_email_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:electronicMailAddress"]["gco:CharacterString"])
        self.input_fax_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:facsimile"]["gco:CharacterString"])
        self.input_house_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:hoursOfService"]["gco:CharacterString"])
        self.input_individual_name.setText(baseContact["gmd:individualName"]["gco:CharacterString"])
        self.input_linkage_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:onlineResource"]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])
        self.input_organisation_name.setText(baseContact["gmd:organisationName"]["gco:CharacterString"])
        self.input_phone_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:voice"]["gco:CharacterString"])
        self.input_position_name.setText(baseContact["gmd:positionName"]["gco:CharacterString"])
        self.input_postal_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:postalCode"]["gco:CharacterString"])
        self.input_area_name.setText(baseContact["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:administrativeArea"]["gco:CharacterString"])
        
        baseDistributor = metaView["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:distributor"]["gmd:MD_Distributor"]["gmd:distributorContact"]["gmd:CI_ResponsibleParty"]
        #Distribution User
        self.input_name_distributor.setText(baseDistributor["gmd:individualName"]["gco:CharacterString"])
        self.input_organisation_distributor.setText(baseDistributor["gmd:organisationName"]["gco:CharacterString"])
        self.input_position_distributor.setText(baseDistributor["gmd:positionName"]["gco:CharacterString"])
        self.input_phone_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:voice"]["gco:CharacterString"])
        self.input_fax_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:phone"]["gmd:CI_Telephone"]["gmd:facsimile"]["gco:CharacterString"])
        self.input_delivery_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:deliveryPoint"]["gco:CharacterString"])
        self.input_email_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:electronicMailAddress"]["gco:CharacterString"])
        self.input_country_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:country"]["gco:CharacterString"])
        self.input_linkage_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:onlineResource"]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"])
        self.input_house_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:hoursOfService"]["gco:CharacterString"])
        self.input_contact_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:contactInstructions"]["gco:CharacterString"])
        self.input_city_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:city"]["gco:CharacterString"])
        self.input_postal_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:postalCode"]["gco:CharacterString"])
        self.input_area_distributor.setText(baseDistributor["gmd:contactInfo"]["gmd:CI_Contact"]["gmd:address"]["gmd:CI_Address"]["gmd:administrativeArea"]["gco:CharacterString"])

        self.open()