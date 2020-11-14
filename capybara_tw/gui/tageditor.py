#!/usr/bin/env python3
import re
from enum import Enum, auto
from PyQt5.QtGui import (QTextOption, QContextMenuEvent, QTextObjectInterface, QTextFormat, QTextCharFormat,
                         QTextDocument, QFontMetrics, QPainter, QPainterPath, QColor, QBrush, QPen, QKeySequence,
                         QTextCursor)
from PyQt5.QtWidgets import (QTextEdit, QApplication)
from PyQt5.QtCore import (Qt, QMimeData, QObject, QSizeF, QRectF, QEvent, QRegExp, pyqtSignal)
from capybara_tw.gui.wordboundary import BoundaryHandler

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

    segmentEdited = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_undoing = False
        self.setAcceptRichText(False)
        # self.setUndoRedoEnabled(False)

        self.key_event_filter = KeyEventFilter()
        self.key_event_filter.install_to(self)
        self.mouse_event_filter = BoundaryHandler()
        self.mouse_event_filter.install_textedit(self)

        self.__register_tag_type()
        self.textChanged.connect(self.__on_text_changed)

    def display_hidden_characters(self, display=False):
        option = QTextOption()
        if display:
            option.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
        self.document().setDefaultTextOption(option)

    def initialize(self, text):
        text = text or ''
        self.setText('')
        cursor = self.textCursor()
        for run in self.all_tags.split(text):
            if self.start_tags.search(run):
                name = run.strip('{>')
                self.insert_tag(cursor, name, name, TagKind.START)
            elif self.end_tags.search(run):
                name = run.strip('<}')
                self.insert_tag(cursor, name, name, TagKind.END)
            elif self.empty_tags.search(run):
                name = run.strip('{}')
                self.insert_tag(cursor, name, name, TagKind.EMPTY)
            else:
                run = run.replace('\r\n', '\n').replace('\r', '\n')
                run = run.replace('\n', '<br/>')
                cursor.insertHtml(f'<span>{run}</span>')
        self.document().clearUndoRedoStacks()

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

    def __on_text_changed(self):
        if self.is_undoing:
            self.is_undoing = False
            return
        blocked = self.blockSignals(True)
        self.textCursor().beginEditBlock()
        doc = self.document()
        pattern = QRegExp(r'\{\d{1,2}\}|\{\d{1,2}>|<\d{1,2}\}|\{j\}|\{[biu_^]+>|<[biu_^]+\}')
        pattern.setMinimal(True)
        cursor = QTextCursor(doc)
        while True:
            cursor = doc.find(pattern, cursor)
            if cursor.isNull():
                break
            matched_str = cursor.selectedText()
            if matched_str.endswith('>'):
                tag_name = cursor.selectedText().strip('{>')
                self.insert_tag(cursor, tag_name, tag_name, TagKind.START)
            elif matched_str.startswith('<'):
                tag_name = cursor.selectedText().strip('<}')
                self.insert_tag(cursor, tag_name, tag_name, TagKind.END)
            elif matched_str.startswith('{'):
                tag_name = cursor.selectedText().strip('{}')
                self.insert_tag(cursor, tag_name, tag_name, TagKind.EMPTY)

        self.textCursor().endEditBlock()
        self.blockSignals(blocked)
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
            super().insertPlainText(text)

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
        start_pos = 0
        end_pos = len(self.document().toPlainText())
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
                self.widget.is_undoing = True

        return QObject.eventFilter(self, obj, event)
