#!/usr/bin/env python3
import re
from enum import Enum, auto
from typing import Optional, Tuple

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
    content_propId = 10002

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
        tag_name = format_.property(TagTextObject.name_propid)
        sz = fm.boundingRect(tag_name).size()
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
        tag_name = format_.property(TagTextObject.name_propid)
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignCenter, tag_name)


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

        self.__register_tag_type()
        self.textChanged.connect(self.__on_text_changed)

    @property
    def is_source(self) -> bool:
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
            tag_id, tag_kind = self.__get_tag_info(run)
            if tag_id:
                self.insert_tag(cursor, tag_id, tag_id, tag_kind)
            else:
                run = run.replace('\r\n', '\n').replace('\r', '\n')
                run = run.replace('\n', '<br/>')
                cursor.insertHtml(f'<span style="white-space: pre;">{run}</span>')

    def set_readonly_with_text_selectable(self):
        self.setReadOnly(True)
        self.setTextInteractionFlags(self.textInteractionFlags() | Qt.TextSelectableByKeyboard)

    def __register_tag_type(self) -> None:
        document_layout = self.document().documentLayout()
        document_layout.registerHandler(TagTextObject.type, TagTextObject(self))

    @staticmethod
    def insert_tag(cursor: QTextCursor, name: str, content: str, kind: TagKind) -> None:
        char_format = QTextCharFormat()
        char_format.setProperty(TagTextObject.name_propid, name)
        char_format.setProperty(TagTextObject.kind_propid, kind)
        char_format.setToolTip(content)
        char_format.setObjectType(TagTextObject.type)
        char_format.setVerticalAlignment(QTextCharFormat.AlignTop)
        cursor.insertText(chr(OBJECT_REPLACEMENT_CHARACTER), char_format)

    def __get_tag_info(self, run: str) -> Tuple[Optional[str], Optional[TagKind]]:
        if self.start_tags.search(run):
            return run.strip('{>'), TagKind.START
        elif self.end_tags.search(run):
            return run.strip('<}'), TagKind.END
        elif self.empty_tags.search(run):
            return run.strip('{}'), TagKind.EMPTY
        else:
            return None, None

    def __get_next_tag(self) -> Optional[str]:
        src_tags = self.all_tags.findall(self.tu.source.text)
        content = self.to_model_data()
        tgt_tags = self.all_tags.findall(content)
        for src_tag in src_tags:
            src_count = src_tags.count(src_tag)
            tgt_count = tgt_tags.count(src_tag)
            if src_count > tgt_count:
                return src_tag
        return None

    def copy_tag_from_source(self) -> None:
        if not self.hasFocus():
            return
        cursor = self.textCursor()
        tag = self.__get_next_tag()
        if not tag:
            return
        tag_id, kind = self.__get_tag_info(tag)
        if cursor.hasSelection():
            if kind == TagKind.EMPTY:
                return
            # Surround the selection with the tag pair.
            start = cursor.selectionStart()
            end = cursor.selectionEnd() + 1
            cursor.setPosition(start)
            self.insert_tag(cursor, tag_id, tag_id, TagKind.START)
            cursor.setPosition(end)
            self.insert_tag(cursor, tag_id, tag_id, TagKind.END)
            cursor.clearSelection()
            self.setTextCursor(cursor)
        else:
            # insert the tag at the current position.
            self.insert_tag(cursor, tag_id, tag_id, kind)

    def contains_tag_str(self):
        return self.all_tags.search(self.toPlainText()) is not None

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
