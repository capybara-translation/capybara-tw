#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from capybara_tw.app import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())