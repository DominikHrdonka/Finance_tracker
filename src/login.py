import json
import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

USER_DATA_FILE = "users.json"

# ======== Správa uživatelů ======== #
class UserManager:
    @staticmethod
    def load_users():
        try:
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_users(users):
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(users, file, indent=4)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

# ======== LoginApp ======== #
class LoginApp(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_authenticated = False  # ✅ Přidáno
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Finance Tracker Login")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        self.label = QLabel("Přihlášení", self)
        self.label.setFont(QFont('Segoe UI', 24))
        layout.addWidget(self.label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Uživatelské jméno")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Heslo")
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Přihlásit se", self)
        self.login_button.clicked.connect(self.on_login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Registrace", self)
        self.register_button.clicked.connect(self.on_register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.setStyleSheet('''
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #333;
                text-align: center;
            }
            QLineEdit {
                background-color: #fff;
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
            }
            QPushButton {
                background-color: #007BFF;
                color: #fff;
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        ''')

    def on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        users = UserManager.load_users()

        if username in users and users[username] == UserManager.hash_password(password):
            self.is_authenticated = True  # ✅ Přidáno
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Chyba", "❌ Nesprávné uživatelské jméno nebo heslo")

    def on_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        users = UserManager.load_users()

        if username in users:
            QMessageBox.warning(self, "Chyba", "❗ Uživatelské jméno již existuje.")
        elif len(username) < 3 or len(password) < 3:
            QMessageBox.warning(self, "Chyba", "❗ Uživatelské jméno a heslo musí mít alespoň 3 znaky.")
        else:
            users[username] = UserManager.hash_password(password)
            UserManager.save_users(users)
            QMessageBox.information(self, "Úspěch", "✅ Registrace proběhla úspěšně!")
