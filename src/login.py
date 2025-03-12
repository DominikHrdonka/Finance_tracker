import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
)
import sys

# Cesta k souboru s uživateli
USER_FILE = "users.json"

# Funkce pro načtení uživatelů ze souboru
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Funkce pro uložení uživatelů do souboru
def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Inicializace uživatelské databáze
users = load_users()

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Přihlášení")
        self.setStyleSheet(self.load_styles())  # Použití QStyle

        layout = QGridLayout()

        # Jméno uživatele
        self.label_name = QLabel("Name:")
        self.textbox_name = QLineEdit()
        layout.addWidget(self.label_name, 0, 0)
        layout.addWidget(self.textbox_name, 0, 1)

        # Heslo
        self.label_password = QLabel("Password:")
        self.textbox_password = QLineEdit()
        self.textbox_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.textbox_password, 1, 1)

        # Tlačítka
        self.btn_login = QPushButton("Přihlásit se")
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login, 2, 0, 1, 2)

        self.btn_register = QPushButton("Registrace")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register, 3, 0, 1, 2)

        self.btn_forgot_password = QPushButton("Zapomenuté heslo")
        self.btn_forgot_password.clicked.connect(self.forgot_password)
        layout.addWidget(self.btn_forgot_password, 4, 0, 1, 2)

        self.setLayout(layout)

    # Načtení stylů z řetězce (QSS)
    def load_styles(self):
        return """
        QWidget {
            background-color: #f0f2f5;
            font-family: Arial;
        }

        QLabel {
            font-weight: bold;
            font-size: 14px;
        }

        QLineEdit {
            border: 2px solid #5e72e4;
            border-radius: 8px;
            padding: 6px;
            background-color: #ffffff;
        }

        QPushButton {
            background-color: #4a69bd;  /* Výraznější modrá */
            color: #ffffff;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
            font-size: 16px;  /* Větší text */
            border: 2px solid #324cdd;
        }

        QPushButton:hover {
            background-color: #3b4cca;  /* Zesvětlená modrá při najetí myší */
            color: #f0f2f5;
        }

        QPushButton:pressed {
            background-color: #2d3a8c;
        }

        QMessageBox {
            background-color: #ffffff;
        }
    """


    # Kontrola přihlášení
    def check_login(self):
        username = self.textbox_name.text()
        password = self.textbox_password.text()

        if username in users and users[username] == password:
            QMessageBox.information(self, "Úspěch", "Přihlášení úspěšné!")
        else:
            QMessageBox.warning(self, "Chyba", "Neplatné přihlašovací údaje.")

    # Registrace nového uživatele
    def register_user(self):
        username = self.textbox_name.text()
        password = self.textbox_password.text()

        if username in users:
            QMessageBox.warning(self, "Chyba", "Uživatel již existuje.")
        elif not username or not password:
            QMessageBox.warning(self, "Chyba", "Jméno a heslo musí být vyplněny.")
        else:
            users[username] = password
            save_users(users)
            QMessageBox.information(self, "Úspěch", f"Uživatel '{username}' byl úspěšně zaregistrován!")

    # Funkce pro zapomenuté heslo
    def forgot_password(self):
        username = self.textbox_name.text()

        if username in users:
            QMessageBox.information(self, "Obnovení hesla", f"Vaše heslo je: {users[username]}")
        else:
            QMessageBox.warning(self, "Chyba", "Uživatel nenalezen.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec_())
