#!/usr/bin/env python3

def constant(f):
    def fset(self, value):
        raise TypeError

    def fget(self):
        return f()
    return property(fget, fset)


class _const(object):

    # === START INI CONFIG ===

    @constant
    def DHCP_LEASE_DIRS():
        return [
            "/var/lib/dhclient",
            "/var/lib/NetworkManager",
            "/tmp/dhclient",
        ]

    @constant
    def INI_URL():
        return "http://iso.penguincomputing.com/ini/buildmaster.ini"

    # === END INI CONFIG ===
    # === START XHPL CONFIG===

    @constant
    def XHPL_MEM_PCT():
        return 80  # percentage (int)

    @constant
    def XHPL_TIMEOUT():
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
    def CMD_DMSETUP_REMOVEALL():
        return "dmsetup remove_all"

    @constant
    def CMD_FLASHUPDT():
        return "flashupdt"

    @constant
    def CMD_IFCONFIG():
        return "ifconfig"

    @constant
    def CMD_IPADDR():
        return "ip -o address"

    @constant
    def CMD_IPLINK():
        return "ip -o link"

    @constant
    def CMD_IPMITOOL():
        return "ipmitool"

    @constant
    def CMD_LSCPU():
        return "lscpu"

    @constant
    def CMD_LSPCI():
        return "lspci"

    @constant
    def CMD_LSMOD():
        return "lsmod"

    @constant
    def CMD_LVCHANGE():
        return "lvchange"

    @constant
    def CMD_LVSCAN():
        return "lvscan"

    @constant
    def CMD_MEMINFO():
        return "cat /proc/meminfo"

    @constant
    def CMD_MOUNTS():
        return "cat /proc/mounts"

    @constant
    def CMD_NPROC():
        return "nproc"

    @constant
    def CMD_PARTED():
        return "parted"

    @constant
    def CMD_PVSCAN():
        return "pvscan"

    @constant
    def CMD_SMARTCTL():
        return "smartctl"

    @constant
    def CMD_STORCLI():
        return "storcli"

    @constant
    def CMD_UNAME():
        return "uname"

    @constant
    def CMD_VGCHANGE():
        return "vgchange"

    # === END HARDWARE COMMANDS ===
