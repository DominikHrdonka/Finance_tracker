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
from PyQt5.QtGui import QPixmap
from PIL import ImageGrab
from PyQt5.QtGui import QImage, QPixmap
from PIL import ImageGrab, Image  # ✅ Správný import!
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt




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
        """ 📸 Screenshotování bez chyb! Používá čistý PyQt5, žádný ImageQt. """

        def screenshot_thread():
            print("🟢 Screenshotovací vlákno spuštěno...")
            self.label.setText("🖱️ Klikni a táhni myší pro výběr oblasti...")

            root = tk.Tk()
            root.attributes("-fullscreen", True)
            root.attributes("-alpha", 0.3)
            root.configure(bg="black")

            coords = []

            def on_click(event):
                print(f"🔵 Kliknutí na: {event.x_root}, {event.y_root}")
                coords.clear()
                coords.append((event.x_root, event.y_root))

            def on_release(event):
                print(f"🟠 Uvolnění na: {event.x_root}, {event.y_root}")
                coords.append((event.x_root, event.y_root))
                root.quit()

            canvas = tk.Canvas(root, cursor="cross", bg="black")
            canvas.pack(fill=tk.BOTH, expand=True)
            canvas.bind("<ButtonPress-1>", on_click)
            canvas.bind("<ButtonRelease-1>", on_release)

            root.mainloop()
            root.destroy()

            if len(coords) < 2:
                self.label.setText("❌ Screenshot byl zrušen.")
                print("🔴 Screenshot zrušen.")
                return

            x1, y1 = coords[0]
            x2, y2 = coords[1]

            if x1 == x2 or y1 == y2:
                self.label.setText("❌ Vybraná oblast je příliš malá!")
                print("🔴 Vybraná oblast je příliš malá.")
                return

            print(f"🟢 Pořizuji screenshot oblasti: ({x1}, {y1}) → ({x2}, {y2})")

            # 📸 Pořídíme screenshot v zadané oblasti
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot = screenshot.convert("RGB")  # ✅ Nutné pro PyQt5

            # 🖼️ Převedeme screenshot do formátu pro PyQt5 **bez ImageQt!**
            data = screenshot.tobytes("raw", "RGB")
            qimage = QImage(data, screenshot.width, screenshot.height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            # ✅ Aktualizujeme QLabel ve hlavní aplikaci **v hlavním Qt vlákně**
            self.screenshot_label.setPixmap(pixmap)
            self.screenshot_label.setPixmap(pixmap.scaled(self.screenshot_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.label.setText("✅ Screenshot byl pořízen!")

            print("🟢 Screenshot dokončen!")

        # 🚀 Spustíme screenshotovací funkci ve **vlastním vlákně**
        threading.Thread(target=screenshot_thread, daemon=True).start()

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
        self.cursor.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        data = self.cursor.fetchall()
        if not data:
            self.label.setText("Žádné transakce k zobrazení.")
            return

        labels = [row[0] for row in data]
        values = [row[1] for row in data]
        figure = plt.figure(figsize=(5, 3))
        ax = figure.add_subplot(111)
        ax.bar(labels, values, color=['green' if lbl == "Příjem" else 'red' for lbl in labels])
        ax.set_title("Příjmy vs Výdaje")
        ax.set_xlabel("Kategorie")
        ax.set_ylabel("Částka (Kč)")
        canvas = FigureCanvas(figure)
        self.graph_layout.addWidget(canvas)

    def clearTransactions(self):
        self.cursor.execute("DELETE FROM transactions")
        self.conn.commit()
        self.balance = 0
        self.label.setText(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        self.updateGraph()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FinanceTracker()
    sys.exit(app.exec_())
