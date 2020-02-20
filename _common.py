"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

Contains common (utility) functions for the MoVeDo Pandoc filters.

This is typicaly used by importing it into panflute filter scripts:
import * from _common
"""

from __future__ import print_function

import re
import sys

# constants
REGEX_URL = re.compile(r'^(?:[a-z:_-]+)://', re.IGNORECASE)
REGEX_ABS_PATH = re.compile(r'^([A-Z]:)?[/\\]', re.IGNORECASE)
REQUIRED_VERSION = (3, 6)

def check_version():
    """Checks whether we are running on the minimum required python version."""
    cur_version = sys.version_info
    if cur_version < REQUIRED_VERSION:
        msg = (("ERROR: Your Python interpreter is too old. "
                "Please consider upgrading to at least %d.%d.")
               % (REQUIRED_VERSION[0], REQUIRED_VERSION[1]))
        sys.exit(msg)

def eprint(*args, **kwargs):
    """Prints a message to stderr, just like `print()` does for stdout)."""
    print(*args, file=sys.stderr, **kwargs)

def is_url(a_str):
    """Returns True if the argument is a URL."""
    return re.match(REGEX_URL, a_str) is not None

def is_abs_path(a_str):
    """Returns True if the argument is an absolute, local file path."""
    return re.match(REGEX_ABS_PATH, a_str) is not None

def is_rel_path(a_str):
    """Returns True if the argument is an absolute, local file path."""
    return not (is_url(a_str) or is_abs_path(a_str))

def get_arg(doc, key, default_value=None):
    """
    Returns the argument value (pandoc meta-data parameter) for the given key,
    or raises an error if it is not given, if `default_value` is `None`.
    """
    required = default_value is None
    if required:
        default_value = "<%s>" % key
    value = doc.get_metadata(key, default_value)
    if required and value == default_value:
        raise ValueError(
            ("Missing filter argument '%s'; " +
             "Use for example '-M %s=\"some_value\"' on the command line.")
            % (key, key))
    return value
