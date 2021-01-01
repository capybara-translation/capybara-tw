#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional, List

from lxml import etree

from capybara_tw.model.capy_context import CapyContext
from capybara_tw.util.xliff_util import Xliff12Tag


class CapyContextGroup(object):
    contexts: List[CapyContext]

    def __init__(self):
        self.contexts = []

    @classmethod
    def from_element(cls, elem) -> Optional[CapyContextGroup]:
        if elem is None:
            return None
        obj = cls()
        obj.contexts = [CapyContext.from_element(e) for e in elem.iterchildren(Xliff12Tag.context)]
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.context_group)
        for context in self.contexts:
            root.append(context.to_element())
        return root
