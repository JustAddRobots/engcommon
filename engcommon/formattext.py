#!/usr/bin/env python3

"""
This module contains functions for text formatting.
"""

import logging

logger = logging.getLogger(__name__)


def add_colour(text, colour):
    """Get coloured text string.

    Format statement must include space for control chars.

    Args:
        text (str): Text to colour.
        colour (str): Colour.

    Return:
        text_coloured (str): Coloured text.
    """
    colour_dict = {
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "bold": "37",
        "dim": "90",
    }
    prefix = "\033[{0}m".format(colour_dict[colour])
    suffix = "\033[0m"
    text_coloured = prefix + str(text) + suffix
    return text_coloured


def add_color(text, color):
    """Get colored text string."""
    return add_colour(text, color)
