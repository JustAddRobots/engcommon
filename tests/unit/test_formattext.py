#!/usr/bin/env python3

import pytest
from engcommon.formattext import add_color


@pytest.mark.parametrize("color, expected", [
    ("red", '\x1b[31mtest\x1b[0m'),
    ("green", '\x1b[32mtest\x1b[0m'),
    ("yellow", '\x1b[33mtest\x1b[0m'),
    ("blue", '\x1b[34mtest\x1b[0m'),
    ("magenta", '\x1b[35mtest\x1b[0m'),
    ("cyan", '\x1b[36mtest\x1b[0m'),
    ("bold", '\x1b[37mtest\x1b[0m'),
    ("dim", '\x1b[90mtest\x1b[0m')
])
def test_add_color(color, expected):
    assert add_color("test", color) == expected
