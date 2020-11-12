#!/usr/bin/env python3

"""
This module contains utility functions specific for gathering information
about hardware or performing tasks on hardware, firmware, DMI, devices, etc.
"""

import collections
import logging
import os
import re

from . import util
from .constants import _const as CONSTANTS

logger = logging.getLogger(__name__)


def get_cpuinfo():
    """Get /proc/cpuinfo.

    Get a list of "processors" from /proc/cpuinfo. Each item contians
    a dict of key/value pairs of the processor info.

    Ex:
    cpuinfo[0]["vendor_id"] is the "vendor_id" of processor "0".

    Args:
        None

    Returns:
        cpuinfo (list): cpuinfo.
    """
    cpuinfo = []
    cmd = "{0}".format(CONSTANTS().CMD_CPUINFO)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for stanza in stdout.split('\n\n'):
        if stanza:
            entry = {}
            for line in stanza.splitlines():
                if line:
                    k = (line.split(":")[0]).strip()
                    v = (line.split(":")[1]).strip()
                    entry[k] = v
            cpuinfo.insert(int(entry['processor']), entry)
    util.check_null(cpuinfo)
    return cpuinfo


def get_cpu_vendor():
    """Get vendor string of either "Intel" or "AMD".

    Args:
        None

    Returns:
        vendor (str): vendor.
    """
    vendor = ""
    cpuinfo = get_cpuinfo()
    vendor_id = cpuinfo[0]["vendor_id"]
    if "GenuineIntel" in vendor_id:
        vendor = "intel"
    elif "AuthenticAMD" in vendor_id:
        vendor = "amd"
    else:
        pass

    util.check_null(vendor)
    return vendor


def get_arch():
    """Get hardware architecture.

    Args:
        none

    Returns:
        arch (str): architecture.
    """
    cmd = "{0} -i".format(CONSTANTS().CMD_UNAME)
    dict_ = util.get_shell_cmd(cmd)
    arch = dict_["stdout"].strip()
    return arch


def get_cpu_extensions_with_prefix(prefix):
    """Get CPU extensions that start with "prefix".

    Args:
        prefix (str): extension prefix.

    Returns:
        extensions (list): extensions
    """
    extensions = []
    cpuinfo = get_cpuinfo()
    flags = cpuinfo[0]["flags"].split()
    for flag in flags:
        if flag.startswith(prefix):
            extensions.append(flag)
    return extensions


def get_cpu_core_count_cpuinfo():
    """Get total non-virtualised cpu cores using cpuinfo.

    Args:
        None

    Returns:
        count (int): core count.
    """
    count = 0
    cpuinfo = get_cpuinfo()

    # First check if processor has the "cpu cores" parameter
    count = (
        (proc["physical id"], int(proc["cpu cores"]))
        for proc in cpuinfo if "cpu cores" in list(proc.keys())
    )
    count = list(count)
    count = set(count)
    count = dict(count)
    count = sum(count.values())

    # If no "cpu cores" parameter, do it the old-fashioned way
    if count == 0:
        count = ((proc["physical id"], proc["core id"]) for proc in cpuinfo)
        count = list(count)
        count = set(count)
        count = len(count)

    util.check_null(count)
    return count


def get_cpu_core_count_lscpu():
    """Get total non-virtualised cpu cores using lscpu.

    Args:
        None

    Returns:
        count (int): core count.
    """
    cmd = "{0}".format(CONSTANTS().CMD_LSCPU)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    lscpu = {}
    for line in stdout.splitlines():
        if line:
            k = (line.split(":")[0]).strip()
            v = (line.split(":")[1]).strip()
            lscpu[k] = v
    core_count = int(lscpu["Socket(s)"]) * int(lscpu["Core(s) per socket"])
    return core_count


def get_cpu_core_count():
    """Get total non-virtualised cpu cores."""
    return get_cpu_core_count_lscpu()


def get_meminfo():
    """Get /proc/meminfo.

    Get a dict of memory info from /proc/meminfo with key/value pairs.
    Ex:
        meminfo['MemTotal'] is the total memory.

    Args:
        None

    Returns:
        meminfo (dict): meminfo.

    Raises:
        ValueError: Error converting memory value string to int.
    """
    meminfo = {}
    cmd = "{0}".format(CONSTANTS().CMD_MEMINFO)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for line in stdout.splitlines():
        if line:
            k = (line.split(":")[0]).strip()
            v = (line.split(":")[1]).strip(' kB')
            try:
                v = int(v)
            except ValueError:
                logger.critical("Integer Conversion Error")
                logger.debug(util.get_debug(v))
                raise
            meminfo[k] = v
    util.check_null(meminfo)
    return meminfo


def clear_sel():
    """Clear SEL."""
    cmd = "{0} sel clear".format(CONSTANTS().CMD_IPMITOOL)
    util.call_shell_cmd(cmd)
    return None
