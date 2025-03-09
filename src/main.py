import sqlite3
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QPushButton, QLineEdit, QLabel, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QFont


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.graph_visible = False  # ✅ Stav grafu
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
        self.resize(900, 700)  # ✅ Nastaví pevnou velikost okna při spuštění

        layout = QVBoxLayout()
        font = QFont("Arial", 12)

        self.radio1 = QRadioButton("Příjem")
        self.radio1.setFont(font)
        self.radio2 = QRadioButton("Výdaj")
        self.radio2.setFont(font)
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)

        self.textbox = QLineEdit(self)
        self.textbox.setFont(font)
        self.textbox.setFixedHeight(40)
        layout.addWidget(self.textbox)

        self.button = QPushButton("Enter", self)
        self.button.setFont(font)
        self.button.setFixedHeight(40)
        self.button.clicked.connect(self.onSubmit)
        layout.addWidget(self.button)

        # ✅ Tlačítko pro zobrazení/skrytí grafu
        self.graph_button = QPushButton("Zobrazit graf", self)
        self.graph_button.setFont(font)
        self.graph_button.setFixedHeight(40)
        self.graph_button.clicked.connect(self.toggleGraph)
        layout.addWidget(self.graph_button)

        # ✅ Tlačítko pro smazání všech transakcí
        self.clear_button = QPushButton("Vymazat všechny transakce", self)
        self.clear_button.setFont(font)
        self.clear_button.setFixedHeight(40)
        self.clear_button.clicked.connect(self.clearTransactions)
        layout.addWidget(self.clear_button)

        # ✅ Widget pro graf (prázdný na začátku)
        self.graph_widget = QWidget(self)
        self.graph_layout = QVBoxLayout(self.graph_widget)
        layout.addWidget(self.graph_widget)
        self.graph_widget.setVisible(False)  # ✅ Skrýt graf na začátku

        self.label = QLabel(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        self.label.setFont(font)
        layout.addWidget(self.label)

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
            amount = -amount  # ✅ Výdaje jako záporná čísla

        self.cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", (transaction_type, amount))
        self.conn.commit()

        self.balance += amount
        self.label.setText(f"Na vašem účtu je zůstatek: {self.balance} Kč")
        self.textbox.clear()

        self.updateGraph()  # ✅ Aktualizuje graf po změně

    def showGraph(self):
        self.cursor.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        data = self.cursor.fetchall()

        if not data:
            self.label.setText("Žádné transakce k zobrazení.")
            return

        labels = [row[0] for row in data]
        values = [row[1] for row in data]

        # ✅ Odstraníme starý graf
        for i in reversed(range(self.graph_layout.count())):
            self.graph_layout.itemAt(i).widget().setParent(None)

        # ✅ Nový graf
        figure = plt.figure(figsize=(5, 3))
        ax = figure.add_subplot(111)
        ax.bar(labels, values, color=['green' if lbl == "Příjem" else 'red' for lbl in labels])
        ax.set_title("Příjmy vs Výdaje")
        ax.set_xlabel("Kategorie")
        ax.set_ylabel("Částka (Kč)")

        canvas = FigureCanvas(figure)
        self.graph_layout.addWidget(canvas)

    def updateGraph(self):
        """ ✅ Aktualizuje graf po každé nové transakci """
        if self.graph_visible:  # ✅ Aktualizuj graf jen pokud je viditelný
            self.showGraph()

    def toggleGraph(self):
        """ ✅ Přepínání viditelnosti grafu """
        if self.graph_visible:
            self.graph_widget.setVisible(False)  # ✅ Skryj graf
            self.graph_button.setText("Zobrazit graf")
        else:
            self.showGraph()  # ✅ Zobraz graf
            self.graph_widget.setVisible(True)
            self.graph_button.setText("Skrýt graf")

        self.graph_visible = not self.graph_visible  # ✅ Přepni stav

    def clearTransactions(self):
        """ ✅ Smaže všechny transakce, vynuluje zůstatek a aktualizuje graf """
        self.cursor.execute("DELETE FROM transactions")  # ❌ Smaže všechny transakce
        self.conn.commit()

        self.balance = 0  # ✅ Vynuluje zůstatek
        self.label.setText(f"Na vašem účtu je zůstatek: {self.balance} Kč")

        self.updateGraph()  # ✅ Aktualizuje graf


if __name__ == "__main__":
    app = QApplication([])
    ex = MyApp()
    app.exec_()

