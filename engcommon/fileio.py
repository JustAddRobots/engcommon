#!/usr/bin/env python3

"""
This module contains file I/O functions.
"""

import logging
from pathlib import Path

from . import testvar

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
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.error("Parent mkdir  Error")
        logger.debug(testvar.get_debug(filename))
        raise

    try:
        with open(filename, mode) as f:
            f.write(content)
            f.close()
    except OSError:
        logger.error("File Open Error")
        logger.debug(testvar.get_debug(filename))
        raise
    return None
