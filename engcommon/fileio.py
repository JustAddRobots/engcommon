#!/usr/bin/env python3

"""
This module contains file I/O functions.
"""

import logging

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
