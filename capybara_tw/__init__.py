#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from capybara_tw.app import MainWindow

__version__ = '0.1'
__application_name__ = 'Capybara Translation Workbench'
__organization_name__ = 'Capybara Translation'


def run():
    app_ = QApplication(sys.argv)
    app_.setApplicationName(__application_name__)
    app_.setOrganizationName(__organization_name__)
    app_.setApplicationVersion(__version__)
    window = MainWindow()
    window.show()
    sys.exit(app_.exec_())


if __name__ == '__main__':
    run()
