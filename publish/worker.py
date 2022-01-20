from qgis.PyQt import QtCore
from requests import HTTPError

from .geoserver import Geoserver

class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(Exception)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


class CheckConnectionWorker(QtCore.QRunnable):
    def __init__(self, url, user, password):
        super().__init__()
        self._password = password
        self._url = url
        self._user = user
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            g = Geoserver(url=self._url, username=self._user, password=self._password)
            g.check_connection()
        except HTTPError as err:
            self.signals.result.emit('Server Error {}'.format(err.response.status_code))
        except Exception as err:
            self.signals.result.emit('Error  {}'.format(err))
        else:
            self.signals.result.emit(None)  # Return the result of the processing
        finally:
            self.signals.finished.emit()