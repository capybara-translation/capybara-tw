#!/usr/bin/env python3
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

from capybara_tw.model.capy_xliff import CapyXliff

GetSourceRole = Qt.UserRole + 1
GetTargetRole = Qt.UserRole + 2
GetTransUnitRole = Qt.UserRole + 3


class XliffModel(QAbstractTableModel):

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.xliff = CapyXliff.load(self.filename)
        self._headers = ['Source', 'Target']
        self._data = [tu for tu in self.xliff.get_all_trans_units()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if index.column() in (0, 1) and role == Qt.TextAlignmentRole:
            return Qt.AlignTop
        if role == Qt.DisplayRole:
            tu = self._data[index.row()]
            return tu.source.text if index.column() == 0 else tu.target.text
        if role == GetSourceRole:
            tu = self._data[index.row()]
            return tu.source
        if role == GetTargetRole:
            tu = self._data[index.row()]
            return tu.target
        if role == GetTransUnitRole:
            tu = self._data[index.row()]
            return tu

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.isValid() and role == Qt.EditRole:
            if index.column() == 0:
                self._data[index.row()].source.text = value
            else:
                self._data[index.row()].target.text = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def save_data(self):
        self.xliff.save(self.filename)
