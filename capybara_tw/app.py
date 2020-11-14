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
        self.prevEditor.set_readonly_with_text_selectable()
        self.nextEditor.set_readonly_with_text_selectable()
        self.srcEditor.set_readonly_with_text_selectable()

        self.translationGrid.currentSourceSegmentChanged.connect(self.srcEditor.initialize)
        self.translationGrid.currentTargetSegmentChanged.connect(self.tgtEditor.initialize)
        self.translationGrid.previousSegmentChanged.connect(self.prevEditor.initialize)
        self.translationGrid.nextSegmentChanged.connect(self.nextEditor.initialize)

        self.srcEditor.segmentEdited.connect(self.translationGrid.set_source_segment)
        self.tgtEditor.segmentEdited.connect(self.translationGrid.set_target_segment)

        self.__initialize_actions()

        self.show()

    def __initialize_actions(self):
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

        paragraph_icon = QIcon(':/icon/paragraph.png')
        self.actionDisplayHiddenCharacters.setIcon(paragraph_icon)
        self.actionDisplayHiddenCharacters.setToolTip(
            f'{self.actionDisplayHiddenCharacters.toolTip()}')
        self.actionDisplayHiddenCharacters.triggered.connect(self.display_hidden_characters)

        self.actionMoveToFirstSegment.setToolTip(
            f'{self.actionMoveToFirstSegment.toolTip()} ({self.actionMoveToFirstSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToLastSegment.setToolTip(
            f'{self.actionMoveToLastSegment.toolTip()} ({self.actionMoveToLastSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToNextSegment.setToolTip(
            f'{self.actionMoveToNextSegment.toolTip()} ({self.actionMoveToNextSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToPreviousSegment.setToolTip(
            f'{self.actionMoveToPreviousSegment.toolTip()} ({self.actionMoveToPreviousSegment.shortcut().toString(QKeySequence.NativeText)})')

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
        self.prevEditor.display_hidden_characters(display)
        self.nextEditor.display_hidden_characters(display)
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
