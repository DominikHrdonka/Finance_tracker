import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QRadioButton, QPushButton,
    QLineEdit, QLabel, QApplication
)
from PyQt5.QtCore import Qt

from screenshot import take_screenshot, add_amounts_to_db
from graph import show_transaction_graph

class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.graph_visible = True
        self.init_db()
        self.init_ui()
        self.update_graph()

    def init_db(self):
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

    def init_ui(self):
        self.resize(900, 700)
        self.setWindowTitle("Finance Tracker")

        layout = QVBoxLayout()

        # Income/Expense selection
        self.radio_income = QRadioButton("Income")
        self.radio_income.setChecked(True)
        self.radio_expense = QRadioButton("Expense")
        layout.addWidget(self.radio_income)
        layout.addWidget(self.radio_expense)

        # Manual entry input
        self.textbox = QLineEdit()
        layout.addWidget(self.textbox)

        self.enter_button = QPushButton("Add Amount")
        self.enter_button.clicked.connect(self.submit_manual_amount)
        layout.addWidget(self.enter_button)

        # Screenshot + OCR button
        self.screenshot_button = QPushButton("Take Screenshot")
        self.screenshot_button.clicked.connect(self.take_screenshot)
        layout.addWidget(self.screenshot_button)

        # Graph toggle
        self.graph_button = QPushButton("Hide Graph")
        self.graph_button.clicked.connect(self.toggle_graph)
        layout.addWidget(self.graph_button)

        # Clear all button
        self.clear_button = QPushButton("Clear All Transactions")
        self.clear_button.clicked.connect(self.clear_transactions)
        layout.addWidget(self.clear_button)

        # Graph area
        self.graph_widget = QWidget(self)
        self.graph_layout = QVBoxLayout(self.graph_widget)
        layout.addWidget(self.graph_widget)

        # Balance label
        self.label = QLabel(f"Current balance: {self.balance} CZK")
        layout.addWidget(self.label)

        # Screenshot preview
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setFixedSize(500, 300)
        layout.addWidget(self.screenshot_label)

        self.setLayout(layout)
        self.show()

    def submit_manual_amount(self):
        try:
            amount = int(self.textbox.text())
        except ValueError:
            self.label.setText(f"Error: Please enter a valid amount!\nCurrent balance: {self.balance} CZK")
            return

        transaction_type = "Income" if self.radio_income.isChecked() else "Expense"
        if transaction_type == "Expense":
            amount = -abs(amount)

        self.cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", (transaction_type, amount))
        self.conn.commit()
        self.balance += amount
        self.label.setText(f"Current balance: {self.balance} CZK")
        self.textbox.clear()

        if self.graph_visible:
            self.update_graph()

    def take_screenshot(self):
        amounts = take_screenshot(self)
        if amounts:
            add_amounts_to_db(self, amounts)
            if self.graph_visible:
                self.update_graph()

    def toggle_graph(self):
        self.graph_visible = not self.graph_visible
        self.graph_widget.setVisible(self.graph_visible)
        self.graph_button.setText("Show Graph" if not self.graph_visible else "Hide Graph")
        if self.graph_visible:
            self.update_graph()

    def show_graph(self):
        self.clear_graph()
        canvas = show_transaction_graph(self.cursor)
        if canvas:
            canvas.setMinimumWidth(800)
            canvas.setMinimumHeight(400)
            self.graph_layout.addWidget(canvas)
        else:
            self.show_no_data_label()

    def update_graph(self):
        self.clear_graph()
        canvas = show_transaction_graph(self.cursor)
        if canvas:
            canvas.setMinimumWidth(800)
            canvas.setMinimumHeight(400)
            self.graph_layout.addWidget(canvas)
            self.graph_widget.setVisible(True)
        else:
            self.show_no_data_label()

    def clear_graph(self):
        while self.graph_layout.count():
            item = self.graph_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_no_data_label(self):
        no_data_label = QLabel("No transaction data available.", self)
        no_data_label.setAlignment(Qt.AlignCenter)
        no_data_label.setStyleSheet("font-size: 18px; font-weight: bold; color: gray;")
        self.graph_layout.addWidget(no_data_label)
        self.graph_widget.setVisible(True)

    def clear_transactions(self):
        self.cursor.execute("DELETE FROM transactions")
        self.conn.commit()
        self.balance = 0
        self.label.setText("Balance reset: 0 CZK (all transactions cleared)")
        if self.graph_visible:
            self.update_graph()
