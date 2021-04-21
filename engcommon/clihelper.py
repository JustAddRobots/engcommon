#!/usr/bin/env python3

"""
This module generalises common code typically used in a project's CLI
(i.e project/project/cli.py) thus allowing for custom standardised CLI
output across packages.

    Typical Usage:

    my_cli = clihelper.CLI(project_name, command_args)
    logger = my_cli.logger
    my_cli.print_versions()
"""

import logging
import os
import pkg_resources

from . import fileio
from . import formattext
from . import log
from . import randomword
from . import testvar

logger = logging.getLogger(__name__)


class CLI:
    """A class for organising CLI bits.

    This class is used to facilitate consistent CLI output across packages.

    Attributes:
        version (str): Version.
        log_id (str): Unique runtime ID.
        logdir (str): Log directory for CLI output.
        logger (logging.Logger): Standardised custom logger.
        logger_noformat (logging.Logger): Custom logger without formatting.
    """

    def __init__(self, project_name, args):
        """Init CLI.

        Args:
            project_name (str): Project name seen by installer.
            args (dict): Command line arguments.
                {
                    log_id (str): Override random runtime ID with this.
                    prefix (str): Prefix for log directory.
                    debug (bool): Enable/disable debug mode.
                }
        """
        self._project_name = self._get_project_name(project_name)
        self._args = self._get_args(args)
        self._version = pkg_resources.get_distribution(project_name).version
        self._log_id = self._get_log_id()
        self._logdir = log.get_logdir(
            self._project_name,
            prefix = self._args["prefix"],
            suffix = self._log_id,
        )
        os.makedirs(self._logdir, exist_ok=True)
        loggers = log.get_std_logger(
            self._project_name,
            self._args["debug"],
            logdir = self._logdir,
        )
        self._logger = loggers[0]
        self._logger_noformat = loggers[1]
        self._fh = self._logger.handlers[0]  # file
        self._ch = self._logger.handlers[1]  # console
        self._bh = self._logger.handlers[2]  # buffer
        self._dh = self._logger.handlers[3]  # debug file

    @property
    def version(self):
        """Get version."""
        return self._version

    @property
    def log_id(self):
        """Get log_id."""
        return self._log_id

    @property
    def logdir(self):
        """Get logdir."""
        return self._logdir

    @property
    def logger(self):
        """Get logger."""
        return self._logger

    @property
    def logger_noformat(self):
        """Get logger_noformat."""
        return self._logger_noformat

    def _get_project_name(self, name):
        try:
            pkg_resources.get_distribution(name)
        except pkg_resources.DistributionNotFound:
            raise RuntimeError("Package Not Found: {0}".format(name))
        return name

    def _get_args(self, args):
        if not isinstance(args, dict):
            raise TypeError("Arguments must be dict")
        if "logid" in args.keys():  # Rename log_id
            args["log_id"] = args.pop("logid")
        return args

    def _get_log_id(self):
        if not self._args["log_id"]:
            log_id = randomword.get_random_phrase()
        else:
            log_id = self._args["log_id"]
        return log_id

    def _get_third_party_list(self):
        """Get third party packages to use for version map.

        Get a list of packages whose version number we'll want.

        Args:
            None

        Returns:
            third_party (list): List of packages.
        """
        third_party = ["engcommon"]
        return third_party

    def _get_versions(self, tool_list):
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

    def _print_versions(self):
        """Print module and third-party dependency versions.

        Print versions to verify version compatibility.
        """
        module_title = ("{0} v: {1}".format(
            self._project_name,
            self._version,
        ))
        logger.debug(formattext.add_colour(module_title, "blue"))
        third_party = self._get_third_party_list()
        versions = self._get_versions(third_party)
        for tool, ver in versions.items():
            logger.debug("{0} v: {1}".format(tool, ver))
        logger.debug(testvar.get_debug(self._args))
        return None

    def print_versions(self):
        """Print versions."""
        self._print_versions()
        return None

    def _print_logdir(self):
        logger.debug("LOGS: {0}".format(self.logdir))
        return None

    def print_logdir(self):
        """Print logdir."""
        self._print_logdir()
        return None

    def _write_logs(self, dict_, mode):
        """Write runtime tests to logfile.

        Args:
            dict_ (dict): keys are test names, values are test output.
            mode (str): File write mode (Ex. 'w' = write, 'a' = append).

        Returns:
            None
        """
        logfile_cmd = self._fh.baseFilename
        logfile_test = logfile_cmd.replace('.cmd.', '.test.')
        str_ = log.get_formatted_logs(dict_)
        fileio.write_file(logfile_test, str_, mode)
        return None

    def write_logs(self, dict_, mode):
        self._write_logs(dict_, mode)
        return None

    def _get_stdout(self):
        """Get the STDOUT CLI stream."""
        logger.debug("Saving STDOUT")
        stdout = self._bh.stream.getvalue()
        self._bh.stream.close()
        self.logger.removeHandler(self._bh)
        return stdout

    def get_stdout(self):
        return self._get_stdout()
