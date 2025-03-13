import sys
import sqlite3
import re
import threading
import tkinter as tk
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QPushButton, QLineEdit, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PIL import ImageGrab, ImageQt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from login import LoginApp
from screenshot import take_screenshot
from graph import show_graph


class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.graph_visible = False
        self.initDB()
        self.initUI()

    def initDB(self):
        self.conn = sqlite3.connect("finance_tracker.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount INTEGER
            )
        """)
        self.conn.commit()
        self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        self.balance = self.cursor.fetchone()[0]

    def initUI(self):
        self.resize(900, 700)
        layout = QVBoxLayout()

        self.radio1 = QRadioButton("Příjem")
        self.radio2 = QRadioButton("Výdaj")
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)

        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)

        self.button = QPushButton("Enter", self)
        self.button.clicked.connect(self.onSubmit)
        layout.addWidget(self.button)

        self.screenshot_button = QPushButton("Vybrat oblast a udělat screenshot", self)
        self.screenshot_button.clicked.connect(self.take_screenshot)
        layout.addWidget(self.screenshot_button)

        self.graph_button = QPushButton("Zobrazit graf", self)
        self.graph_button.clicked.connect(self.toggleGraph)
        layout.addWidget(self.graph_button)

        self.clear_button = QPushButton("Vymazat všechny transakce", self)
        self.clear_button.clicked.connect(self.clearTransactions)
        layout.addWidget(self.clear_button)

        self.graph_widget = QWidget(self)
        self.graph_layout = QVBoxLayout(self.graph_widget)
        layout.addWidget(self.graph_widget)
        self.graph_widget.setVisible(False)

        self.label = QLabel(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        layout.addWidget(self.label)

        self.screenshot_label = QLabel(self)
        self.screenshot_label.setFixedSize(500, 300)
        layout.addWidget(self.screenshot_label)

        self.setLayout(layout)
        self.setWindowTitle("Finance Tracker")
        self.show()

    def onSubmit(self):
        try:
            amount = int(self.textbox.text())
        except ValueError:
            self.label.setText(f"Chyba: Zadej platnou částku!\nNa vašem účtu je zůstatek: {self.balance} Kč")
            return

        transaction_type = "Příjem" if self.radio1.isChecked() else "Výdaj"
        if transaction_type == "Výdaj":
            amount = -amount

        self.cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", (transaction_type, amount))
        self.conn.commit()
        self.balance += amount
        self.label.setText(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        self.textbox.clear()
        self.updateGraph()

    def take_screenshot(self):
        """Spustí screenshotovací funkci"""
        take_screenshot(self)  # ✅ Použití externí funkce ze screenshot.py

    def toggleGraph(self):
        if self.graph_visible:
            self.graph_widget.setVisible(False)
            self.graph_button.setText("Zobrazit graf")
        else:
            self.showGraph()
            self.graph_widget.setVisible(True)
            self.graph_button.setText("Skrýt graf")
        self.graph_visible = not self.graph_visible

    def display_graph(self):
        """Zavolá funkci pro zobrazení grafu"""
        show_graph(self, self.cursor)

    def clearTransactions(self):
        self.cursor.execute("DELETE FROM transactions")
        self.conn.commit()
        self.balance = 0
        self.label.setText(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        self.updateGraph()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginApp()
    login_window.show()
    app.exec_()  # Počkáme na zavření přihlašovacího okna

    if login_window.is_authenticated:
        main_window = FinanceTracker()
        main_window.show()
        sys.exit(app.exec_())
