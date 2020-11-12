#!/usr/bin/env python3

"""
This module contains functions for testing run-time variables.
"""

import collections
import pprint

from . import error

logger = logging.getLogger(__name__)


def get_debug(var):
    """Get pprint of variable.

    Args:
        var (any):

    Returns:
        var_pprint (PrettyPrinter): pprint of var.
    """
    if isinstance(var, collections.Callable):
        attrs = var.__module__ + "." + var.__name__
    else:
        try:
            attrs = vars(var)
        except TypeError:
            attrs = var
    var_pprint = pprint.pformat(attrs, width = 160, compact = True)
    return var_pprint


def check_null(var):
    """Raise error if variable is null.

    This can help avoid casading errors, by checking values before
    proceeding.

    Args:
        var (any): Variable to check.

    Returns:
        None

    Raises:
        error.NullValueError: Variable has null value.
    """
    if not var:
        try:
            raise error.NullValueError()
        except error.NullValueError:
            logger.error("Null Value Error")
            raise
    return None
