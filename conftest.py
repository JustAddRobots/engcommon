#!/usr/bin/env python3

import pytest
from engcommon.clihelper import CLI


@pytest.fixture(scope="session")
def firstlines():
    var = {
        "neuromancer": ("The sky above the port was the color of television, "
                        "tuned to a dead channel."),
        "exhalation": ("It has long been said that air (which others call argon) "
                       "is the source of life.")
    }
    return var


@pytest.fixture(scope="function")
def mycli():
    args = {
        "log_id": "testily-testful-test",
        "prefix": "/tmp/logs/prefix",
        "debug": True
    }
    return CLI("engcommon", args)
