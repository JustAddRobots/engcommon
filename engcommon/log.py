#!/usr/bin/env python3

"""
This module contains functions for configuring and writing logs for institutional
standardisation.
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


def get_logdir(module_name, **kwargs):
    """Get directory in which to save logs.

    Create unique logdir based on timestamp and module name.

    Default: /tmp/logs/[hostname]/[module_name].[timestamp]
    Ex:      /tmp/logs/ribeye/runxhpl.2020.06.15-134944

    Example of optional **kwargs using 'logid' as suffix:
    /tmp/misc/logs/ribeye/favorable-wire/2020.06.15-134944

    Args:
        module_name (str): Module/package subdir for logs.

    **kwargs:
        prefix (str): Prefix dir.
        suffix (str): Suffix dir.

    Returns:
        logdir (str):
    """
    prefix = kwargs.setdefault("prefix", "/tmp/logs")
    suffix = kwargs.setdefault("suffix", "")
    dt = datetime.datetime.now()
    timestamp = "{0}.{1:02d}.{2:02d}-{3:02d}{4:02d}{5:02d}".format(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second
    )
    hostname = socket.gethostname()
    logdir = "{0}/{1}/{2}/{3}.{4}".format(
        prefix, hostname, suffix, module_name, timestamp,
    )
    return logdir


def get_std_logger_conf():
    """Get standard logger config dict.

    Get config to be used by logging.config.dictConfig().

    Args:
        None

    Returns:
        logger_conf (dict): logger config dict.
    """
    logger_conf = {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            '': {
                'handlers': ['file', 'console', 'buffer', 'debug'],
            },
            'noformat': {
                'handlers': ['noformat'],
                'propagate': False,
            },
        },
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(levelname)s [%(module)s]: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'complex': {
                'format': '%(asctime)s - %(levelname)s %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s,',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'noformat': {
                'format': '',
                'datefmt': '',
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'simple',
            },
            'console': {
                'stream': 'ext://sys.stdout',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'buffer': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'debug': {
                'class': 'logging.FileHandler',
                'formatter': 'simple',
            },
            'noformat': {
                'class': 'logging.FileHandler',
                'formatter': 'noformat',
            },
        },
    }
    return logger_conf


def get_std_logger(module_name, debug, **kwargs):
    """Get Logger objects from custom logger config.

    Args:
        module_name (str): Module name
        debug (bool): Debug mode.

    **kwargs:
        logdir (str): Custom logdir to store log files.

    Returns:
        tuple(
            lgr (logging.Logger): Main logger.
            lgr_nf (logging.Logger): Logger with no formatting.
        )
    """
    # Config logging of command output (file, console, buffer)
    logdir = kwargs.setdefault("logdir", get_logdir(module_name))
    my_pid = os.getpid()
    logfile_cmd = "{0}/{1}.cmd.{2}.log".format(logdir, module_name, my_pid)
    logfile_debug = "{0}/{1}.debug.{2}.log".format(logdir, module_name, my_pid)
    buffer_cmd = io.StringIO()
    logger_dict = get_std_logger_conf()
    logger_dict['handlers']['file']['filename'] = logfile_cmd
    logger_dict['handlers']['buffer']['stream'] = buffer_cmd
    logger_dict['handlers']['debug']['filename'] = logfile_debug
    logger_dict['handlers']['noformat']['filename'] = logfile_debug
    logging.config.dictConfig(logger_dict)
    lgr = logging.getLogger()
    lgr_nf = logging.getLogger('noformat')
    fh = logging.getLogger().handlers[0]  # file handler in logger_conf
    ch = logging.getLogger().handlers[1]  # console
    bh = logging.getLogger().handlers[2]  # buffer
    dh = logging.getLogger().handlers[3]  # debug
    if debug:
        fh.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        bh.setLevel(logging.DEBUG)
        dh.setLevel(logging.DEBUG)
        lgr.setLevel(logging.DEBUG)
        lgr_nf.setLevel(logging.DEBUG)
    else:
        fh.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
        bh.setLevel(logging.INFO)
        dh.setLevel(logging.DEBUG)  # silent "always on" debug file logger
        lgr.setLevel(logging.DEBUG)
        lgr_nf.setLevel(logging.DEBUG)
    return (lgr, lgr_nf)


def get_formatted_logs(dict_):
    """Get command log string from dictionary.

    Convert dictionary of command output to string with headers output.

    Args:
        dict_ (dict): keys are command names, values are command output.

    Result:
        str_ (str): Command output with command headers.
    """
    str_ = ""
    for cmd_name, output in dict_.items():
        str_ = str_ + "### {0} ###\n{1}\n".format(cmd_name, output)
    return str_
