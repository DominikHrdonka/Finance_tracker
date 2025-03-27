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
            return None

        labels, values = zip(*data) if data else ([], [])

        plt.close("all")
        figure, ax = plt.subplots(figsize=(8, 6))  # ZVÝŠENO na výšku

        colors = ['green' if lbl == "Příjem" else 'red' for lbl in labels]
        bars = ax.bar(labels, values, color=colors, width=0.6)

        ax.set_title("Příjmy vs Výdaje", fontsize=16, fontweight="bold")
        ax.set_xlabel("Kategorie", fontsize=14)
        ax.set_ylabel("Částka (Kč)", fontsize=14)

        # Přidání popisků na sloupce
        for bar, value in zip(bars, values):
            height = bar.get_height()
            offset = max(abs(height) * 0.02, 20)  # Dynamický posun, min 20px
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + (offset if height > 0 else -offset),
                f"{round(value)} Kč",
                ha='center',
                va='bottom' if height > 0 else 'top',
                fontsize=12,
                fontweight="bold"
            )

        plt.subplots_adjust(left=0.15, right=0.95, top=0.85, bottom=0.2)

        canvas = FigureCanvas(figure)
        print("✅ Graf úspěšně vytvořen a vrácen jako FigureCanvas!")
        return canvas

    except Exception as e:
        print("❌ Chyba při vykreslování grafu!")
        import traceback
        traceback.print_exc()
        return None
