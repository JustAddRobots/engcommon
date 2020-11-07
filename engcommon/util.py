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


def write_file(filename, content, mode):
    """Write file, handle exceptions.

    Args:
        filenmame (str): File path.
        content (any): File content.
        mode (str): File write mode.

    Returns:
        None

    Raises:
        OSError: Error opening file.
    """
    try:
        f = open(filename, mode)
    except OSError:
        logger.error("File Open Error")
        logger.debug(get_debug(filename))
        raise
    else:
        f.write(content)
        f.close()
    return None


def download_url(url, savefile):
    """Download URL.

    Args:
        url (str): URL.
        savefile (str): Savefile path.

    Returns:
        None

    Raises:
        IOError: Error downloading URL.
    """
    try:
        urllib.request.urlretrieve(url, savefile)
    except IOError:
        logger.error("URL Download Error")
        logger.debug(get_debug(url))
        raise
    return None


def extract_tarball(tarball, **kwargs):
    """Extract tarball to dir, default is "/tmp".

    Args:
        tarball (str): Tarball filename.

    **kwargs:
        cwd (str): Current working dir in which to extract tarball.

    Returns:
        None
    """
    my_cwd = kwargs.setdefault("cwd", "/tmp")

    if (tarball.endswith(".tgz") or tarball.endswith(".tar.gz")):
        cmd = "tar --overwrite -xzf {0}".format(tarball)
    elif (tarball.endswith(".tbz") or tarball.endswith(".tar.bz2")):
        cmd = "tar --overwrite -xjf {0}".format(tarball)
    logger.debug("Extracting tarball: {0}".format(tarball))
    call_shell_cmd(cmd, cwd = my_cwd)
    return None


def backup_files(files, **kwargs):
    """Backup list of files using default suffix.

    Args:
        files (list): List of files to backup.

    **kwargs:
        suffix (str): Suffix for backup file.

    Returns:
        None

    Raises:
        IOError: Error backing up file.
    """
    suffix = kwargs.setdefault("suffix", "ORIG")
    for filename in files:
        new_name = filename + ".{0}".format(suffix)
        try:
            shutil.copy2(filename, new_name)
        except IOError:
            logger.error("File Backup Error")
            logger.debug(get_debug(filename))
            raise
    return None


def restore_files(files, **kwargs):
    """Restore list of files with default suffix.

    Args:
        files (list): List of files to restore.

    **kwargs:
        suffix (str): Suffix for backup file.

    Returns:
        None

    Raises:
        IOError: Error restoring file.
    """
    suffix = kwargs.setdefault("suffix", "ORIG")
    for filename in files:
        new_name = filename.rstrip(".{0}".format(suffix))
        try:
            shutil.move(filename, new_name)
        except IOError:
            logger.error("File Restore Error")
            logger.debug(get_debug(filename))
            raise
    return None


def make_mount_points(mount_points):
    """Make mount points from list.

    Args:
        mount_points (list): Mount points.

    Returns:
        None

    Raises:
        OSError: Error making mount point.
    """
    for mnt_pt in mount_points:
        try:
            os.mkdir(mnt_pt)
        except OSError:
            logger.error("Make Mountpoint Error")
            logger.debug(get_debug(mnt_pt))
            raise
    return None


def add_colour(text, colour):
    """Get coloured text string.

    Format statement must include space for control chars.

    Args:
        text (str): Text to colour.
        colour (str): Colour.

    Return:
        text_coloured (str): Coloured text.
    """
    colour_dict = {
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "bold": "37",
        "dim": "90",
    }
    prefix = "\033[{0}m".format(colour_dict[colour])
    suffix = "\033[0m"
    text_coloured = prefix + str(text) + suffix
    return text_coloured


def add_color(text, color):
    """Get colored text string."""
    return add_colour(text, color)


