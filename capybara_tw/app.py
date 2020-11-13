#!/usr/bin/env python3
from PyQt5.Qt import QMainWindow
from PyQt5.QtGui import (QIcon, QKeySequence, QShowEvent)
from PyQt5.QtWidgets import (QFileDialog, QHeaderView, QAbstractItemView, QAbstractScrollArea)
from PyQt5.QtCore import (Qt, QDir, QModelIndex)
from capybara_tw.gui.main_window import Ui_MainWindow
from capybara_tw.gui.translation_grid import TranslationGrid
from capybara_tw.xliff_model import XliffModel
from capybara_tw.gui.tageditor_delegate import TagEditorDelegate


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = None
        self.translation_grid = TranslationGrid(self.defaultTab)
        self.gridLayout.addWidget(self.translation_grid, 0, 0, 1, 1)

        # self.tuTableView.setSortingEnabled(False)
        # self.tuTableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.tuTableView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        # self.tuTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Auto-fit column width
        # self.tuTableView.horizontalHeader().sectionResized.connect(self.tuTableView.resizeRowsToContents)
        # self.tuTableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tuTableView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

        # self.segment_delegate = TagEditorDelegate(self.tuTableView)
        # self.tuTableView.setItemDelegateForColumn(0, self.segment_delegate)
        # self.tuTableView.setItemDelegateForColumn(1, self.segment_delegate)

        bold_icon = QIcon(':/icon/bold.png')
        self.actionBold.setIcon(bold_icon)
        self.actionBold.setToolTip(
            f'{self.actionBold.toolTip()} ({self.actionBold.shortcut().toString(QKeySequence.NativeText)})')

        italic_icon = QIcon(':/icon/italic.png')
        self.actionItalic.setIcon(italic_icon)
        self.actionItalic.setToolTip(
            f'{self.actionItalic.toolTip()} ({self.actionItalic.shortcut().toString(QKeySequence.NativeText)})')

        underlined_icon = QIcon(':/icon/underlined.png')
        self.actionUnderlined.setIcon(underlined_icon)
        self.actionUnderlined.setToolTip(
            f'{self.actionUnderlined.toolTip()} ({self.actionUnderlined.shortcut().toString(QKeySequence.NativeText)})')

        superscript_icon = QIcon(':/icon/superscript.png')
        self.actionSuperscript.setIcon(superscript_icon)
        self.actionSuperscript.setToolTip(
            f'{self.actionSuperscript.toolTip()} ({self.actionSuperscript.shortcut().toString(QKeySequence.NativeText)})')

        subscript_icon = QIcon(':/icon/subscript.png')
        self.actionSubscript.setIcon(subscript_icon)
        self.actionSubscript.setToolTip(
            f'{self.actionSubscript.toolTip()} ({self.actionSubscript.shortcut().toString(QKeySequence.NativeText)})')

        self.actionOpen.triggered.connect(self.open_file)

        self.show()

    def showEvent(self, a0: QShowEvent) -> None:
        print('showEvent1')
        super().showEvent(a0)
        self.translation_grid.resizeRowsToContents()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select an mxliff file to open...",
            directory=QDir.homePath(),
            filter='Mxliff Files (*.mxliff) ;;All Files (*)',
        )
        if filename:
            self.model = XliffModel(filename)
            self.translation_grid.setModel(self.model)
            # self.tuTableView.viewport().update()
            self.translation_grid.init_persistent_editors()
            self.translation_grid.resizeRowsToContents()
            # self.translation_grid.verticalHeader().setMinimumSectionSize()

    def init_persistent_editors(self):
        for i in range(self.tuTableView.model().rowCount()):
            self.tuTableView.openPersistentEditor(self.tuTableView.model().index(i, 0, QModelIndex()))
            self.tuTableView.openPersistentEditor(self.tuTableView.model().index(i, 1, QModelIndex()))
