#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from lxml import etree

from capybara_tw.model.capy_content import CapyContent
from capybara_tw.util import xml_util
from capybara_tw.util.xliff_util import CapyxliffTag


class CapyTag(object):
    id: Optional[str]
    content: Optional[CapyContent]

    def __init__(self):
        self.id = None
        self.content = None

    @classmethod
    def from_element(cls, elem) -> CapyTag:
        obj = cls()
        obj.id = elem.get('id')
        content_elem = xml_util.first(elem, CapyxliffTag.content)
        obj.content = CapyContent.from_element(content_elem)
        return obj

    def to_element(self):
        root = etree.Element(CapyxliffTag.tag)
        root.set('id', self.id)
        root.append(self.content.to_element())
        return root

    def __repr__(self):
        return f'{{{self.id}}} {self.content}'