def get_debug(var):
    """Get pprint of variable.

    Args:
        var (any):

    Returns:
        var_pprint (PrettyPrinter): pprint of var.
    """
    if isinstance(var, collections.Callable):
        attrs = var.__module__ + "." + var.__name__
    else:
        try:
            attrs = vars(var)
        except TypeError:
            attrs = var
    var_pprint = pprint.pformat(attrs, width = 160, compact = True)
    return var_pprint


def check_null(var):
    """Raise error if variable is null.

    This can help avoid casading errors, by checking values before
    proceeding.

    Args:
        var (any): Variable to check.

    Returns:
        None

    Raises:
        error.NullValueError: Variable has null value.
    """
    if not var:
        try:
            raise error.NullValueError()
        except error.NullValueError:
            logger.error("Null Value Error")
            raise
    return None


def convert_to_int(var):
    """Get var converted to integer.

    This is useful for SQL/OMS queries.

    Args:
        var (any): Varible to convert.

    Returns:
        var (int): Variable.

    Raises:
        ValueError: Error Converting to Integer.
    """
    try:
        var = int(var)
    except ValueError:
        logger.error("Integer Conversion Error")
        logger.debug(get_debug(var))
        raise
    return var


def glob_copy(src, dest):
    """Copy file/dir to existing destination dir using glob wildcards.

    Args:
        src (str): File/dir source path.
        dest (str): File/dir desitination path.

    Returns:
        None

    Raises:
        IOError: shutil.copy2 Error copying file.
        shutil.Error: shutil.copytree Error copying dir.
    """
    src_dir = os.path.dirname(src)
    for i in [src_dir, dest]:
        if not os.path.isdir(i):
            try:
                raise error.PathNotExistError({
                    'path': i,
                })
            except error.PathNotExistError as e:
                logger.error("Path Not Exist Error")
                logger.debug(get_debug(e.args))
                raise

    glob_list = glob.glob(src)
    for filename in glob_list:
        logger.debug(get_debug(filename))
        dest_tree = dest + "/" + os.path.basename(filename)
        try:
            if os.path.isfile(filename):
                shutil.copy2(filename, dest)
            elif os.path.isdir(filename):
                shutil.copytree(filename, dest_tree, symlinks = True)
        except IOError:
            logger.error("Glob Copy Error")
            logger.debug(get_debug((filename, dest)))
            raise
        except shutil.Error:
            logger.error("Glob Copytree Error")
            logger.debug(get_debug((filename, dest_tree)))
            raise
    return None


def glob_remove(pathname):
    """Remove file/dir using glob wildcards.

    Args:
        pathname (str): File/dir path to remove.

    Returns:
        None

    Raises:
        IOError: Error removing path in glob list.
        IOError: Error removing path.
    """
    if "*" in pathname:
        glob_list = glob.glob(pathname)
        for filename in glob_list:
            try:
                if os.path.isfile(filename):
                    os.remove(filename)
                elif os.path.isdir(filename):
                    shutil.rmtree(filename)
            except IOError:
                logger.error("Glob Remove Error")
                logger.debug(get_debug(filename))
                raise
    else:
        if os.path.exists(pathname):
            try:
                if os.path.isfile(pathname):
                    os.remove(pathname)
                elif os.path.isdir(pathname):
                    shutil.rmtree(pathname)
            except IOError:
                logger.error("Glob Remove Error")
                logger.debug(get_debug(pathname))
    return None


def check_returncode(cmd, ret_code):
    """Check the returncode of a command. Raise if problematic.

    Some platforms + commands are broken and some commands must be ignored
    (e.g. fru on Asus ESC4000).

    Args:
        cmd (str): Command to check.
        ret_code (str): Return code.

    Returns:
        None

    Raises:
        error.ShellCommandExecutionError: Error executing command.
    """
    ignore_returncode = False
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    if ret_code != 0:
        for k, v in CONSTANTS().IGNORE_RETURNCODE.items():
            if cmd.startswith(k) and ret_code == v:
                ignore_returncode = True
                break
        if not ignore_returncode:
            try:
                raise error.ShellCommandExecutionError({
                    'ret_code': ret_code,
                    'cmd': cmd,
                })
            except error.ShellCommandExecutionError as e:
                logger.info(get_debug(e.args))
                logger.error("Shell Command Execution Error")
                raise
    return None


