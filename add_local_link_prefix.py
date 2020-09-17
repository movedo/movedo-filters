#!/usr/bin/env python3
"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

Adds a prefix to all *local*, *relative* link & image paths,
consisting of the relative path from PWD to the input document.
So for example, if we call `pandoc ... my/input/file.md`,
the paths would be prefixed with 'my/input/'.

It is implemented as a Pandoc filter using panflute.

This might typicaly be used as a preparation step
when combining a multitude of documents found within a directory tree
into a single document at the directory trees root.
Or more pracitcally: when creating a single PDF
out of a bunch of Markdown or HTML files scatered around the filesystem.

Usage example:
$ pandoc -f markdown -t markdown --atx-headers \
        -M allp_prefix="some/static/prefix/" \
        -M allp_file="input.md" \
        --filter add_local_link_prefix.py \
        -o output.md \
        input.md
"""

# HACK for panflute on python 2
#      -> DEPRECATED, Python 2 is not supported anymore by panflute anyway
from __future__ import unicode_literals

from _common import check_version, is_rel_path, get_arg
check_version()

import re
import panflute as pf
from bs4 import BeautifulSoup

# parameters
# should be something like 'some/static/prefix/'
prefix = '<default-prefix>'
# should be something like 'file-name.md'
file_name = '<default-file-name>'

def prefix_if_rel_path(url):
    """
    Prefixes the input URL with the prefix,
    if the URL is a link to/image with a relative path.
    """
    global prefix, file_name
    if is_rel_path(url):
        if url.startswith('#'):
            url = file_name + url
        else:
            url = prefix + url
    return url

def prefix_elem_if_rel_path(elem):
    """
    Prefixes the URL of an input element with the prefix,
    if the URL is a link to/image with a relative path.
    """
    elem.url = prefix_if_rel_path(elem.url)

def prefix_html(elem):
    """Prepends the reference-formatted relative file path to the identifier."""
    parsed = BeautifulSoup(elem.text, 'html.parser')
    replaced = False
    anchors_with_href = parsed.findAll(
        lambda tag:
        tag.name == "a" and tag.get("href") is not None)
    for anchor in anchors_with_href:
        new_href = prefix_if_rel_path(anchor.get("href"))
        if new_href != anchor.get("href"):
            anchor["href"] = new_href
            replaced = True
    imgs_with_src = parsed.findAll(
        lambda tag:
        tag.name == "img" and tag.get("src") is not None)
    for img in imgs_with_src:
        new_src = prefix_if_rel_path(img.get("src"))
        if new_src != img.get("src"):
            img["src"] = new_src
            replaced = True
    if replaced:
        elem.text = str(parsed)
        # HACK Remove end-tag automatically inserted by BeautifulSoup as a sanitation matter, see https://stackoverflow.com/questions/57868615/how-to-disable-the-sanitizer-beautifulsoup
        elem.text = re.sub(r'></[^>]+>$', '>', elem.text)
    #eprint("XXX allp HTML after '%s'" % elem.text)

def prepare(doc):
    """The panflute filter init method."""
    global prefix, file_name
    prefix = get_arg(doc, 'allp_prefix')
    file_name = get_arg(doc, 'allp_file')

def action(elem, doc):
    """The panflute filter main method, called once per element."""
    if isinstance(elem, (pf.Link, pf.Image)):
        prefix_elem_if_rel_path(elem)
    if isinstance(elem, pf.RawInline) and elem.format == 'html':
        prefix_html(elem)
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
