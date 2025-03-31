# README.md

## Finance_tracker:
A PyQt5 application that displays income and expenses for the logged-in user. The app can extract amounts from screenshots using EasyOCR. And is configured for Czech number format — amounts like 1.234,56 CZK are correctly recognized and parsed.

## How to Run:
- `pip install -r requirements.txt`
- `python src/main.py`
- Create an account and log in (initial loading may take a moment)

---

## Development Progress Checklist:
- [x] Split `main.py` into multiple files
- [x] Write `README.md`
- [x] Create `requirements.txt`
- [x] Implement Tesseract OCR for capturing amounts
- [x] Switch from Tesseract OCR to EasyOCR
- [x] Configure and test EasyOCR functionality
- [x] Implement login system
- [x] Connect login with `main.py`
- [x] Add password hashing (salting)
- [x] Migrate login system from `users.json` to SQLite
- [x] Migrate from SQLite to SQLAlchemy for login
- [x] Use SQLAlchemy for all database input/output
- [x] Attempt pull request to merge `switching_to_easyOCR` branch into `main`
- [ ] Validate input fields in login form
- [ ] Handle negative amounts consistently (income/expense)
- Configured easyORC switch for global number formatting (e.g. `1,234.56 USD`)
- [ ] Create UI/UX design for the final application layout
- [ ] Implement transaction records (month, type, amount, description)
- [ ] Add transaction editing functionality
- [ ] Create a visual chart for income vs. expenses