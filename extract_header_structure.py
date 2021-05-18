#!/usr/bin/env python3
"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

This extracts the headers and compiles statistical meta-info about them.
The output is written to a separate file,
while the AST/the document is not modified at all.

It is implemented as a Pandoc filter using panflute.

This might typicaly be used to gater document strucutre info,
which would be used by an other filter as input to modfy the document.

Usage example:
$ pandoc -f markdown -t markdown --markdown-headings=atx \
        -M ehs_output_file="extracted_headers.txt" \
        --filter extract_header_structure.py \
        -o output.md \
        input.md
"""

# HACK for panflute on python 2
#      -> DEPRECATED, Python 2 is not supported anymore by panflute anyway
from __future__ import unicode_literals

from _common import check_version, eprint, get_arg
check_version()

import panflute as pf

# constants
MIN_LEVEL = 1
# NOTE This will be 10 in future pandoc versions (not yet in pandoc 2.7.3)
MAX_LEVEL = 6
MAX_LEVEL = 10

# parameters
# how many instances of each header level we encountered
counters = []
output_file = ''
ofh = None

def prepare(doc):
    """The panflute filter init method."""
    global counters, output_file, ofh
    for _ in range(MIN_LEVEL, MAX_LEVEL):
        counters.append(0)
    output_file = get_arg(doc, 'ehs_output_file')
    ofh = open(output_file, "w")

def action(elem, doc):
    """The panflute filter main method, called once per element."""
    global counters
    if isinstance(elem, pf.Header):
        lvl = elem.level - MIN_LEVEL
        counters[lvl] = counters[lvl] + 1
        ofh.write('%d %s\n' % (lvl + 1, elem.identifier))
    return elem

def finalize(doc):
    """The panflute filter "destructor" method."""
    ofh.write('####\n')
    total = 0
    min = 999
    max = 0
    for lvl in range(MIN_LEVEL, MAX_LEVEL):
        cnt = counters[lvl - MIN_LEVEL]
        total += cnt
        if lvl > max and cnt > 0:
            max = lvl
        if lvl < min and cnt > 0:
            min = lvl
        ofh.write('# %s: %d\n' % ("Headers of level %d", MIN_LEVEL + lvl, cnt))
    ofh.write('# %s: %d\n' % ("Total headers", total))
    ofh.write('# %s: %d\n' % ("Min header level", min))
    ofh.write('# %s: %d\n' % ("Max header level", max))
    ofh.close()

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
