#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from lxml import etree

from capybara_tw.model.capy_body import CapyBody
from capybara_tw.util import xml_util
from capybara_tw.util.xliff_util import Xliff12Tag


class CapyFile(object):
    body: Optional[CapyBody]
    original: Optional[str]
    source_language: Optional[str]
    target_language: Optional[str]
    datatype: Optional[str]

    def __init__(self):
        self.body = None
        self.original = None
        self.source_language = None
        self.target_language = None
        self.datatype = None

    @classmethod
    def from_element(cls, elem) -> CapyFile:
        obj = cls()
        obj.original = elem.get('original')
        obj.source_language = elem.get('source-language')
        obj.target_language = elem.get('target-language')
        obj.datatype = elem.get('datatype')
        obj.body = CapyBody.from_element(xml_util.first(elem, Xliff12Tag.body))
        return obj

    def to_element(self):
        root = etree.Element(Xliff12Tag.file)
        root.set('original', self.original)
        root.set('source-language', self.source_language)
        root.set('target-language', self.target_language)
        root.set('datatype', self.datatype)
        root.append(self.body.to_element())
        return root
