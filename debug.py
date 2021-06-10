#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2016 Sergio Correia <sergio.correia@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""
This is part of the [MoVeDo](https://github.com/movedo) project.

Pretty print contents of the filters' input (both sys.argv and the JSON)

Usage example:
$ pandoc -f markdown -t markdown --markdown-headings=atx \
        --filter debug.py \
        -o output.md \
        input.md
"""

# HACK for panflute on python 2
from __future__ import unicode_literals

import sys
import json
import pprint
import pkg_resources

import panflute as pf

def action(elem, doc):
    if isinstance(elem, pf.Doc):
        version = pkg_resources.get_distribution("panflute").version
        json_serializer = lambda elem: elem.to_json()
        raw = json.dumps(elem, default=json_serializer)
        raw = json.loads(raw)
        raw = json.dumps(raw, check_circular=False,
                         indent=4, separators=(',', ': '))
        disclaimer = pf.Para(pf.Emph(pf.Str('Note: sort order not preserved')))
        elem.content = [
          pf.Header(pf.Str('Python version:'), level=2),
          pf.Para(pf.Str(sys.version)),
          pf.Header(pf.Str('Panflute version:'), level=2),
          pf.Para(pf.Str(version)),
          pf.Header(pf.Str('sys.argv:'), level=2),
          pf.Plain(pf.Str(str(sys.argv))),
          pf.Header(pf.Str('JSON Input:'), level=2),
          disclaimer,
          pf.CodeBlock(raw)
        ]

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == '__main__':
    main()
