#!/usr/bin/python3

from engcommon.log import get_formatted_logs
from engcommon.log import get_std_logger_conf


def test_get_std_logger_conf():
    logger_keys = [
        'version',
        'disable_existing_loggers',
        'loggers',
        'formatters',
        'handlers'
    ]
    assert list(get_std_logger_conf().keys()) == logger_keys


def test_get_formatted_logs():
    var = {
        "neuromancer": ("The sky above the port was the color of television, "
                        "tuned to a dead channel."),
        "exhalation": ("It has long been said that air (which others call argon) "
                       "is the source of life.")
    }
    assert get_formatted_logs(var) == (
        '### neuromancer ###\n'
        'The sky above the port was the color of television, tuned to a dead channel.\n'
        '### exhalation ###\n'
        'It has long been said that air (which others call argon) is the source of life.\n'
    )
