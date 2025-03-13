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
from graph import showGraph
from screenshot import add_amounts_to_db
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QListWidget
from PyQt5.QtCore import Qt
import sys


class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.graph_visible = False
        self.initDB()
        self.initUI()  # ✅ Tlačítko se vytvoří tady
        self.updateGraph()
        self.graph_button.setText("Skrýt graf")

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
        self.setWindowTitle("Finance Tracker")
        self.resize(1000, 700)

        # 🔲 Hlavní layout bude grid
        layout = QGridLayout()

        # 📌 MENU PANEL (levý horní)
        self.menu_layout = QVBoxLayout()
        self.screenshot_button = QPushButton("📸 Udělat screenshot")
        self.clear_button = QPushButton("🗑️ Vymazat transakce")
        self.graph_button = QPushButton("Skrýt graf")  # ✅ Tlačítko pro zobrazení/skrytí grafu
        self.menu_layout.addWidget(self.screenshot_button)
        self.menu_layout.addWidget(self.clear_button)
        self.menu_layout.addWidget(self.graph_button)  # ✅ Přidáme tlačítko na přepínání grafu
        layout.addLayout(self.menu_layout, 0, 0)

        # 📜 VÝPIS TRANSAKCÍ (pravý horní)
        self.transaction_list = QListWidget()
        self.transaction_list.addItem("🔄 Historie transakcí")  # Placeholder
        layout.addWidget(self.transaction_list, 0, 1)

        # 📸 SCREENSHOT PANEL (levý dolní)
        self.screenshot_label = QLabel("📷 Náhled screenshotu")
        self.screenshot_label.setStyleSheet("border: 1px solid black; min-height: 200px;")
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.screenshot_label, 1, 0)

        # 📊 GRAF PANEL (pravý dolní)
        self.graph_widget = QWidget(self)  # ✅ Vytvoříme widget pro graf
        self.graph_layout = QVBoxLayout(self.graph_widget)  # ✅ Přidáme layout
        layout.addWidget(self.graph_widget, 1, 1)

        # 🔗 Nastavení hlavního layoutu
        self.setLayout(layout)

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

        if self.graph_visible:
            print("🔄 Aktualizujeme graf po ručním zadání částky...")
            self.update_graph()

    def take_screenshot(self):
        """Spustí screenshotovací funkci a aktualizuje graf, pokud je viditelný"""
        amounts = take_screenshot(self)  # Pořídíme screenshot a extrahujeme částky

        if amounts:
            print("📊 Přidáváme částky do databáze...")
            add_amounts_to_db(self, amounts)  # Uloží částky do databáze

            if self.graph_visible:
                print("🔄 Aktualizujeme graf po screenshotu...")
                self.update_graph()

    def toggleGraph(self):
        if self.graph_visible:
            self.graph_widget.setVisible(False)
            self.graph_button.setText("Zobrazit graf")
        else:
            self.showGraph()
            self.graph_widget.setVisible(True)
            self.graph_button.setText("Skrýt graf")
        self.graph_visible = not self.graph_visible

    def showGraph(self):
        """ Zavolá funkci `showGraph()` a správně přidá graf do GUI. """
        print("📊 Generuji graf...")

        # 🗑️ **Smažeme starý graf**
        while self.graph_layout.count():
            item = self.graph_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 📊 **Získáme nový graf jako `FigureCanvas`**
        canvas = showGraph(self.cursor)

        if canvas:  # ✅ **Pokud se graf vytvořil, nastavíme jeho velikost**
            canvas.setMinimumWidth(800)  # 📌 **Zabráníme stlačení grafu**
            canvas.setMinimumHeight(400)
            self.graph_layout.addWidget(canvas)
            print("✅ Graf přidán do GUI!")
        else:
            print("⚠️ Graf se nevytvořil, protože nejsou žádná data!")

    def clearTransactions(self):
        """ Smaže všechny transakce a resetuje zůstatek. """
        try:
            print("🗑️ Mazání všech transakcí z databáze...")
            self.cursor.execute("DELETE FROM transactions")
            self.conn.commit()

            # Resetujeme zůstatek
            self.balance = 0

            # 🔄 Aktualizujeme GUI
            self.label.setText(f"💰 Zůstatek: {self.balance} Kč (transakce vymazány)")
            self.repaint()  # ✅ Qt GUI update

            # 🟢 **Aktualizujeme graf pouze pokud byl viditelný**
            if self.graph_visible:
                self.updateGraph()

            # ✅ **Tlačítko zůstane ve správném stavu podle viditelnosti grafu**
            self.graph_button.setText("Skrýt graf" if self.graph_visible else "Zobrazit graf")

            print("✅ Všechny transakce úspěšně vymazány!")

        except Exception as e:
            print("❌ Chyba při mazání transakcí!")
            import traceback
            traceback.print_exc()
            self.label.setText(f"❌ Chyba při mazání: {str(e)}")

    def update_graph(self):
        """ Aktualizuje graf a zobrazí jej v GUI """
        print("🔄 Aktualizuji graf...")

        # ✅ Smazání starého grafu
        while self.graph_layout.count():
            item = self.graph_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        QApplication.processEvents()  # 🚀 **Přidá tento řádek, aby Qt GUI zpracovalo změny!**

        # ✅ Vytvoření nového grafu
        canvas = showGraph(self.cursor)
        if canvas:
            self.graph_layout.addWidget(canvas)
            print("✅ Graf úspěšně aktualizován!")
        else:
            print("⚠️ Žádná data k zobrazení! Nahrazujeme zprávou...")

    def updateGraph(self):
        """ Aktualizuje graf podle aktuálních transakcí. """
        print("🔄 Aktualizuji graf...")

        # Nejprve odstraníme starý graf, pokud existuje
        while self.graph_layout.count():
            item = self.graph_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Získáme nový graf jako `FigureCanvas`
        canvas = showGraph(self.cursor)

        if canvas:
            canvas.setMinimumWidth(800)  # 📏 Zabráníme stlačení grafu
            canvas.setMinimumHeight(400)
            self.graph_layout.addWidget(canvas)
            self.graph_widget.setVisible(True)  # ✅ Graf zůstane viditelný i bez dat
            print("✅ Graf přidán do GUI!")
        else:
            print("⚠️ Žádná data k zobrazení! Nahrazujeme zprávou...")

            # 📝 **Vytvoříme QLabel místo grafu**
            no_data_label = QLabel("📊 Žádná data k zobrazení", self)
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 18px; font-weight: bold; color: gray;")

            self.graph_layout.addWidget(no_data_label)
            self.graph_widget.setVisible(True)  # ✅ Necháme grafové pole viditelné


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginApp()
    login_window.show()
    app.exec_()  # Počkáme na zavření přihlašovacího okna

    if login_window.is_authenticated:
        main_window = FinanceTracker()
        main_window.show()
        sys.exit(app.exec_())
