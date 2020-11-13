#!/usr/bin/env python3
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

from capybara_toolkit.converter.mxliff import Mxliff


class XliffModel(QAbstractTableModel):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.mxlf = Mxliff.load(self.filename)
        self._headers = ['Source', 'Target']
        self._data = [tu for tu in self.mxlf.get_all_trans_units()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            tu = self._data[index.row()]
            return tu.source if index.column() == 0 else tu.target

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    def save_data(self):
        pass
