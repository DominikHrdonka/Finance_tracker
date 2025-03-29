import subprocess
import time
import sys
import io
import numpy as np
from PIL import Image, ImageEnhance, ImageGrab, ImageOps
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

import easyocr
reader = easyocr.Reader(['cs', 'en'])

def take_screenshot(widget):
    """
    Captures a screenshot and extracts monetary values using OCR.
    Updates the GUI with results and optionally inserts data into the database.
    """
    try:
        screenshot = None

        if sys.platform == "win32":
            print("[INFO] Launching Windows Snipping Tool...")
            subprocess.run(["explorer", "ms-screenclip:"], shell=True)
            time.sleep(5)

            for _ in range(10):
                screenshot = ImageGrab.grabclipboard()
                if screenshot:
                    break
                time.sleep(0.5)

            if screenshot is None:
                widget.label.setText("Screenshot not found.")
                return

        elif sys.platform.startswith("linux"):
            screenshot_path = "/tmp/screenshot.png"
            print("[INFO] Taking screenshot on Linux...")

            if subprocess.run("command -v maim", shell=True, stdout=subprocess.PIPE).returncode == 0:
                subprocess.run(f"maim -s {screenshot_path}", shell=True)
            elif subprocess.run("command -v scrot", shell=True, stdout=subprocess.PIPE).returncode == 0:
                subprocess.run(f"scrot -s {screenshot_path}", shell=True)
            elif subprocess.run("command -v import", shell=True, stdout=subprocess.PIPE).returncode == 0:
                subprocess.run(f"import {screenshot_path}", shell=True)
            else:
                widget.label.setText("No screenshot tool available.")
                return

            time.sleep(1)
            screenshot = Image.open(screenshot_path)

        else:
            widget.label.setText("Unsupported operating system.")
            return

        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)

        qimage = QImage()
        qimage.loadFromData(buffer.getvalue(), "PNG")
        pixmap = QPixmap.fromImage(qimage)

        widget.screenshot_label.setPixmap(pixmap.scaled(
            widget.screenshot_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        widget.label.setText("Screenshot captured.")

        amounts = extract_amounts_from_image(screenshot)

        if not amounts:
            widget.label.setText("No amounts recognized.")
            return

        amounts_str = ", ".join(f"{a:.2f} CZK" for a in amounts)
        confirm_text = f"The following amounts were recognized:\n{amounts_str}\n\nDo you want to add them to the database?"

        reply = QMessageBox.question(widget, "Confirm OCR Results", confirm_text,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            add_amounts_to_db(widget, amounts)
            widget.label.setText(f"{len(amounts)} amount(s) added.")
        else:
            widget.label.setText("Operation cancelled.")

    except Exception as e:
        print("[ERROR] Failed to process screenshot.")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"Screenshot failed: {str(e)}")

def extract_amounts_from_image(image):
    """
    Preprocesses the image and uses OCR to detect numeric amounts.
    Returns a list of parsed float values.
    """
    print("[INFO] Running OCR on image...")
    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(3.0)
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
            print(f"[OK] Accepted: {text} → {parsed}")
        else:
            print(f"[SKIP] Rejected: {text}")

    print(f"[INFO] Final parsed amounts: {amounts}")
    return amounts

def parse_amount_string(raw):
    """
    Parses a string representing a monetary value and returns it as a float.
    Handles common Czech suffixes and formatting styles.
    """
    raw = raw.lower().strip()
    raw = raw.replace("−", "-").replace("–", "-").replace("—", "-")

    suffixes = [
        "kč", "czk", "kc",
        ",-", ".-", "-", ",−", ".−", "−", ",–", ".–", "–", ",—", ".—", "—",
        "kč-", "czk-", "kc-", "kč−", "czk−", "kc−",
        "kč–", "czk–", "kc–", "kč—", "czk—", "kc—",
        "kč.", "czk.", "kc."
    ]
    for suffix in suffixes:
        if raw.endswith(suffix):
            raw = raw[:-len(suffix)].strip()

    is_negative = raw.startswith("-")
    if is_negative:
        raw = raw[1:]

    clean = raw.replace(" ", "")

    value_str = None
    if "," in clean:
        parts = clean.split(",")
        if len(parts) == 2 and parts[1].isdigit():
            if len(parts[1]) == 2:
                value_str = clean.replace(",", ".")
            elif len(parts[1]) == 3:
                value_str = "".join(parts)
    elif "." in clean:
        parts = clean.split(".")
        if len(parts) == 2 and parts[1].isdigit():
            if len(parts[1]) == 2:
                value_str = clean
            elif len(parts[1]) == 3:
                value_str = "".join(parts)
        elif all(p.isdigit() for p in parts):
            value_str = "".join(parts)
    elif clean.isdigit():
        value_str = clean

    if value_str is None:
        return None

    try:
        value = round(float(value_str), 2)
        return -value if is_negative else value
    except ValueError:
        return None

def add_amounts_to_db(widget, amounts):
    """
    Inserts recognized amounts into the database and updates balance.
    """
    try:
        print("[INFO] Inserting amounts into database...")
        transaction_type = "Income" if widget.radio_income.isChecked() else "Expense"


        for amount in amounts:
            if transaction_type == "Expense":
                amount = -abs(amount)
            widget.cursor.execute(
                "INSERT INTO transactions (type, amount) VALUES (?, ?)",
                (transaction_type, amount)
            )

        widget.conn.commit()
        widget.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        widget.balance = widget.cursor.fetchone()[0]

        widget.label.setText(f"Balance: {widget.balance} CZK ({transaction_type} added)")

        if widget.graph_visible:
            widget.update_graph()

    except Exception as e:
        print("[ERROR] Database update failed.")
        import traceback
        traceback.print_exc()
        widget.label.setText(f"Database error: {str(e)}")
