import subprocess
import time
import pytesseract
from PIL import ImageGrab, Image, ImageEnhance
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import io
import re

# ⚙️ Nastavení Tesseract OCR (změň cestu podle své instalace)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def take_screenshot(widget):
    """Spustí Windows Snipping Tool, načte screenshot a extrahuje částky."""
    try:
        print("🟢 Spouštíme Windows Snipping Tool...")
        subprocess.run(["explorer", "ms-screenclip:"], shell=True)

        print("⏳ Čekáme na dokončení screenshotu...")
        widget.label.setText("📸 Pořiď screenshot oblasti s částkami...")
        time.sleep(5)

        print("📋 Zkoušíme načíst obrázek ze schránky...")
        screenshot = None
        for attempt in range(10):
            screenshot = ImageGrab.grabclipboard()
            if screenshot:
                print(f"✅ Screenshot načten na pokus {attempt + 1}")
                break
            time.sleep(0.5)

        if screenshot is None:
            print("❌ Screenshot nebyl nalezen!")
            widget.label.setText("❌ Screenshot nebyl nalezen ve schránce.")
            return

        # 🖼️ Převedeme screenshot na QPixmap
        screenshot = screenshot.convert("RGB")
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

        # 📜 🏦 Spustíme OCR a extrahujeme částky
        amounts = extract_amounts_from_image(screenshot)

        if not amounts:
            widget.label.setText("❌ Nebyly rozpoznány žádné částky.")
            return

        # 💰 Přidáme částky do databáze
        add_amounts_to_db(widget, amounts)

    except Exception as e:
        print("❌ Chyba během screenshotování!")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"❌ Screenshot selhal: {str(e)}")


def add_amounts_to_db(widget, amounts):
    """Uloží rozpoznané částky do databáze jako Příjem/Výdaj."""
    try:
        print("📊 Kontrolujeme databázové spojení...")
        if widget.conn is None or widget.cursor is None:
            print("❌ Chyba: Databázové spojení je neplatné!")
            widget.label.setText("❌ Chyba: Databázové spojení neexistuje!")
            return

        print("📊 Přidáváme částky do databáze...")
        transaction_type = "Příjem" if widget.radio1.isChecked() else "Výdaj"

        for amount in amounts:
            if transaction_type == "Výdaj":
                amount = -amount  # Výdaje ukládáme záporné

            print(f"📊 Vkládáme do DB: {transaction_type}, {amount} Kč")
            widget.cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", (transaction_type, amount))

        widget.conn.commit()  # Uložíme změny do databáze
        widget.balance += sum(amounts)

        # 🔄 Aktualizujeme GUI bezpečně
        print(f"💰 Nový zůstatek: {widget.balance} Kč")
        widget.label.setText(f"💰 Zůstatek: {widget.balance} Kč (přidáno {transaction_type})")

    except Exception as e:
        print("❌ Chyba při přidávání do databáze!")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"❌ Chyba v DB: {str(e)}")



def extract_amounts_from_image(image):
    """ Použije OCR k extrakci částek ze screenshotu. """
    print("🔍 Spouštíme OCR na rozpoznání textu...")

    # 🏆 Převedeme obrázek na černobílý a zvýšíme kontrast
    image = image.convert("L")  # Černobílý režim pro lepší OCR
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Zvýšení kontrastu

    # 📜 Použijeme OCR s češtinou
    text = pytesseract.image_to_string(image, lang="ces+eng")

    print(f"📜 Rozpoznaný text:\n{text}")

    # 🏦 Extrahujeme čísla ve formátu "xx.xxx Kč" nebo "xxxx Kč"
    amounts = re.findall(r"\d{1,3}(?:[\.,]\d{3})*|\d+", text)  # Povolené tečky i čárky

    # 🔄 Oprava čísel – odstranění oddělovačů tisíců
    corrected_amounts = []
    for amount in amounts:
        clean_amount = amount.replace(".", "").replace(",", "")  # Odstranění oddělovačů
        if clean_amount.isdigit():  # Kontrola, jestli je to opravdu číslo
            corrected_amounts.append(int(clean_amount))

    print(f"💰 Opravené částky: {corrected_amounts}")
    return corrected_amounts