def call_shell_cmd(cmd, stdout=None, stderr=subprocess.STDOUT, **kwargs):
    """Run shell command, disregard the output.

    Args:
        cmd (str): Command to run.

    **kwargs:
        cwd (str): Current working dir from which to run cmd.
        shell (bool): Run command in shell mode.
        add_env (mapping): Environment variable mapping.

    Returns:
        None

    Raises:
        OSError: Error starting command.
    """
    my_cwd = kwargs.setdefault("cwd", None)
    my_shell = kwargs.setdefault("shell", False)
    my_env = kwargs.setdefault("add_env", os.environ.copy())
    if not(stdout):
        FNULL = open(os.devnull, 'w')
        stdout = FNULL

    if ("|" in cmd) or ('*' in cmd) or ('?' in cmd):
        my_shell = True
    else:
        cmd = shlex.split(cmd)

    try:
        p = subprocess.Popen(
            cmd,
            shell = my_shell,
            stdout = stdout,
            stderr = stderr,
            cwd = my_cwd,
            env = my_env,
            close_fds = True,
        )
    except OSError:
        logger.error("Shell Command Start Error")
        logger.debug(get_debug((cmd, my_cwd, my_shell)))
        raise
    else:
        p.communicate()
        ret_code = p.returncode
        check_returncode(cmd, ret_code)
    time.sleep(1)
    return None


def cmd_cleanup(cmd):
    """Create a command list from shell command.

    Process a shell command into a list to be processed by
    subprocess.Popen.

    Quotes are handled. Wildcards are expanded. Regex is passed through.

    Args:
        cmd (str): Command to be parsed.

    Returns:
        cmd_list (list): Parsed commands.
    """
    cmd_list = []
    cmd_split = shlex.split(cmd)
    regex_cmds = [
        "sed",
        "grep",
        "egrep",
    ]
    for arg in cmd_split:
        if (
            (("*" in arg) or ("?" in arg))
            and (cmd_split[0] not in regex_cmds)
        ):
            arg = glob.glob(arg)
            cmd_list.extend(arg)
        else:
            cmd_list.append(arg)
    return cmd_list


def get_shell_cmd(cmd, **kwargs):
    """Get shell command output.

    Args:
        cmd (str):

    Returns:
        dict(
            ret_code (str): Return code.
            stdout (str): STDOUT.
            stderr (str): STDERR.
        )

    Raises:
        OSError: Error starting shell command.
        KeyboardInterrupt: CTRL-C caught while running command.
    """
    my_cwd = kwargs.setdefault("cwd", None)
    my_encoding = kwargs.setdefault("encoding", 'utf-8')
    my_stdin = None
    cmd_list = []

    # Create command list from pipes for chaining in subprocess.Popen
    if "|" in cmd:
        cmd_list = cmd.split("|")
    else:
        cmd_list.append(cmd)

    for i, cmd in enumerate(cmd_list):
        cmd = cmd_cleanup(cmd)
        try:
            p = subprocess.Popen(
                cmd,
                shell = False,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                cwd = my_cwd,
                encoding = my_encoding,
            )
        except OSError:
            logger.error("Shell Command Start Error")
            logger.debug("cmd: {0}".format(cmd))
            raise
        else:
            try:
                r = p.communicate(my_stdin)
            except KeyboardInterrupt:
                logger.error("Keyboard Interrupt, sending SIGTERM")
                logger.debug(get_debug(cmd))
                p.terminate()
                raise
            else:
                stderr = r[1]
                ret_code = p.returncode
                check_returncode(cmd, ret_code)
                if i == (len(cmd_list) - 1):  # Last command
                    stdout = r[0]
                else:  # Otherwise pipe to next command
                    my_stdin = r[0]

    return {
        'ret_code': ret_code,
        'stdout': stdout,
        'stderr': stderr
    }


