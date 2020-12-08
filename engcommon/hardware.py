#!/usr/bin/env python3

"""
This module contains functions specific for gathering information
about hardware or performing tasks on hardware, firmware, DMI, devices, etc.
"""

import logging
import re

from . import command
from . import testvar
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
    dict_ = command.get_shell_cmd(cmd)
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
    testvar.check_null(cpuinfo)
    return cpuinfo


def get_cpu_vendor():
    """Get vendor string of either "Intel" or "AMD" CPUs.

    Args:
        None

    Returns:
        vendor (str): vendor in lowercase.
    """
    vendor = ""
    cpuinfo = get_cpuinfo()
    vendor_id = cpuinfo[0]["vendor_id"]
    if "GenuineIntel" in vendor_id:
        vendor = "intel"
    elif "AuthenticAMD" in vendor_id:
        vendor = "amd"
    else:
        pass  # Need ARM platforms for testing

    testvar.check_null(vendor)
    return vendor


def get_arch():
    """Get hardware architecture.

    Args:
        none

    Returns:
        arch (str): architecture.
    """
    cmd = "{0} -i".format(CONSTANTS().CMD_UNAME)
    dict_ = command.get_shell_cmd(cmd)
    arch = dict_["stdout"].strip()
    return arch


def get_cpu_flags_with_prefix(prefix):
    """Get CPU flags that start with "prefix".

    Args:
        prefix (str): flag prefix.

    Returns:
        prefix_flags (list): CPU flags with prefix.
    """
    prefix_flags = []
    cpuinfo = get_cpuinfo()
    flags = cpuinfo[0]["flags"].split()
    for flag in flags:
        if flag.startswith(prefix):
            prefix_flags.append(flag)
    return prefix_flags


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

    testvar.check_null(count)
    return count


def get_cpu_core_count_lscpu():
    """Get total non-virtualised cpu cores using lscpu.

    Args:
        None

    Returns:
        count (int): core count.
    """
    lscpu = get_lscpu()
    core_count = int(lscpu["Socket(s)"]) * int(lscpu["Core(s) per socket"])
    return core_count


def get_cpu_core_count():
    """Get total non-virtualised cpu cores."""
    return get_cpu_core_count_lscpu()


def get_lscpu():
    """Get lscpu info as key/value pairs
    Ex:
        lscpu["Vendor ID"] is the CPU vendor.

    Args:
        None

    Returns:
        lscpu (dict): lscpu information.
    """
    lscpu = {}
    cmd = "{0}".format(CONSTANTS().CMD_LSCPU)
    dict_ = command.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for line in stdout.splitlines():
        if line:
            k = (line.split(":")[0]).strip()
            v = (line.split(":")[1]).strip()
            lscpu[k] = v
    return lscpu


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
    dict_ = command.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for line in stdout.splitlines():
        if line:
            k = (line.split(":")[0]).strip()
            v = (line.split(":")[1]).strip(' kB')
            try:
                v = int(v)
            except ValueError:
                logger.critical("Integer Conversion Error")
                logger.debug(testvar.get_debug(v))
                raise
            meminfo[k] = v
    testvar.check_null(meminfo)
    return meminfo


def get_dmidecode():
    """Get dmidecode.

    Get DMI info in key/value pairs by record name (e.g.  'BIOS Information',
    'System Information', 'Chassis Information').

    NOTE: May require 'sudo'.

    Args:
        None

    Returns:
        dmi (dict): DMI info.
    """
    dmi = {}
    cmd = '{0}'.format(CONSTANTS().CMD_DMIDECODE)
    dict_ = command.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for stanza in stdout.split('\n\n'):
        if stanza.startswith("Handle"):
            stanza_lines = stanza.splitlines()
            record_name = stanza_lines[1]
            if record_name not in list(dmi.keys()):
                dmi[record_name] = []
            dmi[record_name].append(stanza)
    testvar.check_null(dmi)
    return dmi


def get_uuid():
    """Get UUID.

    NOTE: May require 'sudo'.

    Args:
        None

    Returns:
        uuid (str): UUID.
    """
    uuid = ""
    arch = get_arch()
    if arch not in ["ppc64le"]:
        cmd = '{0}'.format(CONSTANTS().CMD_DMIDECODE)
        dict_ = command.get_shell_cmd(cmd)
        stdout = dict_["stdout"]
        match = re.search('UUID: (.*)', stdout)
        if match:
            uuid = match.group(1)
        testvar.check_null(uuid)
    return uuid


def get_serial_num():
    """Get serial number.

    NOTE: May require 'sudo'.

    Args:
        None

    Returns:
        serial (str): serial number.
    """
    serial_num = ""
    cmd = "{0} -s system-serial-number".format(CONSTANTS().CMD_DMIDECODE)
    dict_ = command.get_shell_cmd(cmd)
    serial_num = dict_["stdout"].strip()
    testvar.check_null(serial_num)
    return serial_num
