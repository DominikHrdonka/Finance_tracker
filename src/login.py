import json
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox

# Soubor s uloženými uživateli
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

# Uživatelé uložené v souboru
users = load_users()

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_authenticated = False  # ✅ Zda byl uživatel úspěšně přihlášen
        self.init_ui()

    def init_ui(self):
        """Inicializace UI přihlašovacího okna."""
        self.setWindowTitle("Přihlášení")

        layout = QGridLayout()

        # Jméno uživatele
        self.label_name = QLabel("Jméno:")
        self.textbox_name = QLineEdit()
        layout.addWidget(self.label_name, 0, 0)
        layout.addWidget(self.textbox_name, 0, 1)

        # Heslo
        self.label_password = QLabel("Heslo:")
        self.textbox_password = QLineEdit()
        self.textbox_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.textbox_password, 1, 1)

        # Přihlašovací tlačítko
        self.btn_login = QPushButton("Přihlásit se")
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login, 2, 0, 1, 2)

        # Tlačítko pro registraci
        self.btn_register = QPushButton("Registrace")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register, 3, 0, 1, 2)

        self.setLayout(layout)

    def check_login(self):
        """Ověření přihlašovacích údajů."""
        username = self.textbox_name.text()
        password = self.textbox_password.text()

        if username in users and users[username] == password:
            QMessageBox.information(self, "Úspěch", "Přihlášení úspěšné!")
            self.is_authenticated = True  # ✅ Označíme přihlášení jako úspěšné
            self.close()  # Zavřeme přihlašovací okno
        else:
            QMessageBox.warning(self, "Chyba", "Neplatné přihlašovací údaje.")

    def register_user(self):
        """Registrace nového uživatele."""
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
