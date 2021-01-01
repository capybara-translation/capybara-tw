#!/usr/bin/env python3
from __future__ import annotations

from typing import List, Optional

from lxml import etree

from capybara_tw.model.capy_alt_trans import CapyAltTrans
from capybara_tw.model.capy_source import CapySource
from capybara_tw.model.capy_target import CapyTarget
from capybara_tw.model.capy_source_props import CapySourceProps
from capybara_tw.model.capy_target_props import CapyTargetProps
from capybara_tw.util.xliff_util import CapyxliffTag, CAPYXLF, Xliff12Tag
from capybara_tw.util import xml_util


class CapyTransUnit(object):
    id: Optional[str]
    original_id: Optional[str]
    source: Optional[CapySource]
    target: Optional[CapyTarget]
    alt_translations: List[CapyAltTrans]
    translate: bool
    capy_source_props: Optional[CapySourceProps]
    capy_target_props: Optional[CapyTargetProps]

    def __init__(self):
        self.id = None
        self.original_id = None
        self.source = None
        self.target = None
        self.alt_translations = []
        self.translate = True
        self.capy_source_props = None
        self.capy_target_props = None

    @classmethod
    def from_element(cls, elem) -> CapyTransUnit:
        obj = cls()
        obj.translate = elem.get('translate', 'yes') == 'yes'
        obj.id = elem.get('id')
        obj.original_id = elem.get(CAPYXLF + 'original-id')
        source_elem = xml_util.first(elem, Xliff12Tag.source)
        obj.source = CapySource.from_element(source_elem)
        target_elem = xml_util.first(elem, Xliff12Tag.target)
        obj.target = CapyTarget.from_element(target_elem)
        obj.alt_translations = [CapyAltTrans.from_element(e) for e in elem.iterchildren(Xliff12Tag.alt_trans)]
        source_props_elem = xml_util.first(elem, CapyxliffTag.source_props)
        obj.capy_source_props = CapySourceProps.from_element(source_props_elem)
        target_props_elem = xml_util.first(elem, CapyxliffTag.target_props)
        obj.capy_target_props = CapyTargetProps.from_element(target_props_elem)
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.trans_unit)
        root.set('id', self.id)
        root.set(CAPYXLF + 'original-id', self.original_id)
        root.set('translate', 'yes' if self.translate else 'no')
        root.append(self.source.to_element())
        root.append(self.target.to_element())
        for alt_trans in self.alt_translations:
            root.append(alt_trans.to_element())
        root.append(self.capy_source_props.to_element())
        root.append(self.capy_target_props.to_element())
        return root

    def __repr__(self):
        return f'{self.source} | {self.target}'
