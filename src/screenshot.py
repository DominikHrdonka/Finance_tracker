import threading
import tkinter as tk
from PIL import ImageGrab
from PyQt5.QtGui import QImage, QPixmap


def take_screenshot(widget):
    """ Funkce pro výběr oblasti obrazovky a pořízení screenshotu. """

    def screenshot_thread():
        print("🟢 Screenshotovací vlákno spuštěno...")
        widget.label.setText("🖱️ Klikni a táhni myší pro výběr oblasti...")

        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-alpha", 0.3)
        root.configure(bg="black")

        coords = []

        def on_click(event):
            coords.clear()
            coords.append((event.x_root, event.y_root))

        def on_release(event):
            coords.append((event.x_root, event.y_root))
            root.quit()

        canvas = tk.Canvas(root, cursor="cross", bg="black")
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bind("<ButtonPress-1>", on_click)
        canvas.bind("<ButtonRelease-1>", on_release)

        root.mainloop()
        root.destroy()

        if len(coords) < 2:
            widget.label.setText("❌ Screenshot byl zrušen.")
            return

        x1, y1 = coords[0]
        x2, y2 = coords[1]

        if x1 == x2 or y1 == y2:
            widget.label.setText("❌ Vybraná oblast je příliš malá!")
            return

        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot = screenshot.convert("RGB")

        data = screenshot.tobytes("raw", "RGB")
        qimage = QImage(data, screenshot.width, screenshot.height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        widget.screenshot_label.setPixmap(pixmap)
        widget.screenshot_label.setPixmap(pixmap.scaled(widget.screenshot_label.size(), 
                                                         QPixmap.KeepAspectRatio, 
                                                         QPixmap.SmoothTransformation))
        widget.label.setText("✅ Screenshot byl pořízen!")

    threading.Thread(target=screenshot_thread, daemon=True).start()