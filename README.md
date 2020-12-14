# engcommon

## About

This repository is a collection of basic modules used to help query hardware, 
log and standardise output across different packages. Its meant to be used as a 
dependency for other packages or for quick querying while inside the Python
interpreter.

It is part of, [https://github.com/JustAddRobots/deployxhpl](deployxhpl), a working 
proof-of-concept CI/CD workflow that implements XHPL as a stress-test for baremetal HPC 
hardware.

It is built to run on *CentOS 7 Linux*. **There is no gaurantee this package will work
in any other environment.** There is **no support** for this project.


## Features

* Common Hardware Queries
* Shell Command Execution
* Unified Logger Config for CLI Projects


## Installing




## Usage

### Common hardware querying

```
>>> from engcommon import hardware
>>> hardware.get_cpu_vendor()
'intel'
>>> hardware.get_cpu_flags_with_prefix("avx")
['avx', 'avx2', 'avx512f', 'avx512dq', 'avx512cd', 'avx512bw', 'avx512vl', 'avx512_vnni']
>>> hardware.get_lscpu()["Model name"]
'Intel(R) Xeon(R) W-3245 CPU @ 3.20GHz'
```

Your environment may require root privileges for some hardware queries:

```
❯ sudo python3
Python 3.6.8 (default, Nov 16 2020, 16:55:22)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from engcommon import hardware
>>> d = hardware.get_dmidecode()
>>> print(d["BIOS Information"][0])
Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
        Vendor: VMware, Inc.
        Version: VMW71.00V.16722896.B64.2008100651
        Release Date: 08/10/2020
        ROM Size: 2048 kB
        Characteristics:
                ISA is supported
                PCI is supported
                PNP is supported
                BIOS is upgradeable
                Targeted content distribution is supported
                UEFI is supported
```

### Misc shell commands

```
>>> from engcommon import command
>>> d = command.get_shell_cmd("last|grep reboot")
>>> d.keys()
dict_keys(['ret_code', 'stdout', 'stderr'])
>>> print(d["stdout"])
reboot   system boot  3.10.0-1160.6.1. Sun Dec  6 13:36 - 14:53  (01:16)
reboot   system boot  3.10.0-1160.6.1. Sat Nov 28 23:23 - 14:53 (7+15:29)
reboot   system boot  3.10.0-1160.2.2. Tue Nov 17 15:57 - 22:18 (11+06:20)
```

### Logging

```
>>> from engcommon import clihelper
>>> from engcommon import randomword
>>> s = randomword.get_random_phrase()
>>> s
'trimly-cliched-facade'
>>> mycli = clihelper.CLI("runxhpl", {"logid": s, "prefix": "/tmp/logs", "debug": True})
>>> mycli.version
'0.4.0'
>>> mycli.logdir
'/tmp/logs/hosaka/trimly-cliched-facade/runxhpl.2020.12.07-184023'
>>> import pprint
>>> pprint.pprint(mycli.logger.handlers)
[<FileHandler /tmp/logs/hosaka/trimly-cliched-facade/runxhpl.2020.12.07-184023/runxhpl.cmd.52429.log (DEBUG)>,
 <StreamHandler <stdout> (DEBUG)>,
 <StreamHandler (DEBUG)>,
 <FileHandler /tmp/logs/hosaka/trimly-cliched-facade/runxhpl.2020.12.07-184023/runxhpl.debug.52429.log (DEBUG)>]
```

## License

Licensed under GNU GPL v3. See **LICENSE.md**.
