import sys
from PyQt5.QtWidgets import QApplication
from db_models import Base, engine
from gui_login import LoginApp
from utils import setup_logging

if __name__ == "__main__":
    setup_logging()
    Base.metadata.create_all(engine)

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