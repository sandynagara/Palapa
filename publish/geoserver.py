import json
import os
from urllib.parse import unquote

from requests import HTTPError


class Geoserver:
    """
    Geoserver REST API
    see: https://docs.geoserver.org/stable/en/user/rest/
    """
    def __init__(self, url, username=None, password=None):
        self._url = url
        self._baseUrl = '{}/geoserver/rest'.format(url)
        self._username = username
        self._password = password
        # self.logger = logging.getLogger(type(self).__name__)
    
    def getServerType(self):
        return "geoserver"
    
    def getUrl(self):
        return self._url

    def getWmsUrl(self, workspace):
        return self._url + '/geoserver/' + workspace + '/wms'

    def setAuthCredentials(self, username, password):
        self._username = username
        self._password = password

    def _request(self, url, data=None, method="get", headers=None, params=None):
        if not headers:
            headers = {"content-type": "application/json"}

        if params:
            keys = list(params.keys())
            for key in keys:
                if params[key] is None:
                    params.pop(key)

        if not params:
            params = None

        if isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = data

        # self.logger.info('{}, url={}'.format(method, url))
        url = unquote(url)
        try:
            response = request(url=url,
                               method=method.upper(),
                               headers=headers,
                               data=json_data,
                               auth=(self._username, self._password),
                               params=params)

            response.raise_for_status()
        except HTTPError as err:
            # self.logger.warning('{} request fail {} as code {}'.format(method, url, err.response.status_code))
            raise err
        except Exception as err:
            # self.logger.error('{} request to {}'.format(method, url))
            raise err

        returned_data = {}
        if 'json' in response.headers.get('Content-Type', []):
            returned_data = response.json()
        return returned_data

    def check_connection(self):
        self._request(self._baseUrl + '/about/version')
