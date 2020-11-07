#!/usr/bin/env python3

# Limit to important custom Exceptions
# Exception.args must be a tuple


class ShellCommandExecutionError(Exception):

    def __init__(self, d_args):
        self.msg = "Command failed with non-zero return code"
        self.args = list(d_args.items())

    def __str__(self):
        return self.msg


class NullValueError(Exception):

    def __init__(self):
        self.msg = "Variable has null value"

    def __str__(self):
        return self.msg


class PathNotExistError(Exception):

    def __init__(self, args):
        self.msg = "Path does not exist"
        self.args = args

    def __str__(self):
        return self.msg


class ProcessKilledError(Exception):

    def __init__(self, args):
        self.msg = "Process was killed"
        self.args = args

    def __str__(self):
        return self.msg


class HardwareCheckError(Exception):

    def __init__(self, args):
        self.msg = "Hardware check failed"
        self.args = args

    def __str__(self):
        return self.msg


class InvalidOptionError(Exception):

    def __init__(self, args):
        self.msg = "Invalid Command-Line Option"
        self.args = args

    def __str__(self):
        return self.msg
