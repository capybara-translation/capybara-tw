#!/usr/bin/env python3
from PyQt5.Qt import QMainWindow
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QFileDialog

from capybara_tw.gui.main_window import Ui_MainWindow
from capybara_tw.xliff_model import XliffModel


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = None
        self.srcEditor.set_readonly_with_text_selectable()

        self.translationGrid.currentSourceSegmentChanged.connect(self.srcEditor.initialize)
        self.translationGrid.currentTargetSegmentChanged.connect(self.tgtEditor.initialize)

        self.srcEditor.segmentEdited.connect(self.translationGrid.set_source_segment)
        self.tgtEditor.segmentEdited.connect(self.translationGrid.set_target_segment)

        self.__initialize_actions()

        self.show()

    def __initialize_actions(self):
        paragraph_icon = QIcon(':/icon/paragraph.png')
        self.actionDisplayHiddenCharacters.setIcon(paragraph_icon)
        self.actionDisplayHiddenCharacters.setToolTip(
            f'{self.actionDisplayHiddenCharacters.toolTip()}')
        self.actionDisplayHiddenCharacters.triggered.connect(self.display_hidden_characters)

        self.actionMoveToFirstSegment.setToolTip(
            f'{self.actionMoveToFirstSegment.toolTip()} ({self.actionMoveToFirstSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToFirstSegment.triggered.connect(lambda: self.translationGrid.move_to_first_or_last_segment(True))

        self.actionMoveToLastSegment.setToolTip(
            f'{self.actionMoveToLastSegment.toolTip()} ({self.actionMoveToLastSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToLastSegment.triggered.connect(lambda: self.translationGrid.move_to_first_or_last_segment(False))

        self.actionMoveToNextSegment.setToolTip(
            f'{self.actionMoveToNextSegment.toolTip()} ({self.actionMoveToNextSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToNextSegment.triggered.connect(lambda: self.translationGrid.move_to_adjacent_segment(False))

        self.actionMoveToPreviousSegment.setToolTip(
            f'{self.actionMoveToPreviousSegment.toolTip()} ({self.actionMoveToPreviousSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToPreviousSegment.triggered.connect(lambda: self.translationGrid.move_to_adjacent_segment(True))

        confirm_icon = QIcon(':/icon/confirm.png')
        self.actionConfirmSegment.setIcon(confirm_icon)
        self.actionConfirmSegment.setToolTip(
            f'{self.actionConfirmSegment.toolTip()} ({self.actionConfirmSegment.shortcut().toString(QKeySequence.NativeText)})')

        unconfirm_icon = QIcon(':/icon/unconfirm.png')
        self.actionUnconfirmSegment.setIcon(unconfirm_icon)
        self.actionUnconfirmSegment.setToolTip(
            f'{self.actionUnconfirmSegment.toolTip()} ({self.actionUnconfirmSegment.shortcut().toString(QKeySequence.NativeText)})')

        self.actionOpen.triggered.connect(self.open_file)

    def display_hidden_characters(self, display=False):
        self.srcEditor.display_hidden_characters(display)
        self.tgtEditor.display_hidden_characters(display)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select an mxliff file to open...",
            directory=QDir.homePath(),
            filter='Mxliff Files (*.mxliff) ;;All Files (*)',
        )
        if filename:
            self.model = XliffModel(filename)
            self.translationGrid.setModel(self.model)
            self.translationGrid.selectionModel().selectionChanged.connect(self.translationGrid.selection_changed)
            self.translationGrid.selectRow(0)
