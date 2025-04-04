# Changelog

## v0.2.0 – Major Update (EasyOCR, SQLAlchemy, Logging)

### Changed
- Replaced Tesseract OCR with EasyOCR for better and more flexible recognition
- Switched from SQLite via `sqlite3` to SQLAlchemy ORM
- Reorganized project structure – split `main.py` into multiple files: `gui_tracker.py`, `gui_login.py`, `login.py`, `screenshot.py`, `graph.py`, etc.
- Replaced all `print()` statements with proper logging
- Moved logging configuration to `utils.py`
- Refactored login system to use SQLite and SQLAlchemy instead of JSON
- Updated `requirements.txt` with pinned versions
- Updated `README.md` and marked completed TODOs

### Added
- Password hashing with salt using `bcrypt`
- Graph generation using Matplotlib based on SQLAlchemy data
- Transaction type selection (Income / Expense)
- OCR-based screenshot capture and amount extraction

### Removed
- `login_db.py` and JSON-based login system
- Tesseract-related dependencies
- `finance_tracker.db` from version control (now in `.gitignore`)

---

## v0.1.0 – Initial GUI Version

### Added
- PyQt5 GUI to track income and expenses
- Manual entry of amounts
- Screenshot capture integration (initial version)
- Transaction bar chart using Matplotlib
- Basic login window using JSON user storage
- Initial project setup and directory structure