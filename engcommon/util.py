#!/usr/bin/env python3

"""
This module contains general utility functions.
"""

import collections
import datetime
import errno
import glob
import io
import json
import logging
import logging.config
import numpy
import pymysql
import os.path
import re
import os
import packaging.version
import pkg_resources
import pprint
import random
import shlex
import shutil
import socket
import subprocess
import time
import urllib.request
import urllib.parse
import urllib.error

from . import hardware
from . import error
from .constants import _const as CONSTANTS

logger = logging.getLogger(__name__)


def get_versions(tool_list):
    """Get tools with their versions.

    Args:
        tool_list (list): Tools of which to get versions.

    Returns:
        versions (dict): keys are tool name, values are version string.
    """
    # Shell command to get the version number for each tool
    pkgs = {i.key: i.version for i in pkg_resources.working_set}
    versions = {}
    for tool in tool_list:
        if tool in pkgs.keys():
            versions[tool] = pkgs[tool]
    return versions


def get_third_party_list():
    """Get third party packages to use for version map.

    Get a list of packages whose version number we'll want.

    Args:
        None

    Returns:
        third_party (list): List of packages.
    """
    third_party = ["engcommon"]
    return third_party
