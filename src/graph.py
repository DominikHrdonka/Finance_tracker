import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def show_graph(self):
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