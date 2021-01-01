#!/usr/bin/env python3
from __future__ import annotations

from lxml import etree

from capybara_tw.util.xliff_util import CapyxliffTag


class CapyContent(object):
    value: str

    def __init__(self):
        self.value = ''

    @classmethod
    def from_element(cls, elem) -> CapyContent:
        obj = cls()
        obj.value = elem.text or ''
        return obj

    def to_element(self):
        root = etree.Element(CapyxliffTag.content)
        root.text = self.value
        return root

    def __repr__(self):
        return self.value
