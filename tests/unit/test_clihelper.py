#!/usr/bin/env python3

import logging

logger = logging.getLogger(__name__)


def test_version(mycli):
    assert isinstance(mycli.version, str)


def test_log_id(mycli):
    assert mycli.log_id == "testily-testful-test"


def test_logdir(mycli):
    assert isinstance(mycli.logdir, str)


def test_logger(mycli):
    assert isinstance(mycli.logger, logging.Logger)


def test_logger_noformat(mycli):
    assert isinstance(mycli.logger_noformat, logging.Logger)


def test_print_logdir(mycli, caplog):
    mycli.print_logdir()
    assert ("LOGS: {0}".format(mycli.logdir)) in caplog.text


def test_get_stdout(mycli):
    assert isinstance(mycli.get_stdout(), str)
