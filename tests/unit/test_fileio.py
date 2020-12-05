#!/usr/bin/env python3

import inspect
import os
from engcommon.fileio import write_file


def test_write_file():
    mypid = os.getpid()
    module_name = inspect.getmodulename(inspect.stack()[1][1])
    func_name = inspect.currentframe().f_code.co_name
    filename = "/tmp/test/{0}/{1}-{2}.log".format(module_name, func_name, mypid)
    write_file(filename, "test\n", "w")
    with open(filename, "r") as f:
        assert f.read() == "test\n"
