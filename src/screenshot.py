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
import numpy as np
import easyocr


reader = easyocr.Reader(['cs', 'en'])

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
            widget.label.setText("No amounts recognized.")
            return

        # Připravit text pro potvrzení
        amounts_str = ", ".join(f"{a:.2f} Kč" for a in amounts)
        confirm_text = f"The following amounts were recognized:\n{amounts_str}\n\nDo you want to add them to the database?"

        # Zobrazit potvrzovací dialog
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(widget, "Confirm OCR Results", confirm_text,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            add_amounts_to_db(widget, amounts)
            widget.label.setText(f"{len(amounts)} amount(s) added.")
        else:
            widget.label.setText("Operation cancelled.")

    except Exception as e:
        print("❌ Chyba během screenshotování!")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"❌ Screenshot selhal: {str(e)}")


def extract_amounts_from_image(image):
    print("Running OCR...")

    # Úprava obrázku pro lepší čitelnost
    image = image.convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3.0)
    from PIL import ImageOps
    image = ImageOps.autocontrast(image)
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)

    image_np = np.array(image)
    results = reader.readtext(image_np)

    for box, text, confidence in results:
        print(f"[{confidence:.2f}] {text} @ {box}")

    raw_texts = [text for (_, text, conf) in results if conf > 0.0]

    amounts = []
    for text in raw_texts:
        parsed = parse_amount_string(text)
        if parsed is not None:
            amounts.append(parsed)
            print(f"✅ Přidáno: {text} → {parsed}")
        else:
            print(f"⚠️ Zamítnuto: {text}")

    return amounts


def parse_amount_string(raw):
    original = raw  # pro debug
    raw = raw.lower().strip()

    # Sjednotíme různé typy pomlček
    raw = raw.replace("−", "-").replace("–", "-").replace("—", "-")

    # Seznam možných přípon
    suffixes = [
        "kč", "czk", "kc",
        ",-", ".-", "-",  # běžná pomlčka
        ",−", ".−", "−",  # matematické minus
        ",–", ".–", "–",  # en dash
        ",—", ".—", "—",  # em dash
        "kč-", "czk-", "kc-",
        "kč−", "czk−", "kc−",
        "kč–", "czk–", "kc–",
        "kč—", "czk—", "kc—",
        "kč.", "czk.", "kc."
    ]
    for suffix in suffixes:
        if raw.endswith(suffix):
            raw = raw[: -len(suffix)].strip()

    is_negative = raw.startswith("-")
    if is_negative:
        raw = raw[1:]

    clean = raw.replace(" ", "")

    if ',' in clean:
        parts = clean.split(',')
        if len(parts) == 2 and parts[1].isdigit():
            if len(parts[1]) == 2:
                value_str = clean.replace(',', '.')
            elif len(parts[1]) == 3:
                value_str = ''.join(parts)
            else:
                return None
        else:
            return None

    elif '.' in clean:
        parts = clean.split('.')
        if len(parts) == 2 and parts[1].isdigit():
            if len(parts[1]) == 3:
                value_str = ''.join(parts)
            elif len(parts[1]) == 2:
                value_str = clean
            else:
                return None
        elif all(p.isdigit() for p in parts):
            value_str = ''.join(parts)
        else:
            return None

    elif clean.isdigit():
        value_str = clean
    else:
        return None

    try:
        value = round(float(value_str), 2)
        return -value if is_negative else value
    except ValueError:
        return None

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
