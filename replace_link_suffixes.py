#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Robin Vobruba <hoijui.quaero@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

Replaces the file extensions/suffixes of certain links in an input document.

It is implemented as a Pandoc filter using panflute.

This might typicaly be used to convert local links to *.md to *.html
while converting the format from Markdown to HTML,
as to maintain local cross-linking wihtin the used format.

Usage example:
$ pandoc -f markdown -t markdown --markdown-headings=atx \
        -M rls_relative_only=True \
        -M rls_ext_from=".md" \
        -M rls_ext_to=".html" \
        --filter replace_link_suffixes.py \
        -o output.md \
        input.md
"""

from _common import check_version, is_rel_path, get_arg
check_version()

import re
import panflute as pf

# constants
REGEX_REF_DELETER = re.compile(r'#.*$')
REGEX_PATH_DELETER = re.compile(r'^.*#')

# parameters
relative_only = True
ext_from = '.<unset_ext_from>'
ext_to = '.<unset_ext_to>'

def prepare(doc):
    """The panflute filter init method."""
    global relative_only, ext_from, ext_to
    relative_only = get_arg(doc, 'rls_relative_only', 'True') == 'True'
    ext_from = get_arg(doc, 'rls_ext_from')
    ext_to = get_arg(doc, 'rls_ext_to')

def replace_link_suffix(url):
    """If the URL fits, we replace the file suffix."""
    if not is_rel_path(url) and relative_only:
        return url
    path = re.sub(REGEX_REF_DELETER, '', url)
    ref = re.sub(REGEX_PATH_DELETER, '', url)
    if ref == url:
        ref = None
    if path.endswith(ext_from):
        url = path[:-len(ext_from)] + ext_to
        if ref is not None:
            url = url + '#' + ref
    return url

def action(elem, doc):
    """The panflute filter main method, called once per element."""
    if isinstance(elem, pf.Link):
        elem.url = replace_link_suffix(elem.url)
    # TODO Also do this with HTML links (using BeautifulSoup, see other filters)
    return elem

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

