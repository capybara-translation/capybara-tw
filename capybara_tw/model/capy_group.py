#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional, List

from lxml import etree

from capybara_tw.model.capy_context_group import CapyContextGroup
from capybara_tw.model.capy_trans_unit import CapyTransUnit
from capybara_tw.util import xml_util
from capybara_tw.util.xliff_util import CAPYXLF
from capybara_tw.util.xliff_util import Xliff12Tag


class CapyGroup(object):
    id: Optional[str]
    original_id: Optional[str]
    trans_units: List[CapyTransUnit]
    context_group: Optional[CapyContextGroup]

    def __init__(self):
        self.id = None
        self.original_id = None
        self.context_group = None
        self.trans_units = []

    @classmethod
    def from_element(cls, elem) -> CapyGroup:
        obj = cls()
        obj.id = elem.get('id')
        obj.original_id = elem.get(CAPYXLF + 'original-id')
        context_group_elem = xml_util.first(elem, Xliff12Tag.context_group)
        obj.context_group = CapyContextGroup.from_element(context_group_elem)
        obj.trans_units = [CapyTransUnit.from_element(e) for e in elem.iterchildren(Xliff12Tag.trans_unit)]
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.group)
        root.set('id', self.id)
        root.set(CAPYXLF + 'original-id', self.original_id)
        if self.context_group:
            root.append(self.context_group.to_element())
        for tu in self.trans_units:
            root.append(tu.to_element())
        return root
