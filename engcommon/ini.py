#!/usr/bin/env python3

"""
This module is used to parse JSON-enconded ini configuration.

Ex:
    myini = INIConfig("http://builder.local/config.json")
"""

import json
import logging
import urllib.request

logger = logging.getLogger(__name__)


class INIConfig:
    """A class for containing INI config info.

    Attributes:
        apihost (str): Host running XHPlconsole API.
        buildhost (str): Host for general build info.
        dockerhost (str): Host:Port serving docker registry.
        jenkinshost (str): Host:Port running Jenkins.
        xhplconsole_url (str): URL or XHPLconsole API.
        kubeconfig (str): Kubernetes config on buildhost.
    """

    def __init__(self, ini_url):
        self._ini = self._get_ini_config(ini_url)
        self._apihost = self._ini["apihost"]
        self._buildhost = self._ini["buildhost"]
        self._dockerhost = self._ini["dockerhost"]
        self._jenkinshost = self._ini["jenkinshost"]
        self._xhplconsole_url = self._ini["xhplconsole_url"]
        self._kubeconfig = self._ini["kubeconfig"]

    @property
    def apihost(self):
        return self._apihost

    @property
    def buildhost(self):
        return self._buildhost

    @property
    def dockerhost(self):
        return self._dockerhost

    @property
    def jenkinshost(self):
        return self._jenkinshost

    @property
    def xhplconsole_url(self):
        return self._xhplconsole_url

    @property
    def kubeconfig(self):
        return self._kubeconfig

    def _get_ini_config(self, ini_url):
        """Get the INI config from URL.

        The config must be a JSON-encoded string.

        Args:
            ini_file (str): URL of INI.

        Returns:
            dict_ (dict):
                {
                    apihost (str): Host running XHPlconsole API.
                    buildhost (str): Host for general build info.
                    dockerhost (str): Host:Port serving docker registry.
                    jenkinshost (str): Host:Port running Jenkins.
                    xhplconsole_url (str): URL or XHPLconsole API.
                    kubeconfig (str): Kubernetes config on buildhost.
                }

        Raises:
            IOError: Error opening INI resource.
        """
        try:
            f = urllib.request.urlopen(ini_url)
        except IOError:
            logger.error("URL Open Error")
            logger.debug("resource: {0}".format(ini_url))
            raise
        else:
            ini = f.read().decode("utf-8")
            dict_ = json.loads(ini)
        return dict_
