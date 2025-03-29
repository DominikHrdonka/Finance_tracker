import sys
from PyQt5.QtWidgets import QApplication
from login import LoginApp
from gui import FinanceTracker

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginApp()
    login_window.show()
    app.exec_()  # Wait for login window to close

    if login_window.is_authenticated:
        main_window = FinanceTracker()
        main_window.show()
        sys.exit(app.exec_())