def call_sql_cmd(c, cmd, **kwargs):
    """Run SQL command, disregard output.

    Args:
        c (pymysql.cursor): PyMySQL cursor.
        cmd (str): SQL command.

    **kwargs:
        data (tuple): Data to interpolate in SQL "cmd".

    Returns:
        None

    Raises:
        pymysql.OperationalError: Error in SQL operation.
        pymysql.ProgrammingError: Error in SQL syntax.
    """
    my_data = kwargs.setdefault("data", tuple())
    try:
        c.execute(cmd, my_data)
    except pymysql.OperationalError:
        logger.error("pymysql Error")
        logger.debug("cmd: {0}".format(cmd))
        raise
    except pymysql.ProgrammingError:
        logger.error("pymysql Programming Error")
        logger.debug("cmd: {0}".format(cmd))
        raise
    return None


def get_sql_fetchall(c, cmd):
    """Get SQL fetchall command oyutput.

    Args:
        c (pymysql.cursor): PyMySQL cursor.
        cmd (str): SQL command.

    Returns:
       str_ (str): Command result.

    Raises:
        pymysql.OperationalError: Error in SQL operation.
        pymysql.ProgrammingError: Error in SQL syntax.
    """
    str_ = ""
    try:
        c.execute(cmd)
    except pymysql.OperationalError:
        logger.error("pymysql Error")
        logger.debug("cmd: {0}".format(cmd))
        raise
    except pymysql.ProgrammingError:
        logger.error("pymysql Programming Error")
        logger.debug("cmd: {0}".format(cmd))
        raise
    else:
        str_ = c.fetchall()
    return str_


def get_sql_fetchone(c, cmd):
    """Get SQL fetchone command output.

    Args:
        c (pymysql.cursor): PyMySQL cursor.
        cmd (str): SQL command.

    Returns:
       str_ (str): Command result.

    Raises:
        pymysql.OperationalError: Error in SQL operation.
        pymysql.ProgrammingError: Error in SQL syntax.
    """
    str_ = ""
    try:
        c.execute(cmd)
    except pymysql.OperationalError:
        logger.error("pymysql Error")
        logger.debug("cmd: {0}".format(cmd))
        raise
    except pymysql.ProgrammingError:
        logger.error("pymysql Programming Error")
        logger.debug("cmd: {0}".format(cmd))
        raise
    else:
        str_ = c.fetchone()

    return str_


def get_enviro():
    """Get environment.

    Get operating environment for system (e.g. anaconda, nfsroot).

    Args:
        None

    Returns:
        enviro (str): Operating environment.
    """
    enviro = ""
    root_dev = hardware.get_root_dev()
    disk_prefixes = [
        'sd',
        'md',
    ]
    if "live-rw" in root_dev:
        if os.path.exists("/var/run/anaconda.pid"):
            enviro = "anaconda"
    elif "nfsroot" in root_dev:  # iso nfsroot pathnames
        enviro = "nfsroot"
    else:
        if not enviro:
            for prefix in disk_prefixes:
                if root_dev.startswith("/dev/{0}".format(prefix)):
                    enviro = "postinstall"
                    break
        if not enviro:
            cmd = "{0}".format(CONSTANTS().CMD_MOUNTS)
            dict_ = get_shell_cmd(cmd)
            stdout = dict_["stdout"]
            for line in stdout.splitlines():
                regex = r"BeoBoot[\s]+/[\s]+tmpfs"
                match = re.match(regex, line)
                if match:
                    enviro = "computenode"
                    break

    return enviro


