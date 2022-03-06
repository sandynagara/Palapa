from qgis.core import (
    QgsMessageLog,
    QgsSettings,
    Qgis,
)
settings = QgsSettings()

def logMessage(message, level=Qgis.Info):
    """
    Logger untuk debugging
    """
    QgsMessageLog.logMessage(message, "GeoKKP-GIS", level=level)

def readSetting(key, default=None):
    """
    Read value from QGIS Settings
    """
    logMessage("Mengambil data " + str(key) + " dari memory proyek QGIS")
    try:
        return settings.value("geokkp/" + str(key), default)
    except Exception:
        logMessage("gagal memuat data")
    settings.sync()

def storeSetting(key, value):
    """
    Store value to QGIS Settings
    """
    settings.setValue("geokkp/" + str(key), value)
    logMessage("Menyimpan data " + str(key) + " pada memory proyek QGIS")
    settings.sync()