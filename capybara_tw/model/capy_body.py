#!/usr/bin/env python3
from __future__ import annotations


from typing import List

from lxml import etree

from capybara_tw.model.capy_group import CapyGroup
from capybara_tw.util.xliff_util import Xliff12Tag


class CapyBody(object):
    groups: List[CapyGroup]

    def __init__(self):
        self.groups = []

    @classmethod
    def from_element(cls, elem) -> CapyBody:
        obj = cls()
        obj.groups = [CapyGroup.from_element(e) for e in elem.iterchildren(Xliff12Tag.group)]
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.body)
        for group in self.groups:
            root.append(group.to_element())
        return root
