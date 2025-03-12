import sys
import keyboard
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QPushButton, QLineEdit, QLabel

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.initDB()
        self.initUI()

    def initDB(self):
        self.conn = sqlite3.connect("finance_tracker.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount INTEGER
            )
        ''')
        self.conn.commit()

        # Načti celkový zůstatek
        self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        self.balance = self.cursor.fetchone()[0]

    def initUI(self):
        layout = QVBoxLayout()
        
        # Radio Buttony
        self.radio1 = QRadioButton("Přijem")
        self.radio2 = QRadioButton("Výdaj")
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        
        # Textové pole
        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)
        keyboard.add_hotkey('enter', self.onSubmit)
        
        # Tlačítko
        self.button = QPushButton("Enter", self)
        self.button.clicked.connect(self.onSubmit)
        layout.addWidget(self.button)
        
        # Štítek na výstup
        self.label = QLabel("Výstup se zobrazí zde.")
        self.label.setText(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        self.setWindowTitle("Finance Tracker")
        self.show()

    def onSubmit(self):
        selected_option = ""

        try:
            amount = int(self.textbox.text())
        except ValueError:
            self.label.setText(f"Chyba: Zadej prosím platnou částku!\nNa vašem účtu je zůstatek: {self.balance} Kč")
            return


        if self.radio1.isChecked():
            selected_option = "Příjem"
            self.balance += amount
            self.label.setText(f"Na váš účet bylo připsáno: {amount} Kč\nNa vašem účtu je zůstatek: {self.balance} Kč")
        elif self.radio2.isChecked():
            selected_option = "Výdaj"
            self.balance -= amount
            self.label.setText(f"Z vašeho účtu bylo vydáno: {amount} Kč\nNa vašem účtu je zůstatek: {self.balance} Kč")

        self.label.setText(f"{selected_option}: {amount} Kč\nNa vašem účtu je zůstatek: {self.balance} Kč")
        self.textbox.clear()

        # Ulož do databáze
        self.cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)",
                            (selected_option, amount if selected_option == "Příjem" else -amount))
        self.conn.commit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
