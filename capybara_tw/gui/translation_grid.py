from typing import Tuple

from PyQt5.QtCore import QItemSelection, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import QTableView, QHeaderView

from capybara_tw.model.capy_trans_unit import CapyTransUnit
from capybara_tw.xliff_model import GetTransUnitRole


class TranslationGrid(QTableView):
    currentSourceSegmentChanged = pyqtSignal(CapyTransUnit)  # Tuple of bool and CapyTransUnit
    currentTargetSegmentChanged = pyqtSignal(CapyTransUnit)  # Tuple of bool and CapyTransUnit
    sourceColumnSelected = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Auto-fit column width
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

    def selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        ci = self.selectionModel().currentIndex()
        # Retrieve the selected translation unit and send it to the segment editors.
        tu = ci.model().data(ci, GetTransUnitRole)
        self.currentSourceSegmentChanged.emit(tu)
        self.currentTargetSegmentChanged.emit(tu)
        self.sourceColumnSelected.emit(ci.column() == 0)

    def set_source_segment(self, text):
        ci = self.selectionModel().currentIndex()
        idx = ci.siblingAtColumn(0)
        idx.model().setData(idx, text, Qt.EditRole)
        if idx.isValid():
            idx.model().setData(idx, text, Qt.EditRole)

    def set_target_segment(self, text):
        ci = self.selectionModel().currentIndex()
        idx = ci.siblingAtColumn(1)
        if idx.isValid():
            idx.model().setData(idx, text, Qt.EditRole)

    def move_to_adjacent_segment(self, prev=False):
        if not self.selectionModel():
            return
        ci = self.selectionModel().currentIndex()
        if prev:
            idx = ci.siblingAtRow(ci.row() - 1)
        else:
            idx = ci.siblingAtRow(ci.row() + 1)
        if idx.isValid():
            self.setCurrentIndex(idx)

    def move_to_first_or_last_segment(self, first=False):
        if not self.selectionModel():
            return
        ci = self.selectionModel().currentIndex()
        if first:
            idx = ci.siblingAtRow(0)
        else:
            idx = ci.siblingAtRow(self.selectionModel().model().rowCount() - 1)
        if idx.isValid():
            self.setCurrentIndex(idx)

    def sizeHint(self) -> QSize:
        return QSize(self.width(), 600)

    def resize_current_row(self):
        if not self.selectionModel():
            return
        ci = self.selectionModel().currentIndex()
        if ci.isValid():
            self.resizeRowToContents(ci.row())

    def on_scroll(self):
        # Ensure that selected row moves when scrolling - it must be always visible.
        current_idx = self.selectionModel().currentIndex()
        rect = self.viewport().rect()
        top_idx = self.indexAt(rect.topLeft())
        if current_idx.row() < top_idx.row():
            if top_idx.isValid():
                self.setCurrentIndex(top_idx.siblingAtColumn(current_idx.column()))
        else:
            bottom_idx = self.indexAt(rect.bottomLeft())
            if current_idx.row() > bottom_idx.row():
                if bottom_idx.isValid():
                    self.setCurrentIndex(bottom_idx.siblingAtColumn(current_idx.column()))
