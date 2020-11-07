#!/usr/bin/env python3

"""
This module is used to parse buildmaster's ini configuration.
The server is automatically detected from the DHCP lease, but can be
forced with the optional "server" keyword argument.

    Typical Usage:
    my_ini_bmstagedev = INIConfig(server = "bmstagedev")
    rsync_pw = my_ini_bmstagedev.rsync_password
"""

import configparser
import glob
import io
import logging
import os
import re
import socket
import urllib.request
import urllib.parse
import urllib.error

from . import util
from .constants import _const as CONSTANTS

logger = logging.getLogger(__name__)


class INIConfig:
    """A class for containing buildmaster INI config info.

    Attributes:
        dhcp_server (str): DHCP server.
        load_server (str): OS loading server.
        iso_server (str): ISO repository server.
        rsync_password (str): rsync password.
        uberkonsole (dict): Uberkonsole DB login info.
    """

    def __init__(self, **kwargs):
        """Init INIConfig class.

        Args:
            None

        **kwargs:
            server(str): Server which to get INI config.
        """
        self._server = kwargs.setdefault("server", "")
        self._dhcp_server = self._get_dhcp_server()
        self._ini = self._get_ini_config(CONSTANTS().INI_URL)
        self._load_server = self._ini["load_server"]
        self._iso_server = self._ini["iso_server"]
        self._rsync_password = self._ini["rsync_password"]
        self._uberkonsole = self._ini["db_servers"]["uberkonsole"]

    @property
    def dhcp_server(self):
        """Get DHCP server."""
        return self._dhcp_server

    @property
    def load_server(self):
        """Get OS loading server."""
        return self._load_server

    @property
    def iso_server(self):
        """Get ISO server."""
        return self._iso_server

    @property
    def rsync_password(self):
        """Get rsync password."""
        return self._rsync_password

    @property
    def uberkonsole(self):
        """Get Uberkonsole login info."""
        return self._uberkonsole

    @property
    def oms(self):
        """Get OMS login info."""
        return self._oms

    def _get_dhcp_server(self):
        """Get the DHCP server from DHCP lease or CGI bin socket.

        Args:
            None

        Returns:
            dhcp_server (str): DHCP server.

        Raises:
            IOError: Error opening DHCP lease file.
        """
        dhcp_server = ""
        if self._server:
            dhcp_server = self._server
        elif "REQUEST_METHOD" in os.environ:  # cgi_bin
            dhcp_server = socket.gethostname()
        else:
            dhcp_lease_dirs = CONSTANTS().DHCP_LEASE_DIRS
            wildcards = [
                "dhclient*-eth*.lease*",
                "dhclient*-en*.lease*",
                "dhclient*.lease*",
            ]
            for dirname in dhcp_lease_dirs:
                for wildcard in wildcards:
                    dhcp_lease_wildcard = "{0}/{1}".format(dirname, wildcard)
                    leases = glob.glob(dhcp_lease_wildcard)
                    if leases:
                        first_lease = leases[0]
                        try:
                            with open(first_lease, "r") as f:
                                for line in f:
                                    match = re.search(
                                        r"""server-name.*'([a-zA-Z0-9]+)';""",
                                        line,
                                    )
                                    if match:
                                        dhcp_server = match.group(1)
                        except IOError:
                            logger.error("DHCP Lease Open Error")
                            logger.debug("lease: {0}".format(first_lease))
                            raise
        util.check_null(dhcp_server)
        return dhcp_server

    def _get_ini_config(self, ini_url):
        """Get the INI config from URL.

        Args:
            ini_url (str): URL of INI file.

        Returns:
            dict_ (dict):
                {
                    load_server (str): OS loading server.
                    iso_server (str): ISO repository server.
                    rsync_password (str): rsync password for server.
                    db_servers (dict): DB servers login info.
                }

        Raises:
            IOError: Error opening INI URL.
        """
        try:
            f = urllib.request.urlopen(ini_url)
        except IOError:
            logger.error("URL Open Error")
            logger.debug("url: {0}".format(ini_url))
            raise
        else:
            ini = f.read().decode("utf-8")
            config = configparser.RawConfigParser()
            config.read_file(io.StringIO(ini))
            dict_ = {}
            server = self._dhcp_server
            dict_["load_server"] = config.get(server, "load_server")
            dict_["iso_server"] = config.get(server, "iso_server")
            dict_["rsync_password"] = config.get(server, "rsync_password")
            db_servers = {}
            # Get login info for both Uberkonsole and OMS DBs
            for i in ["uberkonsole", "oms"]:
                login = {}
                for j in [
                    "db_server",
                    "db_name",
                    "db_user",
                    "db_password",
                    "db_port",
                ]:
                    login[j] = config.get(config.get(server, i), j)
                    db_servers[i] = login
            dict_["db_servers"] = db_servers
        return dict_
