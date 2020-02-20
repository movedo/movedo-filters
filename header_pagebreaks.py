#!/usr/bin/env python3
"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

Adds page-breaks before headers (of a certain level or lower).

It is implemented as a Pandoc filter using panflute.

Usage example:
$ pandoc -f markdown -t markdown --atx-headers \
        -M max_level=1 \
        --filter header_pagebreaks.py \
        -o output.md \
        input.md
"""

# HACK for panflute on python 2
#      -> DEPRECATED, Python 2 is not supported anymore by panflute anyway
from __future__ import unicode_literals

from _common import check_version
check_version()

import panflute as pf

# parameters
# should eventually be a value between 1 and 10
max_level = 0

def prepare(doc):
    """The panflute filter init method."""
    global max_level
    max_level = int(doc.get_metadata('hp_max_level', '2'))

def action(elem, doc):
    if isinstance(elem, pf.Header) and elem.level <= max_level:
        pagebreak = pf.RawBlock('\pagebreak{}', format='latex')
        return [pagebreak, elem]

def finalize(doc):
    """The panflute filter "destructor" method."""
    pass

def main(doc=None):
    """
    NOTE: The main function has to be exactly like this
    if we want to be able to run filters automatically
    with '-F panflute'
    """
    return pf.run_filter(
        action,
        prepare=prepare,
        finalize=finalize,
        doc=doc)

if __name__ == '__main__':
    main()
