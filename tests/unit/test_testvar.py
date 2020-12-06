#!/usr/bin/env python3

import pytest
import engcommon.error as error
from engcommon.testvar import check_null
from engcommon.testvar import get_debug


def test_get_debug():
    var = {
        "l": [1, 2.0],
        "t": ("one", "two")
    }
    assert get_debug(var) == "{'l': [1, 2.0], 't': ('one', 'two')}"


def test_check_null():
    with pytest.raises(error.NullValueError):
        check_null("")
