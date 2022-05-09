#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Robin Vobruba <hoijui.quaero@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

Normalize local (absolute and relative) paths in links and images.

Example:

`[l-name](./../some/dir/../some/../more/dirs/../here.txt)`

->

`[l-name](../some/more/here.txt)`

It is implemented as a Pandoc filter using panflute.

This might typicaly be used as an intermediate step
when combining a multitude of documents found within a directory tree
into a single document at the directory trees root.
Or more pracitcally: when creating a single PDF
out of a bunch of Markdown or HTML files scatered around the filesystem.

Usage example:
$ pandoc -f markdown -t markdown --markdown-headings=atx \
        --filter normalize_links.py \
        -o output.md \
        input.md
"""

from _common import check_version, is_url
check_version()

import os
import re
import panflute as pf
# TODO Instead of bs4/BeautifulSoup for parsing HTML, use pandoc itsself - panflute has functions for that, see its docu
from bs4 import BeautifulSoup

def normalize(url):
    """Normalize a URL string."""
    norm_url = url
    if not is_url(url):
        norm_url = os.path.normpath(url)
    return norm_url

def normalize_url(elem):
    """Normalize the elem.url."""
    elem.url = normalize(elem.url)

def normalize_html_link_or_image(elem):
    """Normalizes each a.href and img.src URL in a piece of HTML."""
    parsed = BeautifulSoup(elem.text, 'html.parser')
    replaced = False
    # Normalize anchors (links)
    anchors_with_href = parsed.findAll(
        lambda tag:
        tag.name == "a" and tag.get("href") is not None)
    for anchor in anchors_with_href:
        new_href = normalize(anchor.get("href"))
        if new_href != anchor.get("href"):
            anchor["href"] = new_href
            replaced = True
    # Normalize images
    imgs_with_src = parsed.findAll(
        lambda tag:
        tag.name == "img" and tag.get("src") is not None)
    for img in imgs_with_src:
        new_src = normalize(img.get("src"))
        if new_src != img.get("src"):
            img["src"] = new_src
            replaced = True
    if replaced:
        elem.text = str(parsed)
        # HACK Remove end-tag automatically inserted by BeautifulSoup as a sanitation matter, see https://stackoverflow.com/questions/57868615/how-to-disable-the-sanitizer-beautifulsoup
        elem.text = re.sub('></[^>]+>$', '>', elem.text)

def prepare(doc):
    """The panflute filter init method."""
    pass

def action(elem, doc):
    """The panflute filter main method, called once per element."""
    if isinstance(elem, (pf.Link, pf.Image)):
        normalize_url(elem)
    if isinstance(elem, pf.RawInline) and elem.format == 'html':
        normalize_html_link_or_image(elem)
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
