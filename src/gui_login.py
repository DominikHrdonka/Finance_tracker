from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
from login import load_users, save_users

users = load_users()

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_authenticated = False  # Indicates whether the login was successful
        self.init_ui()

    def init_ui(self):
        """Initializes the login window UI."""
        self.setWindowTitle("Login")

        layout = QGridLayout()

        # Username field
        self.label_name = QLabel("Username:")
        self.textbox_name = QLineEdit()
        layout.addWidget(self.label_name, 0, 0)
        layout.addWidget(self.textbox_name, 0, 1)

        # Password field
        self.label_password = QLabel("Password:")
        self.textbox_password = QLineEdit()
        self.textbox_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.textbox_password, 1, 1)

        # Login button
        self.btn_login = QPushButton("Log In")
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login, 2, 0, 1, 2)

        # Register button
        self.btn_register = QPushButton("Register")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register, 3, 0, 1, 2)

        self.setLayout(layout)

    def check_login(self):
        """Validates the provided credentials."""
        username = self.textbox_name.text()
        password = self.textbox_password.text()

        if username in users and users[username] == password:
            QMessageBox.information(self, "Success", "Login successful.")
            self.is_authenticated = True
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")

    def register_user(self):
        """Registers a new user if validation passes."""
        username = self.textbox_name.text()
        password = self.textbox_password.text()

        if username in users:
            QMessageBox.warning(self, "Error", "User already exists.")
        elif not username or not password:
            QMessageBox.warning(self, "Error", "Username and password must not be empty.")
        else:
            users[username] = password
            save_users(users)
            QMessageBox.information(self, "Success", f"User '{username}' has been registered successfully.")
