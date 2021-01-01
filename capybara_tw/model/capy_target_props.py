#!/usr/bin/env python3
from __future__ import annotations

from typing import List

from lxml import etree

from capybara_tw.model.capy_tag import CapyTag
from capybara_tw.util.xliff_util import CapyxliffTag


class CapyTargetProps(object):
    tags: List[CapyTag]

    def __init__(self):
        self.tags = []

    @classmethod
    def from_element(cls, elem) -> CapyTargetProps:
        obj = cls()
        obj.tags = [CapyTag.from_element(e) for e in elem.iterchildren(CapyxliffTag.tag)]
        return obj

    def to_element(self):
        root = etree.Element(CapyxliffTag.target_props)
        for tag in self.tags:
            root.append(tag.to_element())
        return root
