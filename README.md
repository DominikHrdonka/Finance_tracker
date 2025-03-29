# Finance_tracker:
Aplikace v PyQt5, která zobrazuje příjmy a výdaje přihlášenému uživateli. Částky je schopna screenshotovat pomocí easyOCR.

# Spuštění aplikace:
- pip install -r requirements.txt
- python src/main.py
- vytvoření účtu a přihlášení


# Průběžné body tvorby aplikace:
- [x] rozdělit main.py na vícero souborů
- [x] sepsat README.md
- [x] sepsat requirements.txt
- [x] vytvořit login
- [x] propojit login s main.py
- [x] přidat k loginu solení
- [x] přejít z user.json na sqlite login
- [x] přejít z sqlite na sqlalchemy login
- [ ] udělat grafický návrh, jak má aplikace vypadat
- [ ] nakódovat přidávání transakcí - json: leden, příjem/výdaj, částka, za co
- [ ] přidat editování transakcí
- [ ] vytvořit (návrh) grafu příjmů a výdajů