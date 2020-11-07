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


def get_lsmod():
    """Get lsmod.

    Args:
        None

    Returns:
        lsmod (str): lsmod.
    """
    cmd = "{0}".format(CONSTANTS().CMD_LSMOD)
    dict_ = util.get_shell_cmd(cmd)
    lsmod = dict_["stdout"]
    return lsmod


def is_loaded_module(module):
    """Get whether module is loaded.

    Args:
        module (str): module

    Returns:
        loaded (bool): True if module is loaded.
    """
    loaded = False
    lsmod = get_lsmod()
    match = re.findall(module, lsmod, flags = re.IGNORECASE)
    if match:
        loaded = True
    return loaded


def get_lspci():
    """Get lspci.

    Args:
        None

    Returns:
        lspci (str): lspci.
    """
    cmd = "{0}".format(CONSTANTS().CMD_LSPCI)
    dict_ = util.get_shell_cmd(cmd)
    lspci = dict_["stdout"]
    return lspci


def is_gpu(vendor):
    """Get whether vendor GPU is installed.

    Args:
        vendor (str): vendor.

    Returns:
        installed (bool): True if vendor GPU installed.
    """
    installed = False
    lspci = get_lspci()
    regex_vendor = {
        "nvidia": "NVIDIA",
        "amd": "Radeon",
    }
    match = re.findall(regex_vendor[vendor], lspci, flags = re.IGNORECASE)
    if match:
        installed = True
    return installed


def get_gpu_info():
    """Get GPU SMI info.

    Args:
        None

    Returns:
        smi (str): SMI info.
    """
    lspci = get_lspci()
    regex_vendor = {
        "nvidia": "NVIDIA",
        "rocm": "Radeon",
    }
    smi = ""
    for k, v in regex_vendor.items():
        match = re.findall(v, lspci, flags = re.IGNORECASE)
        if match:
            cmd = "{0}-smi".format(k)
            dict_ = util.get_shell_cmd(cmd)
            smi = dict_["stdout"]
            break
    return smi


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


def get_mac_addrs():
    """Get MAC addresses.

    Args:
        None

    Returns:
        macs (dict): MAC addresses keyed by interface name (e.g. "eth0").
    """
    macs = collections.OrderedDict()
    dev_prefixes = [
        "eth",
        "en",
        "ib",
    ]
    cmd = "{0}".format(CONSTANTS().CMD_IPLINK)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for line in stdout.split('\n'):
        if line:
            dev = line.split()[1].split(':')[0]
            re_mac = (
                r"([0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:"
                r"[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+)"
            )
            match = re.search(re_mac, line)
            util.check_null(match)
            addr = match.groups()[0]
            for prefix in dev_prefixes:
                if dev.startswith(prefix):
                    macs.update({dev: addr})
    util.check_null(macs)
    return macs


def get_ip_addrs():
    """Get IP addresses.

    Args:
        None

    Returns:
        ip_addrs (dict): IP addresses keyed by interface name (e.g. "eth0").
    """
    ip_addrs = collections.OrderedDict()
    dev_prefixes = [
        "eth",
        "en",
        "ib",
    ]
    cmd = "{0}".format(CONSTANTS().CMD_IPADDR)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    re_ipaddr = r"([a-z0-9]+\s+inet\s[0-9]+.[0-9]+.[0-9]+.[0-9]+)"
    match = re.findall(re_ipaddr, stdout)
    for line in match:
        dev = line.split()[0]
        addr = line.split()[2]
        for prefix in dev_prefixes:
            if dev.startswith(prefix):
                ip_addrs.update({dev: addr})
    util.check_null(ip_addrs)
    return ip_addrs


def get_disks():
    """Get disks using parted.

    Args:
        None

    Returns:
        disks (dict): Disks keyed by device name with nested keys:
            size (str): Size.
            sector_size (str): Sector size.
            model (str): Model name.
    """
    disks = collections.OrderedDict()
    cmd = "{0} -lm".format(CONSTANTS().CMD_PARTED)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    match = re.findall(r'\n(/dev/[a-z]+[a-zA-Z0-9:_\- ]+);', stdout)
    for line in match:
        i = line.split(':')
        dev_name = i[0]
        disks.update({dev_name: {
            'size': i[1],
            'sector_size': i[4],
            'model': i[6],
        }})
    return disks


def get_disk_in_units(dev, unit):
    """Get disks using parted.

    parted only prints disk size in sectors if invoked by
    individual device.

    Args:
        dev (str): Device name (e.g. "/dev/sda").
        unit (str): Parted unit.

    Returns:
        disks (dict): Disks keyed by device name with nested keys:
            size (str): Size.
            sector_size (str): Sector size.
            model (str): Model name.
    """
    disk = {}
    cmd = "{0} -m {1} unit {2} print".format(
        CONSTANTS().CMD_PARTED,
        dev,
        unit,
    )
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    match_0 = re.search(r'\n(/dev/[a-z]+[a-zA-Z0-9:_\- ]+);', stdout)
    util.check_null(match_0)
    line = match_0.groups()[0]
    i = line.split(':')
    size = i[1]
    regex = r"([0-9.]+)({0})".format(unit)
    match_1 = re.search(regex, size)
    util.check_null(match_1)
    size = match_1.groups()[0]
    disk = {'size': size, 'sector_size': i[4], 'model': i[6]}

    return disk


