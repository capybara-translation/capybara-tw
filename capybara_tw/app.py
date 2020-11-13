#!/usr/bin/env python3
from PyQt5.Qt import QMainWindow
from PyQt5.QtCore import (QDir)
from PyQt5.QtGui import (QIcon, QKeySequence)
from PyQt5.QtWidgets import (QFileDialog)

from capybara_tw.gui.main_window import Ui_MainWindow
from capybara_tw.xliff_model import XliffModel


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = None

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
