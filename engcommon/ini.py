#!/usr/bin/env python3

"""
This module is used to parse the ini configuration.

Ex:
    myini = INIConfig()
"""

import configparser
import io
import logging
import os.path
import pkg_resources
import sys
import urllib.request

from engcommon import testvar

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

    def __init__(self):
        self._ini_file = self._get_ini_filepath("builder.ini")
        self._ini = self._get_ini_config(self._ini_file)
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

    def _get_ini_filepath(self, filename):
        """Get the INI file path.

        Search the module directory first, then package directory.

        Args:
            filename (str): File name like "builder.ini"

        Returns:
            filepath (str): Absolute path of INI file.
        """
        filepath = ""
        files = (
            "{0}/{1}".format(
                os.path.dirname(sys.modules[__name__].__file__),
                filename
            ),
            pkg_resources.resource_stream(
                __name__,
                "{0}".format(filename)
            ).name
        )

        for f in files:
            if os.path.exists(f):
                filepath = f
                break

        testvar.check_null(filepath)
        return filepath

    def _get_ini_config(self, ini_file):
        """Get the INI config from URL.

        Args:
            ini_file (str): Resource of INI.

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
            if ini_file.startswith("http"):
                f = urllib.request.urlopen(ini_file)
            else:
                f = open(ini_file, "r")
        except IOError:
            logger.error("INI Open Error")
            logger.debug("resource: {0}".format(ini_file))
            raise
        else:
            ini = f.read()
            config = configparser.RawConfigParser()
            config.read_file(io.StringIO(ini))
            section = "builder"
            dict_ = {
                "apihost": config.get(section, "apihost"),
                "buildhost": config.get(section, "buildhost"),
                "dockerhost": config.get(section, "dockerhost"),
                "jenkinshost": config.get(section, "jenkinshost"),
                "xhplconsole_url": config.get(section, "xhplconsole_url"),
                "kubeconfig": config.get(section, "kubeconfig")
            }
        return dict_