def get_block_range(dev, percent):
    """Get block range (last sector first) for badblocks.

    Args:
        dev (str): Device name (e.g. "/dev/sda").
        percent (int/str): Percentage of device.

    Return:
        block_range (str): Block range.

    Raises:
        ValueError: Error converting "percent" to int.
    """
    block_range = ""
    start = 4096
    end = 0
    cmd = "parted -m {0} unit s print".format(dev)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    match = re.search(r'\n(/dev/[a-z]+[a-zA-Z0-9:_\- ]+);', stdout)
    util.check_null(match)

    line = match.groups()[0]
    blocks_total = line.split(":")[1]
    if blocks_total.endswith("s"):  # parted unit
        blocks_total = blocks_total[:-1]

    try:
        blocks_total = int(blocks_total)
    except ValueError:
        logger.critical("Integer Conversion Error")
        logger.debug(util.get_debug(blocks_total))
        raise
    else:
        blocks_test = int(blocks_total * (int(percent) / 100.0))
        end = blocks_test + 4096
    if end < blocks_total:
        block_range = "{0} {1}". format(end, start)
    return block_range


def get_root_dev():
    """Get device that contains "/".

    Args:
        None

    Returns:
        root_dev (str): Device with "/".
    """
    root_dev = ""
    cmd = "{0}".format(CONSTANTS().CMD_MOUNTS)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for line in stdout.splitlines():
        if ' / ' in line:
            fields = line.split()
            if fields[0] not in "rootfs":
                root_dev = fields[0]
                break
    util.check_null(root_dev)
    return root_dev


def is_active_LV():
    """Get whether LV is active.

    Args:
        None

    Returns:
        active (bool): True if 'ACTIVE'.
    """
    active = False
    cmd = "{0}".format(CONSTANTS().CMD_LVSCAN)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    if stdout:
        lines = stdout.split("\n")
        regex = r"\s(ACTIVE.*)"
        for line in lines:
            match = re.search(regex, line, re.IGNORECASE)
            if match:
                active = True
    return active


def deactivate_LV():
    """Deactivate any LV."""
    cmd = "{0} -a n".format(CONSTANTS().CMD_LVCHANGE)
    util.call_shell_cmd(cmd)
    return None


def deactivate_VG():
    """Deactivate any VG."""
    cmd = "{0} -a n".format(CONSTANTS().CMD_VGCHANGE)
    util.call_shell_cmd(cmd)
    return None


def is_megaraid():
    """Get whether sytem has MegaRAID controller.

    Args:
        None

    Returns:
        megaraid (bool): True if MegaRAID controller installed.
    """
    megaraid = False
    regex = "MegaRAID"
    lspci = get_lspci()
    match = re.search(regex, lspci)
    if match:
        megaraid = True
    return megaraid


def get_storcli():
    """Get storcli log.

    Args:
        None

    Returns:
        storcli_log (str): storcli log.
    """
    storcli = []
    cmd = "{0} show".format(CONSTANTS().CMD_STORCLI)
    res = util.get_shell_cmd(cmd)["stdout"]
    storcli.append("### {0} ###".format(cmd))
    storcli.append(res)
    regex = r'Number of Controllers = ([0-9]+)'
    match = re.search(regex, res)
    if match:
        cmds = [
            "{0} /call show all".format(CONSTANTS().CMD_STORCLI),
            "{0} /call /eall /sall show all".format(CONSTANTS().CMD_STORCLI),
        ]
        numctrl = int(match.groups()[0])
        if numctrl > 0:
            for cmd in cmds:
                res = util.get_shell_cmd(cmd)["stdout"]
                storcli.append("### {0} ###".format(cmd))
                storcli.append(res)

    storcli_log = "\n".join(storcli)
    return storcli_log


def get_smartctl():
    """Get smartctl log.

    Args:
        None

    Returns:
        smartctl_log (str): smartctl log.
    """
    smartctl_log = ''
    cmd = "{0} --scan".format(CONSTANTS().CMD_SMARTCTL)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    scanlines = stdout.split("\n")
    for line in scanlines:
        if line:
            params = line.split(" #")[0]
            regex = r"(.*) -d (.*)"
            match = re.search(regex, params)
            if match:
                dev = match.groups()[0]
                devtype = match.groups()[1]
                cmd = "{0} -a -d {1} {2}".format(
                    CONSTANTS().CMD_SMARTCTL,
                    devtype,
                    dev,
                )
                dict_ = util.get_shell_cmd(cmd)
                smartctl_log = smartctl_log + '\n\n' + dict_["stdout"]
    return smartctl_log


def get_serial():
    """Get serial number.

    Args:
        None

    Returns:
        serial (str): serial number.
    """
    serial = ''
    cmd = "{0} -s system-serial-number".format(CONSTANTS().CMD_DMIDECODE)
    dict_ = util.get_shell_cmd(cmd)
    serial = dict_["stdout"].strip()
    util.check_null(serial)  # Is there a serial before DMI programming?
    return serial