def get_os_ver(**kwargs):
    """Get OS version from distro version file.

    Args:
        None

    **kwargs:
        prefix (str): Prefix dir (helpful for anaconda and NFSroot FS).

    Returns:
        os_ver (str): OS version.

    Raises:
        IOError: Error opening version file.
    """
    prefix = kwargs.setdefault("prefix", "")
    os_ver = ""
    distro_files = [
        "/etc/redhat-release",
        "/etc/centos-release",
        "/etc/system-release",
        "/etc/issue",
    ]
    for filename in distro_files:
        filename = "{0}{1}".format(prefix, filename)
        if os.path.exists(filename):
            try:
                f = open(filename, "r")
            except IOError:
                logger.error("Version File Open Error")
                logger.debug(get_debug(filename))
                raise
            else:
                os_ver = f.readlines()[0]
                os_ver = os_ver.rstrip()
                f.close()
                break
    check_null(os_ver)
    return os_ver


def get_os_ver_num(**kwargs):
    """Get OS major and minor numbers.

    Args:
        None

    **kwargs:
        See get_os_ver().

    Returns:
        ver_num (str): Version number.
    """
    os_ver = get_os_ver(**kwargs)
    re_num = r".*release\s([0-9]+.[0-9]+)"
    match = re.search(re_num, os_ver)
    check_null(match)
    ver_num = match.groups()[0]
    return ver_num


