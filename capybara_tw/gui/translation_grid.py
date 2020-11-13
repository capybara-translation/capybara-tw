from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QShowEvent

from capybara_tw.gui.tageditor_delegate import TagEditorDelegate


class TranslationGrid(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Auto-fit column width

        segment_delegate = TagEditorDelegate(self)
        self.setItemDelegateForColumn(0, segment_delegate)
        self.setItemDelegateForColumn(1, segment_delegate)

    def showEvent(self, a0: QShowEvent) -> None:
        print('showEvent2')
        super().showEvent(a0)
        self.resizeRowsToContents()

    def init_persistent_editors(self):
        for i in range(self.model().rowCount()):
            self.openPersistentEditor(self.model().index(i, 0, QModelIndex()))
            self.openPersistentEditor(self.model().index(i, 1, QModelIndex()))
