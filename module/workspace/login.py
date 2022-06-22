import os
import json
from pickle import FALSE
import requests
from zipfile import ZipFile
import codecs

from ..utils import storeSetting
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from PyQt5.QtCore import pyqtSignal

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui/UploadPalapa_login.ui'))

# List daftar geoportal
daftar_geoportal = [{"url":"http://geoportal.jogjakota.go.id","nama":"Kota Yogyakarta"},
                    {"url":"http://geoportal.papua.go.id","nama":"Papua"},
                    {"url":"http://papuabarat.ina-sdi.or.id","nama":"Papua Barat"},
                    {"url":"http://bandungkota.ina-sdi.or.id","nama":"Kota Bandung"},
                    {"url":"http://geoportal.jatimprov.go.id","nama":"Jawa Timur"},
                    {"url":"http://geoportal.jatengprov.go.id","nama":"Jawa Tengah"},
                    {"url":"http://surabayakota.ina-sdi.or.id","nama":"Surabaya"},
                    {"url":"http://geoportal.palembang.go.id","nama":"Palembang"},
                    {"url":"http://baliprov.ina-sdi.or.id","nama":"Bali"},
                    {"url":"http://nttprov.ina-sdi.or.id","nama":"Nusa Tenggara Timur"},
                    {"url":"http://malangkab.ina-sdi.or.id","nama":"Malang"},
                    {"url":"http://gresikkab.ina-sdi.or.id","nama":"Gresik"},
                    {"url":"http://madiunkab.ina-sdi.or.id","nama":"Madiun"},
                    {"url":"http://ponorogokab.ina-sdi.or.id","nama":"Ponorogo"},
                    {"url":"http://sidoarjokab.ina-sdi.or.id","nama":"Sidoarjo"},
                    {"url":"http://geoportal.bukittinggikota.go.id","nama":"Bukit Tinggi"},
                    {"url":"http://sulbarprov.ina-sdi.or.id","nama":"Sulawesi Barat"},
                    {"url":"http://pekanbarukota.ina-sdi.or.id","nama":"Pekanbaru"},
                    {"url":"http://sorongkab.ina-sdi.or.id","nama":"Sorong"},
                    {"url":"http://bekasikota.ina-sdi.or.id","nama":"Kota Bekasi"},
                    {"url":"http://geoportal.tulungagung.go.id","nama":"Tulungagung"},
                    {"url":"http://gorontaloprov.ina-sdi.or.id","nama":"Gorontalo"},
                    {"url":"http://geoportal.pesisirselatankab.go.id","nama":"Pesisir Selatan"},
                    {"url":"http://geoportal.bekasikab.go.id","nama":"Bekasi"},
                    {"url":"http://ciamiskab.ina-sdi.or.id","nama":"Ciamis"},
                    {"url":"http://cianjurkab.ina-sdi.or.id","nama":"Cianjur"},
                    {"url":"http://ciamiskab.ina-sdi.or.id","nama":"Ciamis"},
                    {"url":"http://subangkab.ina-sdi.or.id","nama":"Subang"},
                    {"url":"http://sukabumikab.ina-sdi.or.id","nama":"Sukabumi"},
                    {"url":"http://garutkab.ina-sdi.or.id","nama":"Garut"},
                    {"url":"http://indramayukab.ina-sdi.or.id","nama":"Indramayu"},
                    {"url":"http://karawangkab.ina-sdi.or.id","nama":"Karawang"},
                    {"url":"http://kuningankab.ina-sdi.or.id","nama":"Kuningan"},
                    {"url":"http://bangkalankab.ina-sdi.or.id","nama":"Bangkalan"},
                    {"url":"http://blitarkab.ina-sdi.or.id","nama":"Blitar"},
                    {"url":"http://jemberkab.ina-sdi.or.id","nama":"Jember"},
                    {"url":"http://jombangkab.ina-sdi.or.id","nama":"Jombang"},
                    {"url":"http://kedirikab.ina-sdi.or.id","nama":"Kediri"},
                    {"url":"http://sumenepkab.ina-sdi.or.id","nama":"Sumenep"},
                    {"url":"http://trenggalekkab.ina-sdi.or.id","nama":"Trenggalek"},
                    {"url":"http://tubankab.ina-sdi.or.id","nama":"Tuban"},
                    {"url":"http://batukota.ina-sdi.or.id","nama":"Kota Batu"},
                    {"url":"http://blitarkota.ina-sdi.or.id","nama":"Kota Blitar"},
                    {"url":"http://madiunkota.ina-sdi.or.id","nama":"Kota Madiun"},
                    {"url":"http://pasuruankota.ina-sdi.or.id","nama":"Kota Pasuruan"},
                    {"url":"http://jambiprov.ina-sdi.or.id","nama":"Jambi"},
                    {"url":"http://geoportal.riau.go.id","nama":"Riau"},
                    {"url":"http://geoportal.kalteng.go.id","nama":"Kalimantan Tengah"},
                    {"url":"http://geoportal.kaltaraprov.go.id","nama":"Kalimantan Utara"},
                    {"url":"http://kepriprov.ina-sdi.or.id","nama":"Kepulauan Riau"},
                    {"url":"http://bengkuluprov.ina-sdi.or.id","nama":"Bengkulu"},
                    {"url":"http://geoportal.sumutprov.go.id","nama":"Sumatera Utara"},
                    {"url":"http://geoportal.pemkomedan.go.id","nama":"Medan"},
                    {"url":"http://brg.ina-sdi.or.id","nama":"Badan Restorasi Gambut"},
                    {"url":"http://lamongankab.ina-sdi.or.id","nama":"Lamongan"},
                    {"url":"http://nganjukkab.ina-sdi.or.id","nama":"Nganjuk"},
                    {"url":"http://ngawikab.ina-sdi.or.id","nama":"Ngawi"},
                    {"url":"http://pasuruankab.ina-sdi.or.id","nama":"Pasuruan"},
                    {"url":"http://situbondokab.ina-sdi.or.id","nama":"Situbondo"},
                    {"url":"http://kedirikota.ina-sdi.or.id","nama":"Kediri"},
                    {"url":"http://malangkota.ina-sdi.or.id","nama":"Kota Malang"},
                    {"url":"http://probolinggokota.ina-sdi.or.id","nama":"Probolinggo"},
                    {"url":"http://geoportal.bantulkab.go.id","nama":"Bantul"},
                    {"url":"http://geoportal.okutimurkab.go.id","nama":"Oku TImur"},
                    {"url":"http://geoportal.kuduskab.go.id","nama":"Kudus"},
                    {"url":"http://grobogankab.ina-sdi.or.id","nama":"Grobogan"},
                    {"url":"http://takalarkab.ina-sdi.or.id","nama":"Takalar"},
                    {"url":"http://palangkarayakota.ina-sdi.or.id","nama":"Palangkaraya"},
                    {"url":"http://geoportal.bangka.go.id","nama":"Bangka"},
                    {"url":"http://sigikab.ina-sdi.or.id","nama":"Sigi"},
                    {"url":"http://sintangkab.ina-sdi.or.id","nama":"Sintang"},
                    {"url":"http://pontianakkota.ina-sdi.or.id","nama":"Kota Pontianak"},
                    {"url":"http://geoportal.mojokertokota.go.id","nama":"Mojokerto"},
                    {"url":"http://ketapangkab.ina-sdi.or.id","nama":"Ketapang"},
                    {"url":"http://jeparakab.ina-sdi.or.id","nama":"Jepara"},
                    {"url":"http://palukota.ina-sdi.or.id","nama":"Palu"},
                    {"url":"","nama":"Lainnya"}]

