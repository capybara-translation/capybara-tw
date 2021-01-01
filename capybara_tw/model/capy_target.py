#!/usr/bin/env python3
from __future__ import annotations

from lxml import etree

from capybara_tw.util.xliff_util import State
from capybara_tw.util.xliff_util import Xliff12Tag


class CapyTarget(object):
    text: str
    state: State

    def __init__(self):
        self.text = ''
        self.state = State.NONE

    @classmethod
    def from_element(cls, elem) -> CapyTarget:
        obj = cls()
        obj.text = elem.text or ''
        obj.state = State.create(elem.get('state'))
        return obj

    def to_element(self):
        e = etree.Element(Xliff12Tag.target)
        e.text = self.text
        if self.state != State.NONE:
            e.set('state', self.state.value)
        return e

    def __repr__(self):
        return self.text
