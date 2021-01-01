#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from lxml import etree

from capybara_tw.util.xliff_util import Xliff12Tag


class CapyContext(object):
    context_type: Optional[str]
    value: str

    def __init__(self):
        self.value = ''
        self.context_type = None

    @classmethod
    def from_element(cls, elem) -> CapyContext:
        obj = cls()
        obj.context_type = elem.get('context-type')
        obj.value = elem.text or ''
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.context)
        root.set('context-type', self.context_type)
        root.text = self.value
        return root
