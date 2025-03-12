# Finance_tracker:
Aplika v PyQt5 která zobrazuje příjmy a výdaje přihlášenému uživateli. Nechybí graf. Příjmy je schopen screenshotovat pomocí externí aplikace OCR (Optical Character Recognition).

POZOR: Tesseract OCR není součástí Python knihoven!:
(Musíš ho nainstalovat ručně podle své platformy)

🖥 Windows: 
Stáhni a nainstaluj: https://github.com/UB-Mannheim/tesseract/wiki
(Obvykle se instaluje do C:\Program Files\Tesseract-OCR\tesseract.exe)

🐧 Linux (Ubuntu):
sudo apt update && sudo apt install tesseract-ocr

🍏 MacOS:
brew install tesseract

Po instalaci nezapomeň nastavit cestu k tesseract.exe ve svém kódu:
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Spuštění aplikace:
- pip install -r requirements.txt
- externě nainstalovat Tesseract OCR
- python main.py


# Průběžné body tvorby aplikace:
- [x] vytvořit login
- [ ] propojit login s main.py
- [ ] přidat k logingu solení
- [ ] rozdělit main.py na vícero souborů
- [x] sepsat README.md
- [x] sepsat requirements.txt
- [ ] udělat grafický návrh, jak má aplikace vypadat
- [ ] nakódovat přidávání transakcí - json: leden, příjem/výdaj, částka, za co
- [ ] přidat editování transakcí
- [ ] vytvořit (návrh) grafu příjmů a výdajů