class LoginDialog(QtWidgets.QDialog, FORM_CLASS):

    # Daftar signal untuk login umum dan admin
    UserSignal = pyqtSignal(object)
    UmumMasuk = pyqtSignal()
    
    def __init__(self, parent=None):
        """Constructor."""
        super(LoginDialog, self).__init__(parent)
        self.setupUi(self)

        self.setup_workpanel()

    # Setting workpanel
    def setup_workpanel(self):
        self.QPushButton_test_connection.clicked.connect(self.runConnectionTest)
        self.masuk_button.clicked.connect(self.masuk)
        self.lineEdit_username.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_password.textChanged.connect(self.connectionValuesChanged)
        self.lineEdit_url.textChanged.connect(self.connectionValuesChanged)  

        # Memasukkan list geoportal ke dalam cmb QGIS
        for item in daftar_geoportal:
            self.cmb_geoportal.addItem(item["nama"],item["url"])
            self.cmb_geoportal_2.addItem(item["nama"],item["url"])

        self.cmb_geoportal.currentIndexChanged.connect(self.changeGeoportal)
        self.cmb_geoportal_2.currentIndexChanged.connect(self.changeGeoportal2)

        self.lineEdit_url.setText(self.cmb_geoportal.currentData())
        self.lineEdit_url.setEnabled(False)
        self.lineEdit_url_2.setText(self.cmb_geoportal_2.currentData())
        self.lineEdit_url_2.setEnabled(False)

    # Handle perubahan geoportal Admin
    def changeGeoportal(self):
        data = self.cmb_geoportal.currentData()
        self.lineEdit_url.setText(data)
        if(data == ""):
            self.lineEdit_url.setEnabled(True)
        else:
            self.lineEdit_url.setEnabled(False)

    # Handle perubahan geoportal Umum
    def changeGeoportal2(self):
        data = self.cmb_geoportal_2.currentData()
        self.lineEdit_url_2.setText(data)
        if(data == ""):
            self.lineEdit_url_2.setEnabled(True)
        else:
            self.lineEdit_url_2.setEnabled(False)

    # Handle reset error 
    def connectionValuesChanged(self):
        self.label_status.setText('')
        self.label_status.setStyleSheet("") 

    # Handle masuk geoportal untuk umum
    def masuk(self):
        url=self.lineEdit_url_2.text()
        print(url+'/api/sisteminfo')
        try:
            # Check geoportal valid atau tidak
            responseSimpul = requests.get(url+'/api/sisteminfo')
            if(responseSimpul.status_code != 200):
                url = url + ":8000"
                responseSimpul = requests.get(url+'/api/sisteminfo')
            print(responseSimpul)
            responseSimpul = json.loads(responseSimpul.content)
            storeSetting("url",url)
            self.UmumMasuk.emit()
        except Exception as err:
            # Handle geoportal tidak valid
            print(err)
            self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
            self.label_status.setText('Cek URL atau koneksi internet Anda')

    # Handle masuk geoportal untuk admin
    def runConnectionTest(self):
        # Clean label
        self.connectionValuesChanged()

        # login
        url=self.lineEdit_url.text()
        user=self.lineEdit_username.text()
        password=self.lineEdit_password.text()

        login_payload = {"username": user, "password": password}
        login_json = json.dumps(login_payload)

        try:
            responseSimpul = requests.get(url+'/api/sisteminfo')
            if(responseSimpul.status_code != 200):
                url = url + ":8000"
                responseSimpul = requests.get(url+'/api/sisteminfo')
            responseSimpul = json.loads(responseSimpul.content)

            response_API = requests.post(url+"/api/login", data = login_json)
            responseApiJson = json.loads(response_API.text)
            
            print(response_API.text)
            # Handle response 200
            if response_API.status_code == 200:
                status = responseApiJson['MSG']
                if status == 'Valid Info':             
                    if(responseApiJson['Result']):
                        self.label_status.setStyleSheet("color: white; background-color: #4AA252; border-radius: 4px;")
                        self.label_status.setText('Terhubung')
                        self.grup = responseApiJson['grup']
                        self.user = responseApiJson['user']
                        self.kelas = responseApiJson['kelas']
                        
                        self.url = url
                        # Mengambil data terkait geoportal
                        responseSimpul = requests.get(self.url+'/api/sisteminfo')
                        responseSimpul = json.loads(responseSimpul.content)
                        self.simpulJaringan = responseSimpul['kodesimpul'].split(",")[0]
                        
                        storeSetting("system",responseSimpul)
                        storeSetting("url",self.url)
                        storeSetting("user",self.user)
                        storeSetting("kodesimpul",self.simpulJaringan)
                        storeSetting("grup", self.grup)
                        storeSetting("kelas", self.kelas)
                        storeSetting("password", self.lineEdit_password.text())
                        
                        # Mengirim signal yang berisi payload kepada palapa.py
                        signalsend = {"grup": self.grup, "user": self.user, "url": self.url, "kodesimpul": self.simpulJaringan}
                        self.UserSignal.emit(signalsend)
                        #self.close()
                        print(signalsend)

                    print(responseApiJson)
                else:
                    self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
                    self.label_status.setText(status)
            else:
                # Handle geoportal tidak valid
                self.label_status.setText('Cek URL atau koneksi internet Anda')        
        except Exception as err:
            print(err)
            self.label_status.setStyleSheet("color: white; background-color: #C4392A; border-radius: 4px;")
            self.label_status.setText('Cek URL atau koneksi internet Anda')