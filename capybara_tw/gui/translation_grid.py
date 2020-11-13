from PyQt5.QtWidgets import QTableView, QHeaderView


class TranslationGrid(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Auto-fit column width
