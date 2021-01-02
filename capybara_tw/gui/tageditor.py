#!/usr/bin/env python3
import re
from enum import Enum, auto
from typing import Optional
import dataclasses

from PyQt5.QtCore import (Qt, QMimeData, QObject, QSizeF, QRectF, QEvent, pyqtSignal)
from PyQt5.QtGui import (QTextOption, QContextMenuEvent, QTextObjectInterface, QTextFormat, QTextCharFormat,
                         QTextDocument, QFontMetrics, QPainter, QPainterPath, QColor, QBrush, QPen, QKeySequence,
                         QTextCursor, QFocusEvent)
from PyQt5.QtWidgets import (QTextEdit, QApplication)

from capybara_tw.gui.wordboundary import BoundaryHandler
from capybara_tw.model.capy_trans_unit import CapyTransUnit

OBJECT_REPLACEMENT_CHARACTER = 0xfffc
LINE_SEPARATOR = 0x2028
PARAGRAPH_SEPARATOR = 0x2029


class TagKind(Enum):
    START = auto()
    END = auto()
    EMPTY = auto()


class TagTextObject(QObject, QTextObjectInterface):
    type = QTextFormat.UserObject + 1
    name_propid = 10000
    kind_propid = 10001
    content_propid = 10002

    def __init__(self, parent=None):
        super(TagTextObject, self).__init__(parent)
        self.is_expanded = False

    @staticmethod
    def stringify(char_format: QTextCharFormat) -> str:
        name: str = char_format.property(TagTextObject.name_propid)
        kind: TagKind = char_format.property(TagTextObject.kind_propid)
        if kind == TagKind.START:
            return f'{{{name}>'
        if kind == TagKind.END:
            return f'<{name}}}'
        return f'{{{name}}}'

    def intrinsicSize(self, doc: QTextDocument, pos_in_document: int, format_: QTextFormat) -> QSizeF:
        charformat = format_.toCharFormat()
        font = charformat.font()
        fm = QFontMetrics(font)
        tag_kind: TagKind = format_.property(TagTextObject.kind_propid)
        if self.is_expanded and tag_kind in (TagKind.START, TagKind.EMPTY):
            name = format_.property(TagTextObject.name_propid)
            content = format_.property(TagTextObject.content_propid)
            value = f'{name} {content}' if content else name
        else:
            value = format_.property(TagTextObject.name_propid)
        sz = fm.boundingRect(value).size()
        sz.setWidth(sz.width() + 12)
        sz.setHeight(sz.height() + 4)
        return QSizeF(sz)

    def drawObject(self, painter: QPainter, rect: QRectF, doc: QTextDocument, pos_in_document: int,
                   format_: QTextFormat) -> None:
        painter.setRenderHint(QPainter.Antialiasing, True)
        c = QColor(255, 80, 0, 160)
        painter.setBrush(QBrush(c, Qt.SolidPattern))
        painter.setPen(QPen(Qt.white, 2, Qt.SolidLine))
        tag_kind: TagKind = format_.property(TagTextObject.kind_propid)

        top = rect.top()
        left = rect.left()
        width = rect.width()
        height = rect.height()
        square_size = rect.height() / 2

        if tag_kind == TagKind.START:
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            path.addRoundedRect(rect, 10, 10)

            # QRectF(aleft: float, atop: float, awidth: float, aheight: float)
            bottom_left_rect = QRectF(left, top + height - square_size, square_size, square_size)
            path.addRoundedRect(bottom_left_rect, 2, 2)  # Bottom left

            top_left_rect = QRectF(left, top, square_size, square_size)
            path.addRoundedRect(top_left_rect, 2, 2)  # Top left
            painter.drawPath(path.simplified())
        elif tag_kind == TagKind.END:
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            path.addRoundedRect(rect, 10, 10)

            top_right_rect = QRectF((left + width) - square_size, top, square_size, square_size)
            path.addRoundedRect(top_right_rect, 2, 2)  # Top right

            bottom_right_rect = QRectF((left + width) - square_size, top + height - square_size, square_size,
                                       square_size)
            path.addRoundedRect(bottom_right_rect, 2, 2)  # Bottom right
            painter.drawPath(path.simplified())
        else:
            painter.drawRoundedRect(rect, 4, 4)
        if self.is_expanded and tag_kind in (TagKind.START, TagKind.EMPTY):
            tag_name = format_.property(TagTextObject.name_propid)
            tag_content = format_.property(TagTextObject.content_propid)
            text = f'{tag_name} {tag_content}' if tag_content else tag_name
        else:
            text = format_.property(TagTextObject.name_propid)
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignCenter, text)


@dataclasses.dataclass
class TagInfo:
    id: str
    content: str
    kind: TagKind


