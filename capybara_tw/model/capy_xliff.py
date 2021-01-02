#!/usr/bin/env python3
from __future__ import annotations

from typing import List

from lxml import etree

from capybara_tw.model.capy_file import CapyFile
from capybara_tw.model.capy_trans_unit import CapyTransUnit
from capybara_tw.util import xml_util
from capybara_tw.util.xliff_util import XLFNS, CAPYXLFNS, CAPYXLF, Xliff12Tag


class CapyXliff(object):
    version: str
    capy_version: str
    files: List[CapyFile]

    def __init__(self):
        self.version = '1.2'
        self.capy_version = '1.0'
        self.files = []

    @property
    def source_language(self) -> str:
        if self.files:
            return self.files[0].source_language
        return ''

    @property
    def target_language(self) -> str:
        if self.files:
            return self.files[0].target_language
        return ''

    @classmethod
    def from_element(cls, elem) -> CapyXliff:
        obj = cls()
        obj.version = elem.get('version')
        obj.capy_version = elem.get(CAPYXLF + 'version')
        obj.files = [CapyFile.from_element(e) for e in elem.iterchildren(Xliff12Tag.file)]
        return obj

    @classmethod
    def load(cls, file: str) -> CapyXliff:
        parser = xml_util.get_parser(file)
        root = etree.parse(file, parser=parser).getroot()
        return cls.from_element(root)

    def to_element(self):
        root = etree.Element(Xliff12Tag.xliff, nsmap={None: XLFNS, 'capy': CAPYXLFNS})
        root.set('version', self.version)
        root.set(CAPYXLF + 'version', self.capy_version)
        for file in self.files:
            root.append(file.to_element())
        return root

    def save(self, destination: str) -> None:
        root = self.to_element()
        content = etree.tostring(root, xml_declaration=True, encoding='utf-8', pretty_print=True)
        with open(destination, 'wb') as outfile:
            outfile.write(content)

    def get_all_trans_units(self) -> List[CapyTransUnit]:
        tus = []
        for file in self.files:
            for group in file.body.groups:
                tus.extend(group.trans_units)
        return tus
