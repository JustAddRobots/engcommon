#!/usr/bin/env python3

import inspect
import os
from engcommon.fileio import write_file


def test_write_file():
    mypid = os.getpid()
    func_name = inspect.currentframe().f_code.co_name
    filename = "/tmp/test/engcommon/{0}-{1}.log".format(func_name, mypid)
    write_file(filename, "test\n", "w")
    with open(filename, "r") as f:
        assert f.read() == "test\n"