class TagEditor(QTextEdit):
    start_tags = re.compile(r'({[biu_^]+?>|{[0-9]{1,2}>)')
    end_tags = re.compile(r'(<[biu_^]+?\}|<[0-9]{1,2}\})')
    empty_tags = re.compile(r'({[0-9]{1,2}\}|{j\})')
    all_tags = re.compile(r'({[biu_^]+?>|<[biu_^]+?\}|{[0-9]{1,2}>|<[0-9]{1,2}\}|{[0-9]{1,2}\}|{j\})')

    focusedIn = pyqtSignal(bool)
    segmentEdited = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tu: Optional[CapyTransUnit] = None
        self.setAcceptRichText(False)

        self.key_event_filter = KeyEventFilter()
        self.key_event_filter.install_to(self)
        self.mouse_event_filter = BoundaryHandler()
        self.mouse_event_filter.install_textedit(self)

        # Register tag object handler
        self.tag_object_handler = TagTextObject(self)
        document_layout = self.document().documentLayout()
        document_layout.registerHandler(TagTextObject.type, self.tag_object_handler)

        self.textChanged.connect(self.__on_text_changed)

    @property
    def is_source(self) -> bool:
        """Indicates which of the source and target segments this editor handles.

        Returns: True to handle source segment, otherwise target segment.

        """
        name = self.objectName()
        if name == 'srcEditor':
            return True
        if name == 'tgtEditor':
            return False
        raise AttributeError('No ''is_source'' attribute')

    def initialize(self, tu: CapyTransUnit) -> None:
        """Initializes the editor with tu. Called when the selected segment has been changed on TranslationGrid.

        Args:
            tu: Translation unit
        """
        blocked = self.blockSignals(True)
        self.tu = tu
        text = tu.source.text if self.is_source else tu.target.text
        self.setText('')
        self.insert_content(text or '')
        self.setFocus()
        self.document().clearUndoRedoStacks()
        self.blockSignals(blocked)

    def focusInEvent(self, e: QFocusEvent) -> None:
        super(TagEditor, self).focusInEvent(e)
        self.focusedIn.emit(True)

    def focusOutEvent(self, e: QFocusEvent) -> None:
        super(TagEditor, self).focusOutEvent(e)
        self.focusedIn.emit(False)

    def display_hidden_characters(self, display=False):
        option = QTextOption()
        if display:
            option.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
        self.document().setDefaultTextOption(option)

    def insert_content(self, text: str) -> None:
        cursor = self.textCursor()
        for run in self.all_tags.split(text):
            tag = self.__get_tag_info(run, from_source=self.is_source)
            if tag:
                self.insert_tag(cursor, tag.id, tag.content, tag.kind)
            else:
                run = run.replace('\r\n', '\n').replace('\r', '\n')
                run = run.replace('\n', '<br/>')
                cursor.insertHtml(f'<span style="white-space: pre;">{run}</span>')

    def set_readonly_with_text_selectable(self):
        self.setReadOnly(True)
        self.setTextInteractionFlags(self.textInteractionFlags() | Qt.TextSelectableByKeyboard)

    @staticmethod
    def insert_tag(cursor: QTextCursor, name: str, content: str, kind: TagKind) -> None:
        """Inserts a tag object at the cursor position.

        Args:
            cursor: A QTextCursor object.
            name: Tag name ("b|i|u|^|_|j" for builtin tags, an id for non-builtin tags)
            content: Tag content for non-builtin tags. Empty string for builtin tags.
            kind: Tag kind
        """
        char_format = QTextCharFormat()
        char_format.setProperty(TagTextObject.name_propid, name)
        char_format.setProperty(TagTextObject.kind_propid, kind)
        char_format.setProperty(TagTextObject.content_propid, content)
        char_format.setToolTip(content)
        char_format.setObjectType(TagTextObject.type)
        char_format.setVerticalAlignment(QTextCharFormat.AlignTop)
        cursor.insertText(chr(OBJECT_REPLACEMENT_CHARACTER), char_format)

    def __get_tag_info(self, run: str, from_source: bool) -> Optional[TagInfo]:
        """Converts a tag string ("{1>", "<1}", "{1}", etc.) into a TagInfo Object containing a tag id, kind, content.
        The content will be retrieved from source or target props in the translation unit,
        so from_source argument needs to be supplied to determine which of source and target props to retrieve from.

        Args:
            run: A tag string ("{1>", "<1}", "{1}", etc.)
            from_source: True to retrieve content from source props. False from target props.

        Returns: A TagInfo object

        """
        if self.start_tags.search(run):
            tag_id = run.strip('{>')
            kind = TagKind.START
            capytag = self.tu.find_tag_by_id(tag_id, from_source)
        elif self.end_tags.search(run):
            tag_id = run.strip('<}')
            kind = TagKind.END
            capytag = self.tu.find_tag_by_id(tag_id, from_source)
        elif self.empty_tags.search(run):
            tag_id = run.strip('{}')
            kind = TagKind.EMPTY
            capytag = self.tu.find_tag_by_id(tag_id, from_source)
        else:
            return None
        # Non-builtin tags (tags other than b|i|u|_|^|j) should have content, otherwise empty string
        content = capytag.content.value if capytag else ''
        return TagInfo(id=tag_id, kind=kind, content=content)

    def __get_next_tag(self) -> Optional[TagInfo]:
        """Retrieves the first one from the tags that exist in source but not in target.

        Returns: A TagInfo object
        """
        src_tags = self.all_tags.findall(self.tu.source.text)
        content = self.to_model_data()
        tgt_tags = self.all_tags.findall(content)
        for src_tag in src_tags:
            src_count = src_tags.count(src_tag)
            tgt_count = tgt_tags.count(src_tag)
            if src_count > tgt_count:
                return self.__get_tag_info(src_tag, from_source=True)
        return None

    def copy_tag_from_source(self) -> None:
        """Copies a tag from source to target.
        """
        if not self.hasFocus():
            return
        cursor = self.textCursor()
        tag = self.__get_next_tag()
        if not tag:
            return
        if cursor.hasSelection():
            if tag.kind == TagKind.EMPTY:
                return
            # Surround the selection with the tag pair.
            start = cursor.selectionStart()
            end = cursor.selectionEnd() + 1
            cursor.setPosition(start)
            self.insert_tag(cursor, tag.id, tag.content, TagKind.START)
            cursor.setPosition(end)
            self.insert_tag(cursor, tag.id, tag.content, TagKind.END)
            cursor.clearSelection()
            self.setTextCursor(cursor)
        else:
            # insert the tag at the current position.
            self.insert_tag(cursor, tag.id, tag.content, tag.kind)

        # Write back the copied tag to the target tag list if it's a non-builtin tag
        if tag.content:
            self.tu.add_tag(tag.id, tag.content, to_source=False)

    def contains_tag_str(self):
        return self.all_tags.search(self.to_model_data()) is not None

    def __on_text_changed(self):
        self.segmentEdited.emit(self.to_model_data())

    def contextMenuEvent(self, e: QContextMenuEvent) -> None:
        menu = self.createStandardContextMenu()
        for a in menu.actions():
            if a.objectName() in ('edit-undo', 'edit-redo'):
                menu.removeAction(a)
        menu.exec_(e.globalPos())

    def canInsertFromMimeData(self, source: QMimeData) -> bool:
        return source.hasText()

    def insertFromMimeData(self, source: QMimeData) -> None:
        if source.hasText():
            text = source.text().replace(chr(0xa), chr(LINE_SEPARATOR))
            self.insert_content(text)
            # super().insertPlainText(text)

    # Called when a drag and drop operation is started, or when data is copied to the clipboard.
    def createMimeDataFromSelection(self) -> QMimeData:
        mime = QMimeData()
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return mime
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        selected_text = self.to_model_data_in_range(start_pos, end_pos)
        mime.setText(selected_text)
        return mime

    def to_model_data_in_range(self, start: int, end: int) -> str:
        """ Converts the specified range of editor content into model data.

        Args:
            start: start position of the range
            end: end position of the range

        Returns:
            A model data string within the specified range.
            For example:

            an {2>apple<2} on the {b>table<b}
        """
        doc = self.document()
        substrings = []
        for pos in range(start, end):
            char = doc.characterAt(pos)
            if ord(char) == OBJECT_REPLACEMENT_CHARACTER:
                current_block = doc.findBlock(pos)

                # iterate text fragments within the block
                it = current_block.begin()
                while not it.atEnd():
                    current_fragment = it.fragment()
                    # check if the current position is located within the fragment
                    if current_fragment.contains(pos):
                        char_format = current_fragment.charFormat()
                        substrings.append(TagTextObject.stringify(char_format))
                        break
                    it += 1
            elif ord(char) in (LINE_SEPARATOR, PARAGRAPH_SEPARATOR):
                substrings.append('\n')
            else:
                substrings.append(char)
        text = ''.join(substrings)
        return text

    def to_model_data(self) -> str:
        """ Converts editor content to model data.

        Returns:
            A model data string containing tags that have been converted back from tag objects.
            For example:

            {1} There is an {2>apple<2} on the {b>table<b} that I bought {3>yesterday<3}.
        """
        start_pos = 0
        end_pos = self.document().characterCount() - 1  # subtract len of paragraph separator at the end
        text = self.to_model_data_in_range(start_pos, end_pos)
        return text

    def expand_tags(self, is_expanded: bool):
        """ Expands or collapses tags.

        Args:
            is_expanded: True to expand.
        """
        self.tag_object_handler.is_expanded = is_expanded
        self.viewport().update()
        # Need to reset wrap mode...
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setLineWrapMode(QTextEdit.WidgetWidth)


class KeyEventFilter(QObject):
    def __init__(self):
        super().__init__()
        self.widget = None

    def install_to(self, widget) -> None:
        self.widget = widget
        self.widget.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj == self.widget and event.type() == QEvent.KeyPress:
            modifiers = QApplication.keyboardModifiers()
            key = event.key()
            if modifiers != Qt.ShiftModifier and key == Qt.Key_Return:
                return True
            if modifiers != (Qt.ShiftModifier | Qt.KeypadModifier) and key == Qt.Key_Enter:
                return True
            if QKeySequence(modifiers | key).matches(QKeySequence.Undo):
                # TODO: handle right-click undo
                print('undo')

        return QObject.eventFilter(self, obj, event)
