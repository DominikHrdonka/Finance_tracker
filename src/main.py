import sys
from PyQt5.QtWidgets import QApplication
from gui_login import LoginApp
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginApp()
    login_window.show()
    app.exec_()

    if login_window.is_authenticated:
        # Import and launch main app here
        from gui_tracker import FinanceTracker
        tracker = FinanceTracker()
        tracker.show()
        sys.exit(app.exec_())