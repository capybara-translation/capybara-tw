#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from lxml import etree

from capybara_tw.model.capy_target import CapyTarget
from capybara_tw.util import xml_util
from capybara_tw.util.xliff_util import Xliff12Tag


class CapyAltTrans(object):
    origin: Optional[str]
    target: Optional[CapyTarget]

    def __init__(self):
        self.origin = None
        self.target = None

    @classmethod
    def from_element(cls, elem) -> CapyAltTrans:
        obj = cls()
        obj.origin = elem.get('origin')
        target_elem = xml_util.first(elem, Xliff12Tag.target)
        obj.target = CapyTarget.from_element(target_elem)
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.alt_trans)
        root.set('origin', self.origin)
        root.append(self.target.to_element())
        return root
