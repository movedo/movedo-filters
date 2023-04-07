#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Robin Vobruba <hoijui.quaero@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This is part of the [MoVeDo](https://github.com/movedo) project.
See LICENSE.md for copyright information.

Extracts (prints out) link and image paths/URLs,
both the native (e.g. Markdown) and HTML formatted ones.

Example:

```
[l-name](../some/more/here.txt)
[l2-name](https://www.example.com/sub/path/here.html#some-anchor)
![img-text](https://www.example.com/sub/path/img.png)

<a href="https://www.example.com/sub/path/here.html#some-other-anchor">l3-name</a>
<img src="https://www.example.com/sub/path/img.png"/>
```

->

```
input.md:1:link:../some/more/here.txt
input.md:2:link:https://www.example.com/sub/path/here.html#some-anchor
input.md:3:image:https://www.example.com/sub/path/img.png
input.md:5:link-html:https://www.example.com/sub/path/here.html#some-other-anchor
input.md:6:image-html:https://www.example.com/sub/path/img.png
```

It is implemented as a Pandoc filter using panflute.

This might typicaly be used as an intermediate step
when combining a multitude of documents found within a directory tree
into a single document at the directory trees root.
Or more pracitcally: when creating a single PDF
out of a bunch of Markdown or HTML files scatered around the filesystem.

Usage example:
$ pandoc -f markdown -t markdown --markdown-headings=atx \
        -M elaa_doc_path="dir/to/input.md" \
        -M elaa_links_file="all-links.txt" \
        -M elaa_anchors_file="all-anchors.txt" \
        --filter extract_links_and_anchors.py \
        -o "other-dir/to/output.md" \
        "dir/to/input.md"
"""

# HACK for panflute on python 2
#      -> DEPRECATED, Python 2 is not supported anymore by panflute anyway
#from __future__ import unicode_literals

from _common import check_version, is_url, get_arg
check_version()

import panflute as pf
# TODO Instead of bs4/BeautifulSoup for parsing HTML, use pandoc itsself - panflute has functions for that, see its docu
from bs4 import BeautifulSoup

# parameters
# should be something like 'some/static/prefix/file-name.md'
doc_path = '<default-file-path>'
links_file = None
lfh = None
anchors_file = None
afh = None
line_num = 1
LNKTYP_LINK = 'link'
LNKTYP_IMAGE = 'image'
LNKTYP_LINK_HTML = 'link-html'
LNKTYP_IMAGE_HTML = 'image-html'
ANKTYP_NATIVE = 'anchor'
ANKTYP_HTML_NAME = 'anchor-html-name'
ANKTYP_HTML_ID = 'anchor-html-id'

def extract_link(link, l_type):
    """Output all the details of a link."""
    global doc_path, line_num, lfh
    #if link[0] == '#':
    #    link = doc_path + link
    lfh.write('%s:%s:%s:%s\n' % (doc_path, line_num, l_type, link))

def extract_anchor(anchor, a_type):
    """Output all the details of an anchor."""
    global doc_path, line_num, afh
    afh.write('%s:%s:%s:%s\n' % (doc_path, line_num, a_type, anchor))

def extract_html_elements(elem):
    """Extracts all a.href, a.name, a.id and img.src in a piece of HTML."""
    global lfh, afh
    parsed = BeautifulSoup(elem.text, 'html.parser')
    if lfh is not None:
        # Extract links
        anchors_with_href = parsed.findAll(
            lambda tag:
            tag.name == "a" and tag.get("href") is not None)
        for anchor in anchors_with_href:
            extract_link(anchor.get("href"), LNKTYP_LINK_HTML)
        # Extract images
        imgs_with_src = parsed.findAll(
            lambda tag:
            tag.name == "img" and tag.get("src") is not None)
        for img in imgs_with_src:
            extract_link(img.get("src"), LNKTYP_IMAGE_HTML)
    if afh is not None:
        # Extract name-anchors (References/Identifiers)
        anchors_with_name = parsed.findAll(
            lambda tag:
            tag.name == "a" and tag.get("name") is not None)
        for anchor in anchors_with_name:
            extract_anchor(anchor.get("name"), ANKTYP_HTML_NAME)
        # Extract id-anchors (References/Identifiers)
        elements_with_id = parsed.findAll(
            lambda tag:
            tag.get("id") is not None)
        for elements in elements_with_id:
            extract_anchor(anchor.get("id"), ANKTYP_HTML_ID)

def register_line_break():
    """Increases the line-counter by one."""
    global line_num
    line_num = line_num + 1
    #pf.debug('line num: %d' % line_num)

def extract_native_link(elem):
    """Extracts a native link."""
    extract_link(elem.url, LNKTYP_LINK)

def extract_native_image(elem):
    """Extracts a native image."""
    extract_link(elem.url, LNKTYP_IMAGE)

def extract_anchor_elem(elem):
    """Extracts a native format anchor."""
    extract_anchor(elem.identifier, ANKTYP_NATIVE)

def prepare(doc):
    """The panflute filter init method."""
    global doc_path, links_file, lfh, anchors_file, afh
    doc_path = get_arg(doc, 'elaa_doc_path')
    links_file = get_arg(doc, 'elaa_links_file')
    anchors_file = get_arg(doc, 'elaa_anchors_file')
    if links_file is None or links_file == '':
        lfh = None
    else:
        lfh = open(links_file, "a")
    if anchors_file is None or anchors_file == '':
        afh = None
    else:
        afh = open(anchors_file, "a")

def action(elem, _doc):
    """The panflute filter main method, called once per element."""
    if isinstance(elem, (pf.LineBreak, pf.LineItem, pf.SoftBreak, pf.Para)):
        register_line_break()
    elif isinstance(elem, pf.Link):
        if lfh is not None:
            extract_native_link(elem)
    elif isinstance(elem, pf.Image):
        if lfh is not None:
            extract_native_image(elem)
    elif isinstance(elem, pf.RawInline) and elem.format == 'html':
        #extract_html_elements(elem)
        inner_doc = pf.convert_text(text=elem.text, input_format=elem.format, output_format='panflute', standalone=True)
        pf.run_filter(action, doc=inner_doc)
        pf.debug('XXX %s' % elem.text)
    #if hasattr(elem, 'text') and elem.text != '':
    #    pf.debug('%s: "%s"' % (type(elem), elem.text))
    #if hasattr(elem, 'text') and elem.text != '' and elem.text == '↩':
    #if hasattr(elem, 'text') and elem.text != '' and elem.text == '\n':
    #    register_line_break()
    if hasattr(elem, 'identifier') and elem.identifier != '':
        if afh is not None:
            extract_anchor_elem(elem)
    return elem

def finalize(_doc):
    """The panflute filter "destructor" method."""
    global lfh, afh
    if lfh is not None:
        lfh.close()
    if afh is not None:
        afh.close()

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
