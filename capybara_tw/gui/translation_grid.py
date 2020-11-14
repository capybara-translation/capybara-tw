from PyQt5.QtCore import QItemSelection, pyqtSignal, Qt, QItemSelectionModel, QSize
from PyQt5.QtWidgets import QTableView, QHeaderView

from capybara_tw.gui.QToolTipper import QToolTipper


class TranslationGrid(QTableView):
    currentSourceSegmentChanged = pyqtSignal(str)
    currentTargetSegmentChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Auto-fit column width
        self.viewport().installEventFilter(QToolTipper(self))

    def selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        ci = self.selectionModel().currentIndex()
        src = ci.siblingAtColumn(0).data()
        tgt = ci.siblingAtColumn(1).data()

        self.currentSourceSegmentChanged.emit(src)
        self.currentTargetSegmentChanged.emit(tgt)

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
