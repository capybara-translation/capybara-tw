#!/usr/bin/env python3
import re
from PyQt5.QtWidgets import (QStyledItemDelegate, QWidget, QStyleOptionViewItem, QApplication, QStyle)
from PyQt5.QtCore import (Qt, QModelIndex, QAbstractItemModel, QRectF, QPointF, QSizeF, QSize)
from PyQt5.QtGui import (QPainter, QTextDocument, QTextCursor, QTextOption)

from capybara_tw.gui.tageditor import (TagEditor, TagKind, TagTextObject)


class TagEditorDelegate(QStyledItemDelegate):
    source_column = 0
    target_column = 1
    start_tags = re.compile(r'({[biu_^]+?>|{[0-9]{1,2}>)')
    end_tags = re.compile(r'(<[biu_^]+?\}|<[0-9]{1,2}\})')
    empty_tags = re.compile(r'({[0-9]{1,2}\}|{j\})')
    all_tags = re.compile(r'({[biu_^]+?>|<[biu_^]+?\}|{[0-9]{1,2}>|<[0-9]{1,2}\}|{[0-9]{1,2}\}|{j\})')

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        print('createEditor')
        tageditor = TagEditor(parent)
        tageditor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return tageditor

    # def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
    #     size_hint = editor.sizeHint()
    #     if option.rect.width() < size_hint.width():
    #         option.rect.setWidth(size_hint.width())
    #     if option.rect.height() < size_hint.height():
    #         option.rect.setHeight(size_hint.height())
    #     editor.setGeometry(option.rect)

    # def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
    #     painter.save()
    #     opt = QStyleOptionViewItem(option)
    #     self.initStyleOption(opt, index)
    #
    #     doc = QTextDocument(self)
    #     text_opt = QTextOption()
    #     text_opt.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
    #     # text_opt.setWrapMode(QTextOption.WordWrap)
    #     doc.setDefaultTextOption(text_opt)
    #     doc_layout = doc.documentLayout()
    #     doc_layout.registerHandler(TagTextObject.type, TagTextObject(self))
    #     cursor = QTextCursor(doc)
    #     self.__init_editor_data(cursor, opt.text)
    #
    #     style = QApplication.style() if opt.widget is None else opt.widget.style()
    #     # Painting item without text
    #     doc.setTextWidth(opt.rect.width())
    #     opt.text = ''
    #     style.drawControl(QStyle.CE_ItemViewItem, opt, painter)
    #
    #     painter.translate(opt.rect.left(), opt.rect.top())
    #     clip = QRectF(QPointF(), QSizeF(opt.rect.size()))
    #     doc.drawContents(painter, clip)
    #
    #     painter.restore()

    def setModelData(self, editor: TagEditor, model: QAbstractItemModel, index: QModelIndex) -> None:
        # print('setModelData')
        if index.column() in (self.source_column, self.target_column):
            model.setData(index, editor.to_model_data(), Qt.EditRole)

    def setEditorData(self, editor: TagEditor, index: QModelIndex) -> None:
        # print('setEditorData')
        editor.setText('')
        cursor = editor.textCursor()
        if index.column() in (self.source_column, self.target_column):
            value = index.model().data(index, Qt.DisplayRole)
            self.__init_editor_data(cursor, value)
            # for run in self.all_tags.split(value):
            #     if self.start_tags.search(run):
            #         name = run.strip('{>')
            #         TagEditor.insert_tag(cursor, name, name, TagKind.START)
            #     elif self.end_tags.search(run):
            #         name = run.strip('<}')
            #         TagEditor.insert_tag(cursor, name, name, TagKind.END)
            #     elif self.empty_tags.search(run):
            #         name = run.strip('{}')
            #         TagEditor.insert_tag(cursor, name, name, TagKind.EMPTY)
            #     else:
            #         cursor.insertHtml(f'<span>{run}</span>')

    def __init_editor_data(self, cursor: QTextCursor, value: str) -> None:
        for run in self.all_tags.split(value):
            if self.start_tags.search(run):
                name = run.strip('{>')
                TagEditor.insert_tag(cursor, name, name, TagKind.START)
            elif self.end_tags.search(run):
                name = run.strip('<}')
                TagEditor.insert_tag(cursor, name, name, TagKind.END)
            elif self.empty_tags.search(run):
                name = run.strip('{}')
                TagEditor.insert_tag(cursor, name, name, TagKind.EMPTY)
            else:
                run = run.replace('\r\n', '\n').replace('\r', '\n')
                run = run.replace('\n', '<br/>')
                cursor.insertHtml(f'<span>{run}</span>')
