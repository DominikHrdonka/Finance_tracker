import subprocess
import time
import pytesseract
import sys
from PIL import Image, ImageEnhance, ImageGrab
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import io
import os
import re

# ✅ Nastavení cesty k Tesseract OCR podle OS
if sys.platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif sys.platform.startswith("linux"):
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Standardní cesta pro Linux

print(f"🟢 Tesseract OCR používá: {pytesseract.pytesseract.tesseract_cmd}")


def take_screenshot(widget):
    """Pořídí screenshot podle OS a extrahuje částky."""
    try:
        screenshot = None

        if sys.platform == "win32":
            print("🟢 Spouštíme Windows Snipping Tool...")
            subprocess.run(["explorer", "ms-screenclip:"], shell=True)
            time.sleep(5)

            for attempt in range(10):
                screenshot = ImageGrab.grabclipboard()
                if screenshot:
                    break
                time.sleep(0.5)

            if screenshot is None:
                widget.label.setText("❌ Screenshot nebyl nalezen.")
                return

        elif sys.platform.startswith("linux"):
            screenshot_path = "/tmp/screenshot.png"
            print("📸 Pořizujeme screenshot v Linuxu...")

            if subprocess.run("command -v maim", shell=True, stdout=subprocess.PIPE).returncode == 0:
                subprocess.run(f"maim -s {screenshot_path}", shell=True)
            elif subprocess.run("command -v scrot", shell=True, stdout=subprocess.PIPE).returncode == 0:
                subprocess.run(f"scrot -s {screenshot_path}", shell=True)
            elif subprocess.run("command -v import", shell=True, stdout=subprocess.PIPE).returncode == 0:
                subprocess.run(f"import {screenshot_path}", shell=True)
            else:
                widget.label.setText("❌ Žádný nástroj na screenshot není dostupný!")
                return

            time.sleep(1)
            screenshot = Image.open(screenshot_path)

        else:
            widget.label.setText("❌ Nepodporovaný OS.")
            return

        # 🖼️ Převedeme screenshot na QPixmap
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)

        qimage = QImage()
        qimage.loadFromData(buffer.getvalue(), "PNG")
        pixmap = QPixmap.fromImage(qimage)

        widget.screenshot_label.setPixmap(pixmap)
        widget.screenshot_label.setPixmap(pixmap.scaled(
            widget.screenshot_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        widget.label.setText("✅ Screenshot byl pořízen!")

        # 📜 Spustíme OCR a extrahujeme částky
        amounts = extract_amounts_from_image(screenshot)

        if not amounts:
            widget.label.setText("❌ Nebyly rozpoznány žádné částky.")
            return

        add_amounts_to_db(widget, amounts)

    except Exception as e:
        print("❌ Chyba během screenshotování!")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"❌ Screenshot selhal: {str(e)}")


def extract_amounts_from_image(image):
    """ Použije OCR k extrakci částek ze screenshotu. """
    print("🔍 Spouštíme OCR na rozpoznání textu...")

    # Zvýšíme kontrast obrázku pro lepší OCR
    image = image.convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Rozpoznání textu (čeština + angličtina)
    text = pytesseract.image_to_string(image, lang="ces+eng")
    print(f"📜 Rozpoznaný text:\n{text}")

    # Extrakce čísel (včetně oddělovačů tisíců)
    amounts = re.findall(r"\d{1,3}(?:[\.,]\d{3})*|\d+", text)

    corrected_amounts = []
    for amount in amounts:
        clean_amount = amount.replace(".", "").replace(",", "")
        if clean_amount.isdigit():
            corrected_amounts.append(int(clean_amount))

    print(f"💰 Opravené částky: {corrected_amounts}")
    return corrected_amounts


def add_amounts_to_db(widget, amounts):
    """Uloží rozpoznané částky do databáze jako Příjem/Výdaj a aktualizuje graf."""
    try:
        print("📊 Přidáváme částky do databáze...")
        transaction_type = "Příjem" if widget.radio1.isChecked() else "Výdaj"

        for amount in amounts:
            if transaction_type == "Výdaj":
                amount = -abs(amount)

            widget.cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", (transaction_type, amount))

        widget.conn.commit()
        widget.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        widget.balance = widget.cursor.fetchone()[0]

        widget.label.setText(f"💰 Zůstatek: {widget.balance} Kč (přidáno {transaction_type})")

        if widget.graph_visible:
            widget.update_graph()

    except Exception as e:
        print("❌ Chyba při přidávání do databáze!")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"❌ Chyba v DB: {str(e)}")
