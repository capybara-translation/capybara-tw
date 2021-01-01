#!/usr/bin/env python3
from typing import Optional

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

        self.model: Optional[XliffModel] = None
        self.srcEditor.set_readonly_with_text_selectable()

        self.translationGrid.currentSourceSegmentChanged.connect(self.srcEditor.initialize)
        self.translationGrid.currentTargetSegmentChanged.connect(self.tgtEditor.initialize)

        self.srcEditor.segmentEdited.connect(self.translationGrid.set_source_segment)
        self.tgtEditor.segmentEdited.connect(self.translationGrid.set_target_segment)
        self.srcEditor.segmentEdited.connect(self.translationGrid.resize_current_row)
        self.tgtEditor.segmentEdited.connect(self.translationGrid.resize_current_row)

        self.__initialize_actions()
        self.__enable_actions(False)

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
        self.actionSave.triggered.connect(self.save)
        self.actionInsertTag.triggered.connect(self.tgtEditor.copy_tag_from_source)
        # Disable actionInsertTag when srcEditor is in focus
        self.srcEditor.focusedIn.connect(lambda v: self.actionInsertTag.setDisabled(not self.model or v))

        self.actionExpandTags.triggered.connect(self.srcEditor.expand_tags)
        self.actionExpandTags.triggered.connect(self.tgtEditor.expand_tags)

    def __enable_actions(self, is_enabled: bool) -> None:
        self.actionDisplayHiddenCharacters.setEnabled(is_enabled)
        self.actionMoveToFirstSegment.setEnabled(is_enabled)
        self.actionMoveToLastSegment.setEnabled(is_enabled)
        self.actionMoveToPreviousSegment.setEnabled(is_enabled)
        self.actionMoveToNextSegment.setEnabled(is_enabled)
        self.actionConfirmSegment.setEnabled(is_enabled)
        self.actionUnconfirmSegment.setEnabled(is_enabled)
        self.actionInsertTag.setEnabled(is_enabled)

    def display_hidden_characters(self, display=False):
        self.srcEditor.display_hidden_characters(display)
        self.tgtEditor.display_hidden_characters(display)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select a capyxliff file to open...",
            directory=QDir.homePath(),
            filter='Capyxliff Files (*.capyxliff) ;;All Files (*)',
        )
        if filename:
            self.model = XliffModel(filename)
            self.translationGrid.setModel(self.model)
            self.translationGrid.selectionModel().selectionChanged.connect(self.translationGrid.selection_changed)
            self.translationGrid.selectRow(0)
            self.translationGrid.resizeRowsToContents()
            self.__enable_actions(True)

    def save(self):
        if self.model:
            self.model.save_data()
