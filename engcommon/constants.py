#!/usr/bin/env python3

"""
This module defines constants for frequently used commands for institutional
standardisation across packages.
"""


def constant(f):
    def fset(self, value):
        raise TypeError

    def fget(self):
        return f()
    return property(fget, fset)


class _const(object):

    # === START XHPL CONFIG===

    @constant
    def XHPL_MEM_PCT():
        "Percentage of memory to use for XHPL"
        return 80  # percentage (int)

    @constant
    def XHPL_TIMEOUT():
        "Timeout for XHPL test before killed"
        return 24  # hours (int/float)

    # === END XHPL CONFIG ===
    # === START HARDWARE COMMANDS ===

    @constant
    def CMD_CPUINFO():
        return "cat /proc/cpuinfo"

    @constant
    def CMD_DMIDECODE():
        return "dmidecode"

    @constant
    def CMD_IPMITOOL():
        return "ipmitool"

    @constant
    def CMD_LSCPU():
        return "lscpu"

    @constant
    def CMD_MEMINFO():
        return "cat /proc/meminfo"

    @constant
    def CMD_NPROC():
        return "nproc"

    @constant
    def CMD_UNAME():
        return "uname"

    @constant
    def IGNORE_RETURNCODE():
        return {
            "smartctl": 4,
        }

    # === END HARDWARE COMMANDS ===