def get_uuid():
    """Get UUID.

    Args:
        None

    Returns:
        uuid (str): UUID.
    """
    uuid = ''
    arch = get_arch()
    if arch not in ["ppc64le"]:
        cmd = '{0}'.format(CONSTANTS().CMD_DMIDECODE)
        dict_ = util.get_shell_cmd(cmd)
        stdout = dict_["stdout"]
        match = re.search('UUID: (.*)', stdout)
        if match:
            uuid = match.group(1)
        util.check_null(uuid)
    return uuid


def get_dmidecode():
    """Get dmidecode.

    Get DMI info keyed by record name (e.g.  'BIOS Information',
    'System Information', 'Chassis Information').

    Args:
        None

    Returns:
        dmi (dict): DMI info.
    """
    dmi = {}
    cmd = '{0}'.format(CONSTANTS().CMD_DMIDECODE)
    dict_ = util.get_shell_cmd(cmd)
    stdout = dict_["stdout"]
    for stanza in stdout.split('\n\n'):
        if stanza.startswith("Handle"):
            stanza_lines = stanza.splitlines()
            record_name = stanza_lines[1]
            if record_name not in list(dmi.keys()):
                dmi[record_name] = []
            dmi[record_name].append(stanza)
    util.check_null(dmi)
    return dmi


def get_flashupdt_i():
    """Get "flashupdt -i" for Intel baseboards.

    Args:
        None

    Returns:
        flashupdt_i (str): flashupdt -i logs.
    """
    flashupdt_i = ""
    baseboard_manufacturer = ""
    baseboard_info = get_dmidecode()["Base Board Information"]
    for line in baseboard_info:
        line = line.strip()
        if "Manufacturer:" in line:
            baseboard_manufacturer = line.split(':')[1]

    util.check_null(baseboard_manufacturer)
    if "intel" in baseboard_manufacturer.lower():
        cmd = '{0} -i'.format(CONSTANTS().CMD_FLASHUPDT)
        dict_ = util.get_shell_cmd(cmd, shell=True)
        flashupdt_i = dict_["stdout"]
    return flashupdt_i


def get_lan_print():
    """Get "ipmitool lan print".

    Args:
        None

    Returns:
        lan_print (str): ipmitool lan print log.
    """
    channels = ["1"]
    # Intel boards have multiple LAN channels
    baseboard_manufacturer = ""
    baseboard_info = get_dmidecode()["Base Board Information"]
    for line in baseboard_info:
        line = line.strip()
        if "Manufacturer:" in line:
            baseboard_manufacturer = line.split(':')[1]
    util.check_null(baseboard_manufacturer)
    if "intel" in baseboard_manufacturer.lower():
        channels.append("3")

    lan_print = ""
    for channel in channels:
        cmd = "ipmitool lan print {0}".format(channel)
        dict_ = util.get_shell_cmd(cmd)
        lan_print = lan_print + "=== channel {0} ===\n{1}\n\n".format(
            channel,
            dict_["stdout"],
        )
    return lan_print


def is_EFI():
    """Get whether system booted as EFI.

    Args:
        None

    Returns:
        efi (bool): True if booted as EFI.
    """
    efi = False
    efi_path = "/sys/firmware/efi"
    if os.path.exists(efi_path):
        efi = True
    return efi


def is_VM():
    """Get whether system is booted as a virtual machine.

    Args:
        None

    Returns:
        vm (bool): True if booted as VM.
    """
    vm = False
    cpuinfo = get_cpuinfo()
    flags = cpuinfo[0]["flags"]
    if 'hypervisor' in flags:
        vm = True
    return vm


def get_sel():
    """Get SEL.

    Args:
        None

    Returns:
        sel (str): SEL.
    """
    sel = ""
    cmd = "{0} sel elist".format(CONSTANTS().CMD_IPMITOOL)
    dict_ = util.get_shell_cmd(cmd)
    sel = dict_["stdout"]
    return sel


def clear_sel():
    """Clear SEL."""
    cmd = "{0} sel clear".format(CONSTANTS().CMD_IPMITOOL)
    util.call_shell_cmd(cmd)
    return None


def gen_over_2TB_disk():
    """Generate disks larger than 2 TB.

    Generator yielding booleans whether disks are larger than 2 TB.
    This is useful for determining if a "biosboot" partition is needed
    for legacy systems.

    Args:
        None

    Yields:
        res (generator): disks larger than 2 TB.
    """
    # Use parted units for later eval()
    kB = 1024
    MB = 1024 * kB
    GB = 1024 * MB
    TB = 1024 * GB
    for disk in list(get_disks().values()):
        re_size = r"^([0-9]+)([a-zA-Z]+)"
        match = re.match(re_size, disk["size"])
        num = match.groups()[0]
        units = match.groups()[1]  # parted units like above
        res = True if (int(num) * eval(units) > 2 * TB) else False
        yield res
