# Finance_tracker:
Aplika v PyQt5 která zobrazuje příjmy a výdaje přihlášenému uživateli. Nechybí graf. Příjmy je schopen screenshotovat pomocí externí aplikace OCR (Optical Character Recognition).

# POZOR: Tesseract OCR není součástí Python knihoven! 
# Musíš ho nainstalovat ručně podle své platformy:
#
# 🖥 Windows: 
#    Stáhni a nainstaluj: https://github.com/UB-Mannheim/tesseract/wiki
#    (Obvykle se instaluje do C:\Program Files\Tesseract-OCR\tesseract.exe)
#
# 🐧 Linux (Ubuntu):
#    sudo apt update && sudo apt install tesseract-ocr
#
# 🍏 MacOS:
#    brew install tesseract
#
# Po instalaci nezapomeň nastavit cestu k tesseract.exe ve svém kódu:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Spuštění aplikace:
- pip install -r requirements.txt
- pro 
- python main.py


# Průběžné body tvorby aplikace:
- [x] vytvořit login
- [ ] propojit login s main.py
- [ ] vytvořit graf příjmů a výdajů
- [ ] rozdělit main.py na vícero souborů