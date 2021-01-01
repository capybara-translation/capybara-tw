#!/usr/bin/env python3
import os
import re
from typing import Callable, Optional, Any

from lxml import etree


def get_parser(xml_file: str, encoding: Optional[str] = None) -> etree.XMLParser:
    size_mb = os.path.getsize(xml_file) / 1000000
    if size_mb > 9:
        parser = etree.XMLParser(huge_tree=True, encoding=encoding)
    else:
        parser = etree.XMLParser(encoding=encoding)
    return parser


def remove_invalid_chars(chars: str) -> str:
    if not chars:
        return ''
    return re.sub(r'&#x.+?;', ' ', chars, flags=re.IGNORECASE)


def remove_outer_tags(xml: str) -> str:
    return re.sub(r'(^<[^<>]*?/?>)|(</[^<>]*?>$)', '', xml)


def tostring(elem) -> str:
    xml = etree.tostring(elem, encoding='unicode', with_tail=False)
    return remove_outer_tags(xml)


def first(elem, tag: Optional[str] = None,
          predicate: Optional[Callable[[Any], bool]] = None) -> Any:
    if predicate:
        for e in elem.iterchildren(tag):
            if predicate(e):
                return e
        return None

    for e in elem.iterchildren(tag):
        return e
    return None


def first_sibling(elem, tag: Optional[str] = None,
                  preceding: bool = False,
                  predicate: Optional[Callable[[Any], bool]] = None) -> Any:
    if predicate:
        for e in elem.itersiblings(tag=tag, preceding=preceding):
            if predicate(e):
                return e
        return None

    for e in elem.itersiblings(tag=tag, preceding=preceding):
        return e
    return None
