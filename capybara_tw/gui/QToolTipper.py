#!/usr/bin/env python3
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QToolTip


class QToolTipper(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.ToolTip:
            view = obj.parent()
            if not view:
                return False
            pos = event.pos()
            index = view.indexAt(pos)
            if not index.isValid():
                return False
            item_text = view.model().data(index, Qt.DisplayRole)
            item_tool_tip = view.model().data(index, Qt.ToolTipRole)
            fm = QFontMetrics(view.font())
            item_text_width = fm.width(item_text)
            rect = view.visualRect(index)
            rect_width = rect.width()
            if (item_text_width > (rect_width - 20) or '\n' in item_text) and item_tool_tip:
                QToolTip.showText(event.globalPos(), item_tool_tip, view, rect)
            else:
                QToolTip.hideText()
            return True
        return False
