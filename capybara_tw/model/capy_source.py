#!/usr/bin/env python3
from __future__ import annotations

from lxml import etree

from capybara_tw.util.xliff_util import Xliff12Tag


class CapySource(object):
    text: str

    def __init__(self):
        self.text = ''

    @classmethod
    def from_element(cls, elem) -> CapySource:
        obj = cls()
        obj.text = elem.text or ''
        return obj

    def to_element(self):
        e = etree.Element(Xliff12Tag.source)
        e.text = self.text
        return e

    def __repr__(self):
        return self.text
