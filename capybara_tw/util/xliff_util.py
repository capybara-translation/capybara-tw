#!/usr/bin/env python3
from __future__ import annotations
from enum import Enum

from typing import ClassVar

XMLNS = 'http://www.w3.org/XML/1998/namespace'
XML = '{%s}' % XMLNS

XLFNS = 'urn:oasis:names:tc:xliff:document:1.2'
CAPYXLFNS = 'http://capybaratranslation.com/capyxliff/1.0'

XLF = '{%s}' % XLFNS
CAPYXLF = '{%s}' % CAPYXLFNS

TMX14_NS = 'http://www.lisa.org/tmx14'
TMX14 = '{%s}' % TMX14_NS


class Xliff12Tag(object):
    xliff: ClassVar[str] = XLF + 'xliff'
    file: ClassVar[str] = XLF + 'file'
    body: ClassVar[str] = XLF + 'body'
    group: ClassVar[str] = XLF + 'group'
    trans_unit: ClassVar[str] = XLF + 'trans-unit'
    source: ClassVar[str] = XLF + 'source'
    seg_source: ClassVar[str] = XLF + 'seg-source'
    target: ClassVar[str] = XLF + 'target'
    mrk: ClassVar[str] = XLF + 'mrk'
    context_group: ClassVar[str] = XLF + 'context-group'
    context: ClassVar[str] = XLF + 'context'
    alt_trans: ClassVar[str] = XLF + 'alt-trans'


class CapyxliffTag(object):
    source_props: ClassVar[str] = CAPYXLF + 'source-props'
    target_props: ClassVar[str] = CAPYXLF + 'target-props'
    tag: ClassVar[str] = CAPYXLF + 'tag'
    content: ClassVar[str] = CAPYXLF + 'content'


class State(Enum):
    NONE = 'none'
    NEW = 'new'
    TRANSLATED = 'translated'
    SIGNED_OFF = 'signed-off'
    NEEDS_ADAPTATION = 'needs-adaptation'
    NEEDS_L10N = 'needs-l10n'
    NEEDS_REVIEW_ADAPTATION = 'needs-review-adaptation'
    NEEDS_REVIEW_L10N = 'needs-review-l10n'
    NEEDS_REVIEW_TRANSLATION = 'needs-review-translation'
    NEEDS_TRANSLATION = 'needs-translation'
    FINAL = 'final'

    @classmethod
    def create(cls, value: str) -> State:
        for state in State:
            if state.value == value:
                return state
        return State.NONE

    @classmethod
    def create_from_sdl(cls, sdl_value: str) -> State:
        return State.NONE
