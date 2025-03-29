from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import logging

def show_transaction_graph(cursor):
    """
    Renders a bar chart representing the sum of transactions by type.

    Args:
        cursor: Database cursor used to fetch transaction data.

    Returns:
        A FigureCanvas containing the plotted graph, or None if no data is available.
    """
    try:
        logging.info("Fetching data for transaction graph...")
        cursor.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        data = cursor.fetchall()

        if not data:
            logging.warning("No transactions found. Graph will not be displayed.")
            return None

        labels, values = zip(*data)

        # Prepare the figure
        plt.close("all")
        figure, ax = plt.subplots(figsize=(8, 6))

        # Assign colors based on transaction type
        colors = ['green' if label.lower() == "income" else 'red' for label in labels]
        bars = ax.bar(labels, values, color=colors, width=0.6)

        ax.set_title("Income vs Expenses", fontsize=16, fontweight="bold")
        ax.set_xlabel("Category", fontsize=14)
        ax.set_ylabel("Amount (CZK)", fontsize=14)

        # Add value labels above/below bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            offset = max(abs(height) * 0.02, 20)  # Dynamic offset, min 20px
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + (offset if height > 0 else -offset),
                f"{round(value)} CZK",
                ha='center',
                va='bottom' if height > 0 else 'top',
                fontsize=12,
                fontweight="bold"
            )

        plt.subplots_adjust(left=0.15, right=0.95, top=0.85, bottom=0.2)

        logging.info("Graph rendered successfully.")
        return FigureCanvas(figure)

    except Exception as e:
        logging.error("Failed to render transaction graph.")
        return None