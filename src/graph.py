from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

def showGraph(cursor):
    """ Vykreslí graf transakcí. """
    try:
        print("📊 Načítám data pro graf...")
        cursor.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        data = cursor.fetchall()

        if not data:
            print("⚠️ Žádné transakce k zobrazení. Vracíme None.")
            return None  # 💥 Ověříme, jestli problém je v datech

        labels, values = zip(*data) if data else ([], [])

        plt.close("all")
        figure, ax = plt.subplots(figsize=(8, 5))

        colors = ['green' if lbl == "Příjem" else 'red' for lbl in labels]
        ax.bar(labels, values, color=colors, width=0.6)

        ax.set_title("Příjmy vs Výdaje", fontsize=16, fontweight="bold")
        ax.set_xlabel("Kategorie", fontsize=14)
        ax.set_ylabel("Částka (Kč)", fontsize=14)

        for i, v in enumerate(values):
            ax.text(i, v + (5000 if v > 0 else -5000), f"{v} Kč", ha='center', fontsize=12, fontweight="bold")

        plt.subplots_adjust(left=0.15, right=0.95, top=0.85, bottom=0.2)

        canvas = FigureCanvas(figure)
        print("✅ Graf úspěšně vytvořen a vrácen jako FigureCanvas!")
        return canvas  # ✅ Tohle musí být vráceno do `canvas = showGraph(self.cursor)`

    except Exception as e:
        print("❌ Chyba při vykreslování grafu!")
        import traceback
        traceback.print_exc()
        return None