def get_ks_file():
    """Get the contents of kickstart file.

    Args:
        None

    Returns:
        ks_file (str): Kickstart file contents.

    Raises:
        OSError: Error opening kickstart file.
    """
    ks_file = ""
    for filename in CONSTANTS().KS_FILES:
        if os.path.exists(filename):
            try:
                f = open(filename, 'r')
            except OSError:
                raise
            else:
                ks_file = f.read()
                f.close()
            break
    return ks_file


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
    """Get logger config dict.

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


def get_versions(tool_list):
    """Get tools with their versions.

    Args:
        tool_list (list): Tools of which to get versions.

    Returns:
        versions (dict): keys are tool name, values are version string.
        Ex: {
                "flashupdt": "14.1 Build 22",
                "storcli": "007.0813.0000.0000",
            }
    """
    # Shell command to get the version number for each tool
    bin_tools = {
        'nvidia': r"cat /proc/driver/nvidia/version | sed -rn 's/.*Module\s+([0-9.]+).*$/\1/p'",
        'cuda': r"cat /usr/local/cuda/version.txt | sed -rn 's/.*Version\s+([0-9.]+).*$/\1/p'",
        'storcli': r"storcli -v | sed -rn 's/.*Ver\s+([0-9.]+).*$/\1/p'",
        'flashupdt': r"flashupdt -h | sed -rn 's/.*Version\s+([0-9a-zA-z. ]+).*$/\1/p'",
    }
    pkgs = {i.key: i.version for i in pkg_resources.working_set}
    versions = {}
    for tool in tool_list:
        if tool in pkgs.keys():
            versions[tool] = pkgs[tool]
        elif tool in bin_tools.keys():
            cmd = bin_tools[tool]
            if isinstance(cmd, str):
                versions[tool] = get_shell_cmd(cmd)["stdout"].strip()
            elif isinstance(cmd, collections.Callable):
                versions[tool] = cmd()
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
    if hardware.is_gpu("nvidia"):
        if not hardware.is_loaded_module("nouveau"):
            third_party.extend(["nvidia", "cuda"])
    if (
        (get_enviro() == "nfsroot") and (not hardware.is_VM())
    ):
        third_party.append("storcli")
        third_party.append("flashupdt")
    return third_party


def get_cuda_compat_tbl():
    """Get dict of CUDA toolkit <--> NVIDIA driver version compatibility.

    https://docs.nvidia.com/deploy/cuda-compatibility/index.html

    Args:
        None
    Returns:
        tbl (dict): Compatibility table.
    """
    tbl = {
        "10.2.89": "440.33",
        "10.1.105": "418.39",
        "10.0.130": "410.48",
        "9.2.88": "396.26",
        "9.1.85": "390.46",
        "9.0.76": "384.81",
        "8.0.61 GA2": "375.26",
        "8.0.44": "367.48",
        "7.5.16": "352.31",
        "7.0.28": "346.46",
    }
    return tbl


def is_compat_nvidia_cuda(tool_versions):
    """Get whether there is NVIDIA driver / CUDA toolkit compatibility.

    NVIDIA driver version should be >= the corresponding CUDA toolkit.

    Args:
        tool_versions (dict): Tools and their verion strings.

    Returns:
        compat (bool): True if driver / toolkit is compatible.
    """
    compat = True
    if all(tool in tool_versions.keys() for tool in ['nvidia', 'cuda']):
        if not (
            packaging.version.parse(tool_versions["nvidia"])
            >= packaging.version.parse(
                get_cuda_compat_tbl()[tool_versions["cuda"]]
            )
        ):
            compat = False
    return compat


def get_random_phrase(**kwargs):
    """Get a random dash-separated n-words-length phrase.

    This may be preferable to a random hex string for user
    readability (e.g. log_id).

    Args:
        None

    **kwargs:
        min_length (int): Minimum character length per word.
        max_length (int): Maximum character length per word.
        POS_order (list): Part-of-speech order.

    Returns:
        phrase (str): Random phrase.
    """
    min_length = int(kwargs.setdefault('min_length', 2))
    max_length = int(kwargs.setdefault('max_length', 8))
    POS_order = kwargs.setdefault(
        'POS_order',
        ['adverb', 'adjective', 'noun'],
    )
    # words_url = "https://raw.githubusercontent.com/palmdalian/json_wordlist/master/wordlist_nocaps_byPOS.json"
    words_url = "http://iso.penguincomputing.com/ark/tmp/wordlist_nocaps_byPOS.json"
    f = urllib.request.urlopen(words_url)
    words = json.loads(f.read())  # dict keys are part-of-speech (POS)
    good_word_list = []
    while len(POS_order) > 0:
        word = random.choice(words[POS_order[0]])
        word = word.replace(' ', '')
        if len(word) >= min_length:
            if len(word) <= max_length:
                good_word_list.append(word)
                POS_order.pop(0)
    phrase = "-".join(good_word_list)
    return phrase


def get_random_phrase_probability(**kwargs):
    """Get the probability of a n-words-length phrase being randomly
     selected from word list.

    This is useful to gauge how long to make a random phrase to preserve
    uniqueness of database entries. The smaller the probability, the less
    likely it will be selected for use. Compare the order of magnitude
    of probability to the order of magnitude of expected database entries.

    Args:
        None

    **kwargs:
        min_length (int): Minimum character length per word.
        max_length (int): Maximum character length per word.
        POS_order (list): Part-of-speech order.

    Returns:
        prob (float) = Probability of duplicate phrase being selected.
    """
    min_length = int(kwargs.setdefault('min_length', 2))
    max_length = int(kwargs.setdefault('max_length', 8))
    POS_order = kwargs.setdefault(
        'POS_order',
        ['adverb', 'adjective', 'noun'],
    )
    words_url = "http://iso.penguincomputing.com/ark/tmp/wordlist_nocaps_byPOS.json"
    f = urllib.request.urlopen(words_url)
    words = json.loads(f.read())  # dict keys are part-of-speech (POS)
    prob = 1.00
    # For each POS, divide prob by frequency of n-char-length word.
    # See LOAD-831 for the character-count distribution of each POS.
    for POS in POS_order:
        len_c = [len(i) for i in words[POS]]
        array_c = numpy.array([[j, len_c.count(j)] for j in set(len_c)])
        min_row = int(numpy.where(array_c[:, 0] == min_length)[0])
        max_row = int(numpy.where(array_c[:, 0] == max_length)[0]) + 1
        num_words = array_c[min_row:max_row, 1].sum()
        prob *= float(1 / num_words)
    return prob


def copy(src, dst, overwrite_if_exists=False):
    # Copy files/directories.
    # Include filename in dst or
    # it will not work if the dst
    # is an existing directory.
    # From http://stackoverflow.com/questions/1994488/copy-file-or-directories-recursively-in-python
    if overwrite_if_exists and os.path.exists(dst):
        glob_remove(dst)

    try:
        shutil.copytree(src, dst)
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise
