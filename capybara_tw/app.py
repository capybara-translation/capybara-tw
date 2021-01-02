#!/usr/bin/env python3
from typing import Optional

from PyQt5.Qt import QMainWindow
from PyQt5.QtCore import QDir, QSettings
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QFileDialog, QDialog

from capybara_tw.gui.main_window import Ui_MainWindow
from capybara_tw.gui.preferences_dialog import Ui_PreferencesDialog
from capybara_tw.xliff_model import XliffModel

DEFAULT_FONT_SIZE = 15


class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, preferences: QSettings, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        self.setupUi(self)
        self.preferences = preferences
        self.tuGridFontSizeSpinBox.setValue(
            self.preferences.value('appearance/tu_grid/font_size', DEFAULT_FONT_SIZE, type=int))
        self.editorsFontSizeSpinBox.setValue(
            self.preferences.value('appearance/editors/font_size', DEFAULT_FONT_SIZE, type=int))

    def accept(self) -> None:
        self.preferences.setValue('appearance/tu_grid/font_size', self.tuGridFontSizeSpinBox.value())
        self.preferences.setValue('appearance/editors/font_size', self.editorsFontSizeSpinBox.value())
        super(PreferencesDialog, self).accept()


class MainWindow(QMainWindow, Ui_MainWindow):
    preferences = QSettings('Capybara Translation', 'CapybaraTranslationWorkbench')

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

        self.initialize_actions()
        self.enable_actions(False)
        self.enable_widgets(False)

        self.apply_preferences()

        self.show()

    def initialize_actions(self):
        paragraph_icon = QIcon(':/icon/paragraph.png')
        self.actionDisplayHiddenCharacters.setIcon(paragraph_icon)
        self.actionDisplayHiddenCharacters.setToolTip(
            f'{self.actionDisplayHiddenCharacters.toolTip()}')
        self.actionDisplayHiddenCharacters.toggled.connect(self.display_hidden_characters)

        self.actionMoveToFirstSegment.setToolTip(
            f'{self.actionMoveToFirstSegment.toolTip()} ({self.actionMoveToFirstSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToFirstSegment.triggered.connect(
            lambda: self.translationGrid.move_to_first_or_last_segment(True))

        self.actionMoveToLastSegment.setToolTip(
            f'{self.actionMoveToLastSegment.toolTip()} ({self.actionMoveToLastSegment.shortcut().toString(QKeySequence.NativeText)})')
        self.actionMoveToLastSegment.triggered.connect(
            lambda: self.translationGrid.move_to_first_or_last_segment(False))

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

        self.actionPreferences.triggered.connect(self.show_preferences_dialog)

    def show_preferences_dialog(self):
        ret = PreferencesDialog(self.preferences, self).exec()
        if ret == QDialog.Accepted:
            self.apply_preferences()

    def enable_actions(self, is_enabled: bool) -> None:
        self.actionDisplayHiddenCharacters.setEnabled(is_enabled)
        self.actionMoveToFirstSegment.setEnabled(is_enabled)
        self.actionMoveToLastSegment.setEnabled(is_enabled)
        self.actionMoveToPreviousSegment.setEnabled(is_enabled)
        self.actionMoveToNextSegment.setEnabled(is_enabled)
        self.actionConfirmSegment.setEnabled(is_enabled)
        self.actionUnconfirmSegment.setEnabled(is_enabled)
        self.actionInsertTag.setEnabled(is_enabled)

    def enable_widgets(self, is_enabled: bool) -> None:
        self.srcEditor.setEnabled(is_enabled)
        self.tgtEditor.setEnabled(is_enabled)

    def apply_preferences(self) -> None:
        tu_grid_font = self.translationGrid.font()
        tu_grid_font.setPointSize(self.preferences.value('appearance/tu_grid/font_size', DEFAULT_FONT_SIZE, type=int))
        self.translationGrid.setFont(tu_grid_font)
        self.translationGrid.resizeRowsToContents()

        editor_font_size = self.preferences.value('appearance/editors/font_size', DEFAULT_FONT_SIZE, type=int)
        self.srcEditor.setStyleSheet(f'font-size: {editor_font_size}pt')
        self.tgtEditor.setStyleSheet(f'font-size: {editor_font_size}pt')

        display_hidden_chars = self.preferences.value('appearance/editors/display_hidden_chars', False, type=bool)
        self.actionDisplayHiddenCharacters.setChecked(display_hidden_chars)

    def display_hidden_characters(self, display=False):
        self.srcEditor.display_hidden_characters(display)
        self.tgtEditor.display_hidden_characters(display)
        self.preferences.setValue('appearance/editors/display_hidden_chars', display)

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
            self.enable_actions(True)
            self.enable_widgets(True)

    def save(self):
        if self.model:
            self.model.save_data()